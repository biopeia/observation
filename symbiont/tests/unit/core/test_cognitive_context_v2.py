from __future__ import annotations

from dataclasses import dataclass

import pytest

from symbiont.core.cognition.context import project_cognitive_context


@dataclass(frozen=True)
class _State:
    active_concept_ids: tuple[str, ...]
    activations: dict[str, float]
    topology_revision: int = 0


def test_context_is_bounded_ranked_and_versioned() -> None:
    state = _State(
        active_concept_ids=tuple(f"concept.{index:02d}" for index in range(12)),
        activations={f"concept.{index:02d}": index / 11.0 for index in range(12)},
        topology_revision=7,
    )

    context = project_cognitive_context(state)

    assert context.context_ref.startswith("context.v2.")
    assert len(context.concept_refs) == 8
    assert context.concept_refs[0] == "concept.11"
    assert "concept.01" not in context.concept_refs
    assert context.topology_revision == 7


def test_context_identity_ignores_input_order_and_topology_revision() -> None:
    left = _State(
        active_concept_ids=("concept.b", "concept.a"),
        activations={"concept.a": 0.75, "concept.b": 0.5},
        topology_revision=1,
    )
    right = _State(
        active_concept_ids=("concept.a", "concept.b"),
        activations={"concept.b": 0.5, "concept.a": 0.75},
        topology_revision=99,
    )

    assert project_cognitive_context(left).context_ref == project_cognitive_context(right).context_ref


def test_context_identity_changes_when_relevant_activation_class_changes() -> None:
    low = _State(("concept.a",), {"concept.a": 0.26})
    high = _State(("concept.a",), {"concept.a": 0.76})

    assert project_cognitive_context(low).context_ref != project_cognitive_context(high).context_ref


def test_context_contains_no_surface_or_embodiment_dimension() -> None:
    context = project_cognitive_context(_State(("concept.a",), {"concept.a": 0.5}))

    assert "surface" not in context.context_ref
    assert "embodiment" not in context.context_ref


def test_context_rejects_unbounded_configuration() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        project_cognitive_context(_State((), {}), max_concepts=9)
