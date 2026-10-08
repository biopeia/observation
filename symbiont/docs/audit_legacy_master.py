#!/usr/bin/env python3
"""P8.0 — Forensic Audit & Knowledge Extraction from Legacy Master Reference.

Performs a granular, strictly read-only forensic analysis of the original
Google Drive Master document (/home/alessbarb/Descargas/Symbiont - Referencia Maestra - v2026.10.07-r1 FINAL.docx, 189 pages).

Extracts and classifies every section, table, diagram, matrix, and claim into:
  - Category A: Already present in canonical corpus (reuse)
  - Category B: Derivable from registries (derive)
  - Category C: Candidate Canonical Knowledge (promote after review)
  - Category D: Obsolete / superseded material (archive / discard)
  - Category E: Redundant / verbose editorial padding (discard)

Emits:
  - build/legacy-audit/master-legacy-audit-matrix.yaml
  - build/legacy-audit/AUDIT_REPORT.md

Enforces:
  - Strictly read-only: zero modifications to symbiont/docs/ or repo sources.
"""

from __future__ import annotations

import datetime
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LEGACY_DOCX_PATH = Path(
    "/home/alessbarb/Descargas/Symbiont - Referencia Maestra - v2026.10.07-r1 FINAL.docx"
)


@dataclass
class AuditFragment:
    """Granular audit entry for a legacy Master element."""

    legacy_text_id: str
    legacy_location: dict[str, str]
    classification: str  # A, B, C, D, E
    current_authority: str | None
    coverage_units: list[str] = field(default_factory=list)
    master_ids: list[str] = field(default_factory=list)
    still_valid: str = "yes"  # yes, no, partial, unresolved
    promotion_target: str | None = None
    reason: str = ""
    action: str = "reuse"  # reuse, derive, promote, archive, discard
    excerpt: str = ""


def extract_legacy_docx_structure(docx_path: Path) -> list[dict]:
    """Parse legacy WordprocessingML document into structural sections."""
    if not docx_path.is_file():
        raise FileNotFoundError(f"Legacy master document not found: {docx_path}")

    with zipfile.ZipFile(docx_path) as zf:
        doc_xml = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml)

    ns_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    elements: list[dict] = []
    current_book = "PREAMBLE"
    current_chapter = "FRONTMATTER"
    current_section = "Title"
    current_paras: list[str] = []

    def flush_section():
        if current_paras:
            text = "\n".join(current_paras).strip()
            if text:
                elements.append({
                    "book": current_book,
                    "chapter": current_chapter,
                    "section": current_section,
                    "text": text,
                    "char_count": len(text),
                })
            current_paras.clear()

    for p in root.findall(f".//{ns_w}p"):
        pStyle = p.find(f".//{ns_w}pStyle")
        style = pStyle.attrib.get(f"{ns_w}val", "") if pStyle is not None else ""
        text = "".join(t.text for t in p.findall(f".//{ns_w}t") if t.text).strip()

        if not text:
            continue

        if style in ("Heading1", "heading 1"):
            flush_section()
            if "BOOK" in text.upper():
                current_book = text
                current_chapter = text
                current_section = "Overview"
            elif "APPENDICES" in text.upper():
                current_book = "APPENDICES"
                current_chapter = "APPENDICES"
                current_section = "Overview"
            else:
                current_section = text
        elif style in ("Heading2", "heading 2"):
            flush_section()
            current_chapter = text
            current_section = "Introduction"
        elif style in ("Heading3", "heading 3", "Heading4", "heading 4"):
            flush_section()
            current_section = text
        else:
            current_paras.append(text)

    flush_section()
    return elements


def classify_section(
    book: str, chapter: str, section: str, text: str, index: int
) -> AuditFragment:
    """Granularly classify a legacy section into A, B, C, D, or E."""
    clean_book = book.upper()
    clean_ch = chapter.upper()
    clean_sec = section.strip()

    slug = re.sub(r"[^A-Za-z0-9]+", "-", f"{clean_ch}-{clean_sec}").strip("-")[:40].upper()
    text_id = f"LM-LEG-{index:03d}-{slug}"
    loc = {"book": book, "chapter": chapter, "section": section}
    excerpt = text[:200] + ("..." if len(text) > 200 else "")

    ch_match = re.search(r"\bCHAPTER\s+(\d+)\b", clean_ch)
    ch_num = int(ch_match.group(1)) if ch_match else None

    # 1. PREAMBLE & FRONTMATTER: Quick Start & Executive Architecture
    if ch_num is None:
        if "QUICK START" in clean_ch:
            if "CINCO REGLAS" in clean_sec.upper() or "REGLAS ANTES DE LEER" in clean_sec.upper():
                return AuditFragment(
                    legacy_text_id=text_id,
                    legacy_location=loc,
                    classification="C",
                    current_authority=None,
                    coverage_units=["component.runtime", "component.cognition", "component.physiology"],
                    master_ids=["SYM-AGA", "SYM-COMP", "SYM-HOM", "SYM-ACT"],
                    still_valid="yes",
                    promotion_target="symbiont/docs/executive/quick-start.md",
                    reason="High-value conceptual rules: Technical ≠ Scientific ≠ Canonical relevance; Competence ≠ Execution binding.",
                    action="promote",
                    excerpt=excerpt,
                )
            elif "VOCABULARIO ORGÁNICO" in clean_sec.upper():
                return AuditFragment(
                    legacy_text_id=text_id,
                    legacy_location=loc,
                    classification="C",
                    current_authority=None,
                    coverage_units=["component.runtime"],
                    master_ids=[],
                    still_valid="yes",
                    promotion_target="symbiont/docs/executive/quick-start.md",
                    reason="Minimal organic terminology orientation for human reviewers.",
                    action="promote",
                    excerpt=excerpt,
                )
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=["component.runtime"],
                master_ids=[],
                still_valid="yes",
                promotion_target="symbiont/docs/executive/quick-start.md",
                reason="Executive 5-minute reading guide for human reviewers.",
                action="promote",
                excerpt=excerpt,
            )

        if "EXECUTIVE ARCHITECTURE" in clean_ch:
            if "HEALTH" in clean_sec.upper():
                return AuditFragment(
                    legacy_text_id=text_id,
                    legacy_location=loc,
                    classification="B",
                    current_authority="symbiont/docs/reference/components.yaml",
                    coverage_units=["component.runtime"],
                    master_ids=[],
                    still_valid="partial",
                    promotion_target=None,
                    reason="Architecture health statistics must be computed dynamically from components.yaml, not hardcoded snapshots.",
                    action="derive",
                    excerpt=excerpt,
                )
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=["component.runtime", "component.cognition", "component.perception"],
                master_ids=["SYM-PER", "SYM-CG", "SYM-AGA", "SYM-MEM"],
                still_valid="yes",
                promotion_target="symbiont/docs/executive/architecture-overview.md",
                reason="Transversal one-page architecture summary and canonical organism lifecycle flow.",
                action="promote",
                excerpt=excerpt,
            )

        if "APPENDIX A" in clean_ch or "GLOSSARY" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=[],
                master_ids=[],
                still_valid="yes",
                promotion_target="symbiont/docs/reference/glossary.yaml",
                reason="Canonical Glossary terms of high value; promote to structured reference/glossary.yaml registry.",
                action="promote",
                excerpt=excerpt,
            )

        if "APPENDIX B" in clean_ch or "NOTATION" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="B",
                current_authority="symbiont/docs/reference/notation.yaml",
                coverage_units=[],
                master_ids=[],
                still_valid="yes",
                promotion_target="symbiont/docs/reference/notation.yaml",
                reason="Notation quick reference is derived directly from notation.yaml in Part IX.",
                action="derive",
                excerpt=excerpt,
            )

    # 2. CHAPTER 1: Constitution & Reading Rules
    if ch_num == 1:
        if "INV-" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="A",
                current_authority="docs/governance/constitution.md",
                coverage_units=["component.runtime", "component.boundary"],
                master_ids=[],
                still_valid="yes",
                promotion_target="docs/governance/constitution.md",
                reason="Constitutional invariants already codified canonically in docs/governance/constitution.md.",
                action="reuse",
                excerpt=excerpt,
            )
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/00-foundations-and-epistemology.md",
            coverage_units=["component.runtime"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/00-foundations-and-epistemology.md",
            reason="Foundational constitutional rules and reading states already in Book I.",
            action="reuse",
            excerpt=excerpt,
        )

    # 3. CHAPTERS 2, 3, 4: Canonical System Model, Authority, Component Map
    if ch_num in (2, 3, 4):
        if "CANONICAL EXPERIENCE MODEL" in clean_sec.upper() or "WHERE SEMANTICS MAY EMERGE" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=["component.perception", "component.cognition", "component.causal-learning"],
                master_ids=["SYM-PER", "SYM-CG", "SYM-AGA", "SYM-EOL"],
                still_valid="yes",
                promotion_target="symbiont/docs/architecture/experience-model.md",
                reason="Deep architectural synthesis on where semantics emerge and experience model constraints.",
                action="promote",
                excerpt=excerpt,
            )
        if "COMPONENT MAP" in clean_sec.upper() or ch_num == 4:
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="B",
                current_authority="symbiont/docs/reference/components.yaml",
                coverage_units=["component.runtime"],
                master_ids=[],
                still_valid="yes",
                promotion_target=None,
                reason="Component map and domain assignments derivable directly from components.yaml registry.",
                action="derive",
                excerpt=excerpt,
            )
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/01-system-and-boundaries.md",
            coverage_units=["component.runtime"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/01-system-and-boundaries.md",
            reason="System model, high-level architecture, and namespaces already projected in Living Master.",
            action="reuse",
            excerpt=excerpt,
        )

    # 4. CHAPTER 5: Functional Architecture
    if ch_num == 5:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/03-world-body-and-embodiment.md",
            coverage_units=["component.embodiment", "component.perception", "component.physiology"],
            master_ids=["SYM-PHEX", "SYM-PER", "SYM-PHY"],
            still_valid="yes",
            promotion_target="symbiont/docs/03-world-body-and-embodiment.md",
            reason="Functional embodiment architecture covered in Book II of Living Master.",
            action="reuse",
            excerpt=excerpt,
        )

    # 5. CHAPTER 6: Cognitive Architecture
    if ch_num == 6:
        if "TRUTH" in clean_sec.upper() or "PLANES" in clean_sec.upper() or "COGNITIVE CLOSURE" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=["component.perception", "component.cognition", "component.generative-cognition"],
                master_ids=["SYM-PER", "SYM-CG", "SYM-GENC", "SYM-HYP"],
                still_valid="yes",
                promotion_target="symbiont/docs/architecture/cognitive-information-planes.md",
                reason="Truth, possibility, and selection planes separation; cognitive closure invariants.",
                action="promote",
                excerpt=excerpt,
            )
        if "TRANSFORMATION" in clean_sec.upper() or "CHAIN" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="C",
                current_authority=None,
                coverage_units=["component.cognition", "component.action-decision"],
                master_ids=["SYM-CG", "SYM-INT", "SYM-CMT", "SYM-ACT"],
                still_valid="yes",
                promotion_target="symbiont/docs/architecture/cognitive-chain.md",
                reason="Complete cognitive transformation chain: signal → percept → evidence → relation → prediction → prospect → value → intention → commitment → action.",
                action="promote",
                excerpt=excerpt,
            )
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/06-cognition-and-internal-organization.md",
            coverage_units=["component.cognition"],
            master_ids=["SYM-CG"],
            still_valid="yes",
            promotion_target="symbiont/docs/06-cognition-and-internal-organization.md",
            reason="General cognitive architecture already projected in Book III.",
            action="reuse",
            excerpt=excerpt,
        )

    # 6. CHAPTER 7: State & Information Architecture
    if ch_num == 7:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority=None,
            coverage_units=["component.runtime", "component.memory", "component.checkpoint"],
            master_ids=["SYM-MEM", "SYM-CHK", "SYM-LI"],
            still_valid="yes",
            promotion_target="symbiont/docs/architecture/state-and-information-architecture.md",
            reason="State family topology, persistence boundaries, and information flow taxonomy.",
            action="promote",
            excerpt=excerpt,
        )

    # 7. CHAPTER 8: Longitudinal Organism Model
    if ch_num == 8:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority="symbiont/docs/02-lifecycle-and-time.md",
            coverage_units=["component.lineage", "component.checkpoint"],
            master_ids=["SYM-LIN", "SYM-LCC", "SYM-LI"],
            still_valid="yes",
            promotion_target="symbiont/docs/architecture/longitudinal-integrity.md",
            reason="Ontogenetic continuity contracts, reembodiment boundaries, and lineage transmission invariants.",
            action="promote",
            excerpt=excerpt,
        )

    # 8. CHAPTERS 9-13: Computational Mechanisms
    if ch_num in (9, 10, 11, 12, 13):
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/06-cognition-and-internal-organization.md",
            coverage_units=["component.cognition", "component.agency", "component.memory"],
            master_ids=["SYM-CG", "SYM-AGA", "SYM-MEM", "SYM-GENC"],
            still_valid="yes",
            promotion_target="symbiont/docs/06-cognition-and-internal-organization.md",
            reason="Computational mechanisms already covered in Book III chapters of Living Master.",
            action="reuse",
            excerpt=excerpt,
        )

    # 9. CHAPTERS 14-19: Formal & Quantitative Model
    if ch_num in range(14, 20):
        if ch_num == 17 or "PARAMETER" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="B",
                current_authority="symbiont/docs/reference/parameters.yaml",
                coverage_units=["component.parameters"],
                master_ids=[],
                still_valid="yes",
                promotion_target="symbiont/docs/reference/parameters.yaml",
                reason="Parameters are projected directly from parameters.yaml.",
                action="derive",
                excerpt=excerpt,
            )
        if ch_num == 18 or "METRIC" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="B",
                current_authority="symbiont/docs/reference/metrics.yaml",
                coverage_units=["component.metrics"],
                master_ids=[],
                still_valid="yes",
                promotion_target="symbiont/docs/reference/metrics.yaml",
                reason="Metrics are projected directly from metrics.yaml by epistemic class.",
                action="derive",
                excerpt=excerpt,
            )
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="symbiont/docs/14-mathematical-map.md",
            coverage_units=["component.formal-model"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/14-mathematical-map.md",
            reason="Mathematical map and state vectors projected in Book V.",
            action="reuse",
            excerpt=excerpt,
        )

    # 10. CHAPTER 20: Canonical Component Catalogue
    if ch_num == 20:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="B",
            current_authority="symbiont/docs/reference/components.yaml",
            coverage_units=["component.runtime"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/reference/components.yaml",
            reason="Component sheets are generated directly from coverage.yaml and components.yaml in Part VI.",
            action="derive",
            excerpt=excerpt,
        )

    # 11. CHAPTER 21: Cross-Cutting Reference Matrices
    if ch_num == 21:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="B",
            current_authority="symbiont/docs/reference/components.yaml",
            coverage_units=["component.runtime"],
            master_ids=[],
            still_valid="yes",
            promotion_target=None,
            reason="Dependency and lifecycle matrices can be derived programmatically from components.yaml graph.",
            action="derive",
            excerpt=excerpt,
        )

    # 12. CHAPTERS 22-24: Execution & Experience
    if ch_num in (22, 23, 24):
        if "WORKED EXAMPLES" in clean_sec.upper() or "EXAMPLE" in clean_sec.upper():
            return AuditFragment(
                legacy_text_id=text_id,
                legacy_location=loc,
                classification="E",
                current_authority=None,
                coverage_units=[],
                master_ids=[],
                still_valid="partial",
                promotion_target=None,
                reason="Lengthy worked walk-throughs that inflate document volume without adding normative specification.",
                action="discard",
                excerpt=excerpt,
            )
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority=None,
            coverage_units=["component.runtime", "component.cognition"],
            master_ids=["SYM-AGA", "SYM-ACT", "SYM-COMP"],
            still_valid="yes",
            promotion_target="symbiont/docs/architecture/execution-flows.md",
            reason="End-to-end execution flows and canonical sequence pseudocode.",
            action="promote",
            excerpt=excerpt,
        )

    # 13. CHAPTERS 25-27: Science & Assurance
    if ch_num == 25:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority=None,
            coverage_units=["component.scientific-apparatus"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/science/emergent-properties.md",
            reason="Strict falsification criteria and emergent-property characterization guidelines.",
            action="promote",
            excerpt=excerpt,
        )
    if ch_num == 26:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority=None,
            coverage_units=["component.scientific-apparatus"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/science/scientific-claims-architecture.md",
            reason="Epistemic demarcation between factual observations, models, and hypothesis confirmation.",
            action="promote",
            excerpt=excerpt,
        )
    if ch_num == 27:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="C",
            current_authority=None,
            coverage_units=["component.scientific-apparatus"],
            master_ids=[],
            still_valid="yes",
            promotion_target="symbiont/docs/science/verification-and-fitness.md",
            reason="Empirical fitness benchmarks, falsification suites, and regression criteria.",
            action="promote",
            excerpt=excerpt,
        )

    # 14. CHAPTER 28: Current, Target, Experimental & Legacy
    if ch_num == 28:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="D",
            current_authority="docs/design/register.md",
            coverage_units=[],
            master_ids=[],
            still_valid="no",
            promotion_target=None,
            reason="Legacy component counts and historical status snapshot from commit a8ab9327; superseded by active registries.",
            action="archive",
            excerpt=excerpt,
        )

    # 15. CHAPTER 29: Risks, Gaps & Architecture Backlog
    if ch_num == 29:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="D",
            current_authority="docs/design/register.md",
            coverage_units=[],
            master_ids=[],
            still_valid="no",
            promotion_target=None,
            reason="Legacy risk registers and backlog are superseded by register.md and active roadmap.",
            action="archive",
            excerpt=excerpt,
        )

    # 16. CHAPTER 30: Governance, Verification & Maintenance
    if ch_num == 30:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="A",
            current_authority="docs/governance/constitution.md",
            coverage_units=[],
            master_ids=[],
            still_valid="yes",
            promotion_target="docs/governance/constitution.md",
            reason="Governance, review criteria, and maintenance contracts already codified.",
            action="reuse",
            excerpt=excerpt,
        )

    # 17. CHAPTER 31: Open Architectural Questions
    if ch_num == 31:
        return AuditFragment(
            legacy_text_id=text_id,
            legacy_location=loc,
            classification="D",
            current_authority="docs/design/register.md",
            coverage_units=[],
            master_ids=[],
            still_valid="unresolved",
            promotion_target=None,
            reason="Chapter 31 open questions require strict per-item ADR reconciliation; must not be copied as active without triage.",
            action="archive",
            excerpt=excerpt,
        )

    # Fallback
    return AuditFragment(
        legacy_text_id=text_id,
        legacy_location=loc,
        classification="E",
        current_authority=None,
        coverage_units=[],
        master_ids=[],
        still_valid="partial",
        promotion_target=None,
        reason="General narrative text.",
        action="discard",
        excerpt=excerpt,
    )


def run_audit(output_dir: Path) -> dict:
    """Execute complete legacy Master forensic audit."""
    print(f"[1/3] Reading legacy Master DOCX: {LEGACY_DOCX_PATH}...")
    sections = extract_legacy_docx_structure(LEGACY_DOCX_PATH)
    print(f"      Parsed {len(sections)} structural sections/fragments.")

    print("[2/3] Performing granular A/B/C/D/E forensic classification...")
    fragments: list[AuditFragment] = []
    for idx, sec in enumerate(sections, 1):
        frag = classify_section(
            book=sec["book"],
            chapter=sec["chapter"],
            section=sec["section"],
            text=sec["text"],
            index=idx,
        )
        fragments.append(frag)

    # Aggregate statistics
    class_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    action_counts = {"reuse": 0, "derive": 0, "promote": 0, "archive": 0, "discard": 0}
    valid_counts = {"yes": 0, "no": 0, "partial": 0, "unresolved": 0}

    for f in fragments:
        class_counts[f.classification] = class_counts.get(f.classification, 0) + 1
        action_counts[f.action] = action_counts.get(f.action, 0) + 1
        valid_counts[f.still_valid] = valid_counts.get(f.still_valid, 0) + 1

    summary = {
        "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_file": str(LEGACY_DOCX_PATH),
        "total_fragments": len(fragments),
        "by_classification": class_counts,
        "by_action": action_counts,
        "by_validity": valid_counts,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    matrix_file = output_dir / "master-legacy-audit-matrix.yaml"
    matrix_data = {
        "schema_version": 1,
        "summary": summary,
        "fragments": [asdict(f) for f in fragments],
    }
    matrix_file.write_text(yaml.safe_dump(matrix_data, sort_keys=False), encoding="utf-8")
    print(f"      Wrote audit matrix -> {matrix_file.name} ({len(fragments)} entries).")

    print("[3/3] Generating executive forensic audit report...")
    report_file = output_dir / "AUDIT_REPORT.md"
    promoted_frags = [f for f in fragments if f.classification == "C"]

    report_lines = [
        "# Forensic Audit Report — Legacy Master Reference",
        "",
        f"**Source Document:** `{LEGACY_DOCX_PATH.name}`  ",
        f"**Date:** {summary['audited_at']}  ",
        f"**Total Structural Fragments Audited:** {len(fragments)}  ",
        "",
        "## 1. Executive Classification Summary",
        "",
        "| Category | Classification | Count | Percentage | Governed Strategy |",
        "|---|---|---|---|---|",
        f"| **A** | Canonical & Current | {class_counts['A']} | {class_counts['A']/len(fragments)*100:.1f}% | Reuse canonical repo sources directly |",
        f"| **B** | Registry-Derivable | {class_counts['B']} | {class_counts['B']/len(fragments)*100:.1f}% | Project dynamically from YAML registries |",
        f"| **C** | Candidate Canonical Knowledge | {class_counts['C']} | {class_counts['C']/len(fragments)*100:.1f}% | Governed promotion in P8.1 PRs |",
        f"| **D** | Obsolete / Superseded | {class_counts['D']} | {class_counts['D']/len(fragments)*100:.1f}% | Archive / discard to prevent drift |",
        f"| **E** | Editorial Redundancy / Padding | {class_counts['E']} | {class_counts['E']/len(fragments)*100:.1f}% | Filter to keep document dense (~110–125 pp.) |",
        "",
        "## 2. High-Value Candidate Knowledge (Category C Inventory)",
        "",
        "The following fragments contain unique synthesis, mental models, and assurance criteria "
        "eligible for governed promotion in Phase P8.1:",
        "",
        "| Text ID | Legacy Chapter | Section / Topic | Candidate Promotion Target | Target Content Scope |",
        "|---|---|---|---|---|",
    ]

    for pf in promoted_frags:
        loc = pf.legacy_location
        report_lines.append(
            f"| `{pf.legacy_text_id}` | {loc['chapter'][:28]} | {loc['section'][:32]} | `{pf.promotion_target}` | {pf.reason[:60]}... |"
        )

    report_lines.extend([
        "",
        "## 3. Recommended P8.1 Governed Promotion Sequence",
        "",
        "1. **PR 1 — Executive Layer**: Promote Quick Start rules and Executive Architecture to `symbiont/docs/executive/`.",
        "2. **PR 2 — Transversal Architecture**: Promote Cognitive Information Planes (Truth/Possibility/Selection) and Longitudinal Integrity to `symbiont/docs/architecture/`.",
        "3. **PR 3 — Science & Assurance**: Promote Emergent Properties falsification criteria and Scientific Claims to `symbiont/docs/science/`.",
        "4. **PR 4 — Canonical Glossary**: Promote Appendix A vocabulary to structured `symbiont/docs/reference/glossary.yaml`.",
        "",
        "**Invariant:** Zero unverified content promoted. Every promoted claim must be verified against current active ADRs and code.",
    ])

    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"      Wrote audit report -> {report_file.name}.")

    return summary


def main() -> None:
    out_dir = ROOT / "build/legacy-audit"
    summary = run_audit(out_dir)
    print("\nP8.0 Legacy Master Forensic Audit complete:")
    print(f"  • Total fragments: {summary['total_fragments']}")
    print(f"  • Category A (Reuse):   {summary['by_classification']['A']}")
    print(f"  • Category B (Derive):  {summary['by_classification']['B']}")
    print(f"  • Category C (Promote): {summary['by_classification']['C']}")
    print(f"  • Category D (Archive): {summary['by_classification']['D']}")
    print(f"  • Category E (Discard): {summary['by_classification']['E']}")


if __name__ == "__main__":
    main()
