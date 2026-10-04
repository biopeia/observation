"""Cognitive Cycle v1 W1: matched comparison of ``shared_fact_identity`` off/on.

Exploratory protocol:
``lab/experiments/learning/cognitive-cycle-shared-fact-identity/README.md``.

Three arms continue fresh copies of one developed Physics3D state for a fixed
horizon: ``off`` (default), ``off_replicate`` (noise floor) and ``on``. The
arms differ only in the flag, applied by this Lab study at construction time.
Everything measured is read from the checkpoint the engine exposes each tick;
nothing is fed back to the organism.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from lab.physics3d.engine import run
from lab.physics3d.equivalence import (
    EquivalenceRunConfig,
    _configure_equivalence_determinism,
    _digest,
)
from symbiont.modeling import ExperienceRecord, PrivateModelOrganismRuntime, build_training_corpus

ARMS = {"off": False, "off_replicate": False, "on": True}
# The flag is itself checkpointed, so the whole-checkpoint digest differs from
# the input tick on.  Divergence is therefore read per section (amendment 1).
SECTIONS = (
    "actuation",
    "cognitive_bridge",
    "executive_intention",
    "experience_ledger",
    "generative_cognition",
    "living_body",
    "metabolism",
    "private_model_registry",
)


@contextmanager
def _flag(enabled: bool) -> Iterator[None]:
    """Construct every private runtime of this arm with the flag set."""
    original = PrivateModelOrganismRuntime.__init__

    def construct(self, **options: Any) -> None:
        options["shared_fact_identity"] = enabled
        original(self, **options)

    PrivateModelOrganismRuntime.__init__ = construct  # type: ignore[method-assign]
    try:
        yield
    finally:
        PrivateModelOrganismRuntime.__init__ = original  # type: ignore[method-assign]


def _find(payload: object, key: str) -> Any:
    if isinstance(payload, Mapping):
        if key in payload:
            return payload[key]
        for value in payload.values():
            found = _find(value, key)
            if found is not None:
                return found
    return None


def _source_counts(generative: Mapping[str, Any]) -> list[int]:
    representations = _find(generative.get("generative_use", {}), "representations") or []
    return sorted((len(item.get("source_refs", ())) for item in representations), reverse=True)


def _metrics(payload: object, *, input_tick: int) -> dict[str, Any]:
    ledger = _find(payload, "experience_ledger") or {}
    records = [
        raw
        for raw in ledger.get("records", [])
        if raw["epistemic_status"] == "observed" and int(raw["tick_class"]) >= input_tick
    ]
    motor = [raw for raw in records if raw["source_kind"] == "action_outcome"]
    cited = [
        raw for raw in motor if any(str(ref).startswith("causal.") for ref in raw["evidence_refs"])
    ]
    corpus: dict[str, Any] | None
    try:
        built = build_training_corpus(
            ExperienceRecord.restore(raw) for raw in ledger.get("records", [])
        )
        corpus = {
            "train": len(built.train),
            "validation": len(built.validation),
            "test": len(built.test),
            "corpus_hash": built.manifest.corpus_hash,
        }
    except ValueError:
        corpus = None
    registry = _find(payload, "private_model_registry") or {}
    models = registry.get("records", [])
    generative = _find(payload, "generative_cognition") or {}
    sources = _source_counts(generative)
    return {
        "ledger": {
            "observed_since_input": len(records),
            "motor_caused": len(motor),
            "motor_caused_citing_causal": len(cited),
        },
        "corpus": corpus,
        "models": {
            "records": len(models),
            "states": sorted(str(item.get("state")) for item in models),
        },
        "generative": {
            "tracked_representations": len(sources),
            "factual_sources_sum": sum(sources),
            "factual_sources_max": sources[0] if sources else 0,
            "factual_sources": sources,
            "reconciliation_count": generative.get("reconciliation_count"),
            "contradicted_hypothesis_count": generative.get("contradicted_hypothesis_count"),
            "hypotheses": len(generative.get("hypotheses", [])),
        },
    }


def _arm(
    snapshot: Path, work: Path, *, arm: str, ticks: int, seed: int, body_kind: str
) -> dict[str, Any]:
    target = work / arm
    target.mkdir(parents=True)
    shutil.copy2(snapshot / "organism.symbiont", target / "organism.symbiont")
    shutil.copy2(snapshot / "body.json", target / "body.json")
    if (snapshot / "models").is_dir():
        shutil.copytree(snapshot / "models", target / "models")
    digests: list[tuple[int, dict[str, str]]] = []
    sections: dict[str, str] = {}
    last: dict[str, object] = {}

    def observe(tick: int, payload: object) -> None:
        last["payload"] = payload
        last["first_tick"] = last.get("first_tick", tick)
        digests.append(
            (
                int(tick),
                {
                    name: _digest(payload.get(name)) if isinstance(payload, Mapping) else ""
                    for name in SECTIONS
                },
            )
        )

    with _flag(ARMS[arm]):
        exit_code = run(
            headless=True,
            ticks=ticks,
            seed=seed,
            symbiont_file=target / "organism.symbiont",
            body_file=target / "body.json",
            telemetry_file=target / "telemetry",
            body_kind=body_kind,
            show_monitor=False,
            enable_slm=True,
            slm_train_interval=32,
            slm_device="cpu",
            slm_synchronous=True,
            checkpoint_interval=10**9,
            factorized_effects=True,
            observation_hz=1,
            checkpoint_observer=observe,
        )
    payload = last.get("payload", {})
    if isinstance(payload, Mapping):
        sections = {str(key): _digest(value) for key, value in payload.items()}
    return {
        "exit_code": exit_code,
        "ticks_observed": len(digests),
        "digests": digests,
        "sections": sections,
        "metrics": _metrics(payload, input_tick=int(last.get("first_tick", 0))),  # type: ignore[call-overload]
    }


def _first_divergence(a: dict[str, Any], b: dict[str, Any]) -> dict[str, int | None]:
    """First tick at which each section differs between two arms (None: never)."""
    first: dict[str, int | None] = dict.fromkeys(SECTIONS)
    for (tick, left), (_, right) in zip(a["digests"], b["digests"]):
        for name in SECTIONS:
            if first[name] is None and left[name] != right[name]:
                first[name] = tick
    return first


def _differing_sections(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    keys = sorted(set(a["sections"]) | set(b["sections"]))
    return [key for key in keys if a["sections"].get(key) != b["sections"].get(key)]


def run_shared_fact_identity_study(
    snapshot: Path, work: Path, *, ticks: int, seed: int, body_kind: str
) -> dict[str, Any]:
    determinism = _configure_equivalence_determinism(
        EquivalenceRunConfig(ticks=ticks, body_kind=body_kind, seed=seed, training=True)
    )
    arms = {
        arm: _arm(snapshot, work, arm=arm, ticks=ticks, seed=seed, body_kind=body_kind)
        for arm in ARMS
    }
    result = {
        "protocol": "learning.cognitive-cycle-shared-fact-identity",
        "regime": "exploratory",
        "seed": seed,
        "ticks": ticks,
        "input_tick": arms["off"]["digests"][0][0] if arms["off"]["digests"] else None,
        "body_kind": body_kind,
        "determinism": determinism,
        "noise_floor": {
            "first_divergence_tick_by_section": _first_divergence(
                arms["off"], arms["off_replicate"]
            ),
            "differing_sections": _differing_sections(arms["off"], arms["off_replicate"]),
        },
        "intervention": {
            "first_divergence_tick_by_section": _first_divergence(arms["off"], arms["on"]),
            "differing_sections": _differing_sections(arms["off"], arms["on"]),
        },
        "arms": {
            arm: {key: value for key, value in data.items() if key not in {"digests", "sections"}}
            for arm, data in arms.items()
        },
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("work", type=Path)
    parser.add_argument("--ticks", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--body-kind", default="anthropomorphic-v6-vision")
    args = parser.parse_args(argv)
    result = run_shared_fact_identity_study(
        args.snapshot, args.work, ticks=args.ticks, seed=args.seed, body_kind=args.body_kind
    )
    (args.work / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps({k: result[k] for k in ("noise_floor", "intervention")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
