"""Tests for P8.0 Legacy Master Forensic Audit tooling."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from audit_legacy_master import (  # noqa: E402
    LEGACY_DOCX_PATH,
    AuditFragment,
    classify_section,
    extract_legacy_docx_structure,
    run_audit,
)


def test_audit_fragment_schema() -> None:
    frag = AuditFragment(
        legacy_text_id="test.001",
        legacy_location={"heading": "Test Heading", "section": "1.1"},
        classification="C",
        current_authority=None,
        coverage_units=["component.core"],
        master_ids=["SYM-001"],
        still_valid="yes",
        promotion_target="symbiont/docs/candidate.md",
        reason="Candidate for P8.1 promotion",
        action="promote",
        excerpt="Important candidate text",
    )
    assert frag.classification in {"A", "B", "C", "D", "E"}
    assert frag.action == "promote"


def test_classify_section_rules() -> None:
    # Quick Start 5 rules -> Category C (candidate for promotion)
    frag_c = classify_section(
        book="PREAMBLE",
        chapter="QUICK START",
        section="CINCO REGLAS ANTES DE LEER",
        text="Sample rule text",
        index=1,
    )
    assert frag_c.classification == "C"
    assert frag_c.action == "promote"

    # Chapter 04 component map -> Category B (derived)
    frag_b = classify_section(
        book="BOOK I",
        chapter="CHAPTER 04: ARCHITECTURE",
        section="Component Map and Domains",
        text="Component specs",
        index=2,
    )
    assert frag_b.classification == "B"
    assert frag_b.action == "derive"


def test_extract_legacy_docx_structure_synthetic(tmp_path: Path) -> None:
    sample_docx = tmp_path / "sample.docx"
    xml_content = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body>
        <w:p>
          <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
          <w:r><w:t>BOOK I: OVERVIEW</w:t></w:r>
        </w:p>
        <w:p>
          <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
          <w:r><w:t>CHAPTER 01: INTRO</w:t></w:r>
        </w:p>
        <w:p>
          <w:pPr><w:pStyle w:val="Heading3"/></w:pPr>
          <w:r><w:t>1.1 Background</w:t></w:r>
        </w:p>
        <w:p>
          <w:r><w:t>Body text paragraph one.</w:t></w:r>
        </w:p>
      </w:body>
    </w:document>"""

    with zipfile.ZipFile(sample_docx, "w") as zf:
        zf.writestr("word/document.xml", xml_content)

    sections = extract_legacy_docx_structure(sample_docx)
    assert len(sections) == 1
    assert "BOOK I" in sections[0]["book"]
    assert "CHAPTER 01" in sections[0]["chapter"]
    assert "1.1 Background" in sections[0]["section"]
    assert "Body text paragraph one" in sections[0]["text"]


def test_run_audit_execution(tmp_path: Path) -> None:
    if not LEGACY_DOCX_PATH.is_file():
        pytest.skip("Legacy master document not available in environment")

    summary = run_audit(output_dir=tmp_path)
    assert summary["total_fragments"] > 0
    assert (tmp_path / "master-legacy-audit-matrix.yaml").is_file()
    assert (tmp_path / "AUDIT_REPORT.md").is_file()
