from __future__ import annotations

import json
from importlib import resources

import pytest

from symbiont.actuation.surface import derive_actuator_constitution
from symbiont.core.embodiment.physiology import LivingBodyState
from symbiont.core.orchestration.resident import ResidentOrganism
from symbiont.core.orchestration.runtime import OrganismRuntime
from symbiont.genetics.genome import GenomeCodec
from symbiont.genetics.germline import EpigeneticProtocol, GermlineState


def _genome():
    payload = json.loads(
        resources.files("symbiont.genetics")
        .joinpath("defaults/base-genome-v2.json")
        .read_text(encoding="utf-8")
    )
    payload["genome_id"] = "genome_tick-capture-budding"
    return GenomeCodec().load(payload)


def test_real_ticks_capture_germline_mark_transmitted_through_resident_budding(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    genome = _genome()
    protocol = EpigeneticProtocol(
        enabled=True,
        acquired_capture_enabled=True,
        decay=0.0,
    )
    parent = OrganismRuntime(
        genome=genome,
        germline_state=GermlineState.from_genome(
            genome,
            acquired_capture_enabled=True,
        ),
        epigenetic_protocol=protocol,
        organism_id="tick-capture-parent",
        living_body_state=LivingBodyState(energy_reserve=100.0, max_energy=100.0),
        actuation_enabled=True,
        actuator_constitution=derive_actuator_constitution(
            8,
            physical_contract="germline-capture-budding-test",
        ),
        bootstrap_semantic_senses=False,
        discover_senses=False,
        min_samples=1,
    )

    # Each actual organism tick updates expression from the runtime's own
    # controllability evidence and feeds that expression to germline capture.
    for _ in range(64):
        parent.tick()

    locus = "sensorimotor.spontaneous_activity_baseline"
    assert parent.germline_state is not None
    acquired = parent.germline_state.acquired_marks[locus]
    assert acquired.delta > 0.02

    # Prove the acquired mark is organism checkpoint state before budding.
    restored_parent = OrganismRuntime.from_checkpoint(parent.checkpoint())
    assert restored_parent.germline_state is not None
    assert restored_parent.germline_state.acquired_marks[locus] == acquired

    class Habitat:
        deposited: dict[str, object] | None = None

        def publish_capsule(self, _capsule: object) -> None:
            pass

        def count_incubated(self) -> int:
            return 0

        def deposit_embryo(self, payload: dict[str, object], child_id: str) -> str:
            self.deposited = {"payload": payload, "child_id": child_id}
            return child_id

    habitat = Habitat()
    children: list[OrganismRuntime] = []

    def create_child(**kwargs: object) -> OrganismRuntime:
        child = OrganismRuntime(**kwargs)  # type: ignore[arg-type]
        children.append(child)
        return child

    monkeypatch.setattr("symbiont.core.orchestration.resident.create_capsule", lambda *_: {})
    resident = ResidentOrganism(
        restored_parent,
        state_file=tmp_path / "parent.json",
        habitat=habitat,  # type: ignore[arg-type]
        keypair=object(),  # type: ignore[arg-type]
        create_child=create_child,
    )
    resident._social_and_reproductive_step(20)

    assert len(children) == 1
    child = children[0]
    assert child.generation == restored_parent.generation + 1
    assert child.parent_ids == (restored_parent.organism_id,)
    assert child.germline_state is not None
    inherited = child.germline_state.inherited_marks[locus]
    assert inherited.delta == acquired.delta
    assert inherited.generations_left == acquired.generations_left - 1
    assert child.gene_expression_state is not None
    assert child.gene_expression_state.exploration_drive == pytest.approx(
        genome.sensorimotor.spontaneous_activity_baseline + inherited.delta * inherited.strength
    )
    assert habitat.deposited is not None
    assert habitat.deposited["child_id"] == child.organism_id
