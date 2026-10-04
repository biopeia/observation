from __future__ import annotations

import json
from importlib import resources

import pytest

from symbiont.core.orchestration.runtime import OrganismRuntime
from symbiont.genetics.genome import Genome, GenomeCodec
from symbiont.genetics.germline import (
    EpigeneticMark,
    EpigeneticProtocol,
    GermlineState,
    InheritancePackage,
)


def _genome(genome_id: str) -> Genome:
    payload = json.loads(
        resources.files("symbiont.genetics")
        .joinpath("defaults/base-genome-v2.json")
        .read_text(encoding="utf-8")
    )
    payload["genome_id"] = f"genome_{genome_id}"
    return GenomeCodec().load(payload)


def test_genome_v2_germline_round_trips_as_organism_state() -> None:
    genome = _genome("resident-germline-roundtrip")
    mark = EpigeneticMark(
        locus="plasticity.learning_rate.baseline",
        delta=0.02,
        strength=0.5,
        generations_left=3,
    )
    germline = GermlineState.from_genome(genome, inherited_marks=(mark,))
    runtime = OrganismRuntime(
        genome=genome,
        germline_state=germline,
        organism_id="resident-germline-roundtrip",
        parent_ids=("parent-a",),
    )

    payload = runtime.checkpoint()
    restored = OrganismRuntime.from_checkpoint(payload)

    assert restored.germline_state is not None
    assert restored.germline_state.inherited_marks == germline.inherited_marks
    assert restored.parent_ids == ("parent-a",)
    assert restored.gene_expression_state is not None
    assert restored.gene_expression_state.effective_learning_rate == pytest.approx(
        genome.plasticity.learning_rate.baseline + 0.01
    )
    assert restored.state_hash() == runtime.state_hash()


def test_explicit_inheritance_package_changes_child_birth_expression() -> None:
    genome = _genome("resident-offspring-expression")
    protocol = EpigeneticProtocol(enabled=True, decay=0.0)
    parent = OrganismRuntime(
        genome=genome,
        organism_id="parent",
        generation=2,
        epigenetic_protocol=protocol,
    )
    assert parent.germline_state is not None
    acquired = EpigeneticMark(
        locus="plasticity.learning_rate.baseline",
        delta=0.02,
        strength=0.5,
        generations_left=3,
    )
    parent.germline_state.acquired_marks[acquired.locus] = acquired

    package = parent.inheritance_package()
    child = OrganismRuntime(
        organism_id="child",
        inheritance_package=package,
        epigenetic_protocol=protocol,
    )

    assert package.parent_ids == ("parent",)
    assert package.generation == 3
    assert child.generation == 3
    assert child.parent_ids == ("parent",)
    assert child.germline_state is not None
    assert child.germline_state.inherited_marks == {
        acquired.locus: EpigeneticMark(
            locus=acquired.locus,
            delta=acquired.delta,
            strength=acquired.strength,
            generations_left=acquired.generations_left - 1,
        )
    }
    assert child.gene_expression_state is not None
    assert child.gene_expression_state.effective_learning_rate == pytest.approx(
        genome.plasticity.learning_rate.baseline + 0.01
    )


def test_epigenetic_marks_are_not_transmitted_without_enabled_protocol() -> None:
    genome = _genome("resident-disabled-transmission")
    runtime = OrganismRuntime(genome=genome, organism_id="disabled-parent")
    assert runtime.germline_state is not None
    runtime.germline_state.acquired_marks["plasticity.learning_rate.baseline"] = EpigeneticMark(
        locus="plasticity.learning_rate.baseline",
        delta=0.02,
        strength=0.5,
        generations_left=3,
    )

    package = runtime.inheritance_package()

    assert package.epigenetic_marks == ()


@pytest.mark.parametrize("generation", [True, 1.0, "1"])
def test_inheritance_package_rejects_non_integer_generation(generation: object) -> None:
    with pytest.raises(ValueError, match="generation must be an integer"):
        InheritancePackage(
            genome=_genome("invalid-inheritance-generation"),
            epigenetic_marks=(),
            parent_ids=("parent",),
            generation=generation,  # type: ignore[arg-type]
        )
