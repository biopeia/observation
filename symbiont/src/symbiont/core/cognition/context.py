"""Bounded factual cognitive-context projection for causal learning.

The context is an organism-owned, ephemeral projection of the current
cognitive state.  It is deliberately independent of embodiment/surface
identity: execution authority belongs to bindings, while causal context
answers only "what internal situation was active?".

Context identity is versioned because changing the projection changes the
meaning of context-conditioned causal evidence.  No migration is attempted
between versions; historical evidence keeps the identity it was learned
under.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Mapping, Protocol

_CONTEXT_VERSION = 2
_DEFAULT_MAX_CONCEPTS = 8
_DEFAULT_ACTIVATION_BINS = 8


class CognitiveStateView(Protocol):
    """Minimum read-only surface required to derive a cognitive context."""

    active_concept_ids: tuple[str, ...]
    activations: Mapping[str, float]
    topology_revision: int


@dataclass(frozen=True, slots=True)
class CognitiveContext:
    """One bounded factual projection of the organism's cognitive state.

    ``activation_levels`` contains ``(concept_id, level)`` pairs ordered by
    descending activation and then by id.  ``topology_revision`` is retained
    for provenance/diagnostics but is intentionally excluded from identity so
    unrelated structural edits do not create artificial context churn.
    """

    context_ref: str
    concept_refs: tuple[str, ...]
    activation_levels: tuple[tuple[str, int], ...]
    topology_revision: int

    def __post_init__(self) -> None:
        if not self.context_ref.startswith("context.v2."):
            raise ValueError("cognitive context must use the context.v2 namespace")
        if len(self.concept_refs) > _DEFAULT_MAX_CONCEPTS:
            raise ValueError("cognitive context exceeds the bounded concept count")
        if tuple(concept_id for concept_id, _level in self.activation_levels) != self.concept_refs:
            raise ValueError("context concept refs and activation levels disagree")
        if self.topology_revision < 0:
            raise ValueError("topology_revision must be non-negative")


def _activation_level(value: float, *, bins: int) -> int:
    """Quantize a finite activation in [0,1] into a stable positive class."""

    bounded = max(0.0, min(1.0, float(value)))
    # Active concepts should never collapse to class 0 merely because they
    # sit just above the graph's activation threshold.
    return max(1, min(bins, int(math.ceil(bounded * bins))))


def project_cognitive_context(
    state: CognitiveStateView | None,
    *,
    max_concepts: int = _DEFAULT_MAX_CONCEPTS,
    activation_bins: int = _DEFAULT_ACTIVATION_BINS,
) -> CognitiveContext:
    """Project a bounded, deterministic context from current cognition.

    Selection is based only on organism-owned concept activation.  No body id,
    actuator surface, world coordinate, lab label or external semantic enters
    the identity.  The strongest concepts win; ties are deterministic.
    """

    if isinstance(max_concepts, bool) or not isinstance(max_concepts, int) or max_concepts < 1:
        raise ValueError("max_concepts must be a positive integer")
    if max_concepts > _DEFAULT_MAX_CONCEPTS:
        raise ValueError(f"max_concepts must not exceed {_DEFAULT_MAX_CONCEPTS}")
    if (
        isinstance(activation_bins, bool)
        or not isinstance(activation_bins, int)
        or activation_bins < 2
        or activation_bins > 32
    ):
        raise ValueError("activation_bins must be an integer in [2, 32]")

    topology_revision = int(getattr(state, "topology_revision", 0) or 0) if state else 0
    active_ids = tuple(getattr(state, "active_concept_ids", ()) or ()) if state else ()
    activations = getattr(state, "activations", {}) or {} if state else {}

    ranked: list[tuple[float, str]] = []
    seen: set[str] = set()
    for raw_id in active_ids:
        concept_id = str(raw_id)
        if not concept_id or concept_id in seen:
            continue
        seen.add(concept_id)
        raw_value = activations.get(concept_id)
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            continue
        value = float(raw_value)
        if not math.isfinite(value) or value <= 0.0:
            continue
        ranked.append((value, concept_id))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected = ranked[:max_concepts]
    levels = tuple(
        (concept_id, _activation_level(value, bins=activation_bins))
        for value, concept_id in selected
    )

    material = "|".join(f"{concept_id}:{level}" for concept_id, level in levels) or "opaque"
    digest = hashlib.sha256(f"v{_CONTEXT_VERSION}|{material}".encode("utf-8")).hexdigest()[:24]
    return CognitiveContext(
        context_ref=f"context.v{_CONTEXT_VERSION}.{digest}",
        concept_refs=tuple(concept_id for concept_id, _level in levels),
        activation_levels=levels,
        topology_revision=max(0, topology_revision),
    )


__all__ = ["CognitiveContext", "CognitiveStateView", "project_cognitive_context"]
