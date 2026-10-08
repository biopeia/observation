# tests/docs/test_glossary_registry.py
"""Integrity tests for the canonical conceptual glossary."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = ROOT / "symbiont/docs/reference/glossary.yaml"
COVERAGE = ROOT / "symbiont/docs/coverage.yaml"


def _load() -> tuple[dict[str, dict], dict[str, dict]]:
    with GLOSSARY.open("r", encoding="utf-8") as handle:
        glossary = yaml.safe_load(handle)
    with COVERAGE.open("r", encoding="utf-8") as handle:
        coverage = yaml.safe_load(handle)["units"]
    return glossary, coverage


def test_glossary_schema_and_term_shape() -> None:
    glossary, _ = _load()
    assert glossary["schema_version"] == 1
    terms = glossary["terms"]
    assert terms

    required = {"term", "definition", "distinguishes_from", "owners", "canonical_refs"}
    for term_id, entry in terms.items():
        assert required.issubset(entry), f"{term_id}: missing required fields"
        assert entry["term"].strip()
        assert entry["definition"].strip()
        assert len(entry["definition"].strip()) >= 40
        assert isinstance(entry["distinguishes_from"], list)
        assert isinstance(entry["owners"], list)
        assert isinstance(entry["canonical_refs"], list)
        assert entry["canonical_refs"], f"{term_id}: at least one canonical ref required"


def test_glossary_cross_references_and_owners_resolve() -> None:
    glossary, coverage = _load()
    terms = glossary["terms"]
    known_terms = set(terms)

    errors: list[str] = []
    for term_id, entry in terms.items():
        distinctions = entry["distinguishes_from"]
        if term_id in distinctions:
            errors.append(f"{term_id}: distinguishes_from contains itself")
        if len(distinctions) != len(set(distinctions)):
            errors.append(f"{term_id}: duplicate distinguishes_from entries")
        for other in distinctions:
            if other not in known_terms:
                errors.append(f"{term_id}: unknown glossary term {other}")

        for owner in entry["owners"]:
            if owner not in coverage:
                errors.append(f"{term_id}: owner {owner} missing from coverage.yaml")

        for ref in entry["canonical_refs"]:
            path = ROOT / ref
            if not path.is_file():
                errors.append(f"{term_id}: missing canonical ref {ref}")

    assert not errors, "\n".join(errors)


def test_glossary_core_distinctions_are_bidirectional() -> None:
    """Core paired distinctions should not silently collapse in one direction."""
    glossary, _ = _load()
    terms = glossary["terms"]

    core_pairs = {
        ("fact", "evidence"),
        ("fact", "hypothesis"),
        ("fact", "prediction"),
        ("competence", "capability"),
        ("competence", "competence-execution-binding"),
        ("homeostasis", "external-reward"),
        ("embodiment", "body"),
        ("evidence", "provenance"),
    }

    errors: list[str] = []
    for left, right in core_pairs:
        if right not in terms[left]["distinguishes_from"]:
            errors.append(f"{left} does not distinguish from {right}")
        if left not in terms[right]["distinguishes_from"]:
            errors.append(f"{right} does not distinguish from {left}")

    assert not errors, "\n".join(errors)


def test_body_and_external_reward_do_not_claim_component_ownership() -> None:
    """Contrast terms outside organism component authority stay explicitly unowned."""
    glossary, _ = _load()
    terms = glossary["terms"]
    assert terms["body"]["owners"] == []
    assert terms["external-reward"]["owners"] == []
