# tests/docs/test_master_projection.py
"""Test suite for Master Projection model and publishing pipeline.

Validates the complete P6 contract:
1. Projection builds cleanly without errors or warnings.
2. All 5 Books and 15 canonical chapters projected in manifest order.
3. Exactly 48 component sheets projected with matching SYM-* IDs in catalog order.
4. Closed authority table fields verified for every component sheet.
5. All 13 parameters present and linked to valid owners.
6. All 14 metrics present, partitioned across the 4 epistemic classes.
7. All 17 notation symbols present, matching notation.yaml.
8. Epistemic tags parsed and attributed to blocks.
9. Digest determinism: repeated builds yield identical SHA-256 digest.
10. Provenance metadata complete: commit, canonical files listed, timestamp, counts.
11. Fail closed on missing/corrupt canonical YAML.
12. Fail closed on missing/unmapped SYM-* component.
13. Fail closed on invalid chapter path.
14. Summary snapshot comparison with tests/docs/fixtures/master_projection_summary.json.
15. Mechanical DOCX QA test: valid OpenXML zip archive and parseable XML tree.
16. Headless LibreOffice PDF conversion test (when soffice is installed).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from master_projection import (  # noqa: E402
    MasterProjection,
    build_master_projection,
    parse_markdown_blocks,
)
from publish_master import find_soffice  # noqa: E402
from publishers.docx import build_docx  # noqa: E402


@pytest.fixture(scope="module")
def default_projection() -> MasterProjection:
    """Load default projection once for fast read-only validation."""
    return build_master_projection()


def test_1_projection_builds_cleanly(default_projection: MasterProjection) -> None:
    """1. Verify projection builds cleanly with valid provenance and publication."""
    assert default_projection is not None
    assert default_projection.publication.get("title") == "Symbiont"
    assert default_projection.provenance.source_digest
    assert len(default_projection.provenance.source_digest) == 64
    assert default_projection.provenance.counts["canonical_files"] == 21


def test_2_books_and_chapters_order(default_projection: MasterProjection) -> None:
    """2. Verify all 5 Books and 15 canonical chapters projected in manifest order."""
    expected_books = [
        ("foundations", 3, ["epistemology", "boundaries", "lifecycle"]),
        ("embodiment-physiology", 3, ["embodiment", "perception", "physiology"]),
        ("cognition-agency", 4, ["cognition", "agency", "learning", "generative"]),
        ("lineage-observation", 4, ["lineage", "persistence", "observation", "methodology"]),
        ("formal-map", 1, ["math-map"]),
    ]

    assert len(default_projection.books) == 5
    for idx, (b_id, ch_count, ch_ids) in enumerate(expected_books):
        book = default_projection.books[idx]
        assert book.id == b_id
        assert len(book.chapters) == ch_count
        assert [c.id for c in book.chapters] == ch_ids
        for chapter in book.chapters:
            assert len(chapter.blocks) > 0, f"Chapter {chapter.id} has no parsed blocks"


def test_3_all_48_components_cataloged_in_manifest_order(
    default_projection: MasterProjection,
) -> None:
    """3. Verify exactly 48 component sheets projected with matching SYM-* IDs in catalog order."""
    manifest_p = ROOT / "symbiont/docs/reference/master-projection.yaml"
    with manifest_p.open("r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    expected_ordering = manifest["component_catalog"]["ordering"]
    assert len(expected_ordering) == 48

    projected_syms = [c.sym_id for c in default_projection.components]
    assert len(projected_syms) == 48
    assert projected_syms == expected_ordering


def test_4_closed_authority_table_fields_coherence(default_projection: MasterProjection) -> None:
    """4. Verify closed authority table fields for every component sheet."""
    cov_path = ROOT / "symbiont/docs/coverage.yaml"
    comp_path = ROOT / "symbiont/docs/reference/components.yaml"
    with cov_path.open("r", encoding="utf-8") as f:
        cov_units = yaml.safe_load(f)["units"]
    with comp_path.open("r", encoding="utf-8") as f:
        comps = yaml.safe_load(f)["components"]

    for sheet in default_projection.components:
        cov_entry = cov_units[sheet.coverage_unit]
        comp_entry = comps[sheet.sym_id]

        # Name from components.yaml
        assert sheet.name == comp_entry["name"]
        # Status from coverage.yaml
        assert sheet.status == cov_entry["status"]
        # Owner domain from coverage.yaml
        assert sheet.owner_domain == cov_entry["owner_domain"]
        # State family from components.yaml
        assert sheet.state_family == comp_entry["state"]["family"]
        # Authority from components.yaml
        assert sheet.authority_owns == comp_entry["authority"]["owns"]
        assert sheet.authority_may_decide == comp_entry["authority"]["may_decide"]
        assert sheet.authority_must_not == comp_entry["authority"]["must_not"]
        # Lifecycle from components.yaml
        assert sheet.lifecycle == comp_entry["lifecycle"]
        # Implementation from coverage.yaml
        assert sheet.implementation == cov_entry.get("implementation", [])
        # Tests from coverage.yaml
        assert sheet.tests == cov_entry.get("tests", [])


def test_5_parameters_integrity(default_projection: MasterProjection) -> None:
    """5. Verify all 13 parameters present, linked to valid owners in coverage.yaml."""
    assert len(default_projection.parameters) == 13

    cov_path = ROOT / "symbiont/docs/coverage.yaml"
    with cov_path.open("r", encoding="utf-8") as f:
        cov_units = yaml.safe_load(f)["units"]

    for p in default_projection.parameters:
        assert p.id
        assert p.symbol
        assert p.owner in cov_units, f"Parameter {p.id} owner {p.owner} missing in coverage"
        assert p.source in {"CODE", "DESIGN", "STUDY", "FORMAL"}


def test_6_metrics_epistemic_partitioning(default_projection: MasterProjection) -> None:
    """6. Verify all 14 metrics present, partitioned across the 4 epistemic classes."""
    total_metrics = sum(len(ml) for ml in default_projection.metrics.values())
    assert total_metrics == 14

    expected_partition = {
        "organism_internal": 6,
        "scientific_evaluation": 3,
        "operational": 2,
        "historical": 3,
    }

    for cls, count in expected_partition.items():
        assert cls in default_projection.metrics, f"Epistemic class {cls} missing from metrics"
        assert len(default_projection.metrics[cls]) == count, (
            f"Class {cls}: expected {count} metrics, found {len(default_projection.metrics[cls])}"
        )


def test_7_notation_symbols_integrity(default_projection: MasterProjection) -> None:
    """7. Verify all 17 notation symbols present, matching notation.yaml."""
    assert len(default_projection.notation) == 17
    notation_path = ROOT / "symbiont/docs/reference/notation.yaml"
    with notation_path.open("r", encoding="utf-8") as f:
        notations = yaml.safe_load(f)["symbols"]

    for n in default_projection.notation:
        assert n.symbol in notations
        assert n.domain
        assert n.scope


def test_8_epistemic_tags_parsing() -> None:
    """8. Verify epistemic tags parsed and attributed to blocks."""
    sample_md = (
        "# General Foundations [CODE]\n\n"
        "This is an implementation description [SCIENCE] with empirical bounds.\n\n"
        "- Observation [FORMAL]\n"
        "- Speculative idea [DESIGN]\n\n"
        "| Term [OPEN] | Definition |\n"
        "| --- | --- |\n"
        "| Test | Value |\n"
    )

    blocks = parse_markdown_blocks(sample_md)
    assert len(blocks) == 4

    # Heading block
    assert blocks[0].block_type == "heading"
    assert blocks[0].epistemic_tags == ["CODE"]

    # Paragraph block
    assert blocks[1].block_type == "paragraph"
    assert blocks[1].epistemic_tags == ["SCIENCE"]

    # Bullet list block
    assert blocks[2].block_type == "bullet_list"
    assert "FORMAL" in blocks[2].epistemic_tags
    assert "DESIGN" in blocks[2].epistemic_tags

    # Table block
    assert blocks[3].block_type == "table"
    assert "OPEN" in blocks[3].epistemic_tags


def test_9_digest_determinism() -> None:
    """9. Verify rebuilding yields byte-for-byte identical SHA-256 digest."""
    p1 = build_master_projection()
    p2 = build_master_projection()
    assert p1.provenance.source_digest == p2.provenance.source_digest


def test_10_provenance_metadata(default_projection: MasterProjection) -> None:
    """10. Verify provenance metadata completeness."""
    prov = default_projection.provenance
    assert prov.commit_sha
    assert len(prov.canonical_files) == 21
    assert "symbiont/docs/coverage.yaml" in prov.canonical_files
    assert "symbiont/docs/reference/components.yaml" in prov.canonical_files
    assert "symbiont/docs/00-foundations-and-epistemology.md" in prov.canonical_files
    assert prov.counts["components"] == 48


def test_11_fail_closed_corrupted_yaml(tmp_path: Path) -> None:
    """11. Verify fail closed on missing/corrupt canonical YAML."""
    corrupt_manifest = tmp_path / "corrupt-manifest.yaml"
    corrupt_manifest.write_text("invalid: yaml: duplicate: :", encoding="utf-8")

    with pytest.raises(Exception):
        build_master_projection(manifest_path=corrupt_manifest)


def test_12_fail_closed_missing_component(tmp_path: Path) -> None:
    """12. Verify fail closed on missing/unmapped SYM-* component."""
    manifest_p = ROOT / "symbiont/docs/reference/master-projection.yaml"
    with manifest_p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Inject unknown SYM ID into ordering
    data["component_catalog"]["ordering"][0] = "SYM-UNKNOWN-FAKE"
    test_manifest = tmp_path / "test-manifest.yaml"
    test_manifest.write_text(yaml.dump(data), encoding="utf-8")

    with pytest.raises(ValueError, match="SYM-UNKNOWN-FAKE"):
        build_master_projection(manifest_path=test_manifest)


def test_13_fail_closed_invalid_chapter_path(tmp_path: Path) -> None:
    """13. Verify fail closed on invalid chapter path."""
    manifest_p = ROOT / "symbiont/docs/reference/master-projection.yaml"
    with manifest_p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Point first chapter to non-existent file
    data["books"][0]["chapters"][0]["source"] = "symbiont/docs/non-existent-chapter.md"
    test_manifest = tmp_path / "test-manifest.yaml"
    test_manifest.write_text(yaml.dump(data), encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        build_master_projection(manifest_path=test_manifest)


def test_14_golden_summary_snapshot(default_projection: MasterProjection) -> None:
    """14. Summary snapshot comparison with tests/docs/fixtures/master_projection_summary.json."""
    golden_path = ROOT / "tests/docs/fixtures/master_projection_summary.json"
    assert golden_path.is_file(), f"Golden fixture missing: {golden_path}"

    with golden_path.open("r", encoding="utf-8") as f:
        expected_summary = json.load(f)

    current_summary = default_projection.summary_dict()
    assert current_summary == expected_summary, (
        f"Master projection summary diverged from golden snapshot:\n"
        f"Current: {json.dumps(current_summary, indent=2)}\n"
        f"Expected: {json.dumps(expected_summary, indent=2)}"
    )


def test_15_docx_mechanical_structure(default_projection: MasterProjection, tmp_path: Path) -> None:
    """15. Mechanical DOCX QA: validates OpenXML ZIP structure, schema, and XML tree."""
    docx_file = tmp_path / "test-master.docx"
    build_docx(default_projection, docx_file)

    assert docx_file.is_file()
    assert docx_file.stat().st_size > 30000

    # Inspect zip structure
    with zipfile.ZipFile(docx_file, "r") as zf:
        namelist = zf.namelist()
        required_parts = [
            "[Content_Types].xml",
            "_rels/.rels",
            "word/_rels/document.xml.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/header1.xml",
            "word/footer1.xml",
        ]
        for part in required_parts:
            assert part in namelist, f"Required OpenXML part {part} missing from docx"

        # Parse XML trees cleanly
        doc_xml = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml)
        assert root.tag.endswith("document")

        # Verify TOC field is present
        assert b'w:instr="TOC' in doc_xml

        # Verify cover title and components present
        assert b"Symbiont" in doc_xml
        assert b"SYM-GEN" in doc_xml
        assert b"SYM-CAP" in doc_xml


def test_16_pdf_conversion_optional(default_projection: MasterProjection, tmp_path: Path) -> None:
    """16. Headless LibreOffice PDF conversion test (when soffice is installed)."""
    soffice = find_soffice()
    if not soffice:
        pytest.skip("LibreOffice soffice not available in environment")

    docx_file = tmp_path / "Symbiont-Master.docx"
    build_docx(default_projection, docx_file)

    pdf_file = tmp_path / "Symbiont-Master.pdf"
    proc = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", str(docx_file), "--outdir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert pdf_file.is_file()
    assert pdf_file.stat().st_size > 500000


def test_17_toc_materialization(tmp_path: Path) -> None:
    """17. Two-pass build produces materialized TOC with leader dots and page numbers."""
    from publish_master import run_pipeline

    soffice = find_soffice()
    if not soffice:
        pytest.skip("LibreOffice soffice not available")

    out_dir = tmp_path / "master_out"
    ret = run_pipeline(output_dir=out_dir, generate_pdf=True)
    assert ret == 0

    pdf_p = out_dir / "Symbiont-Master.pdf"
    assert pdf_p.is_file()

    proc = subprocess.run(
        ["pdftotext", "-layout", str(pdf_p), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    pages = proc.stdout.split("\x0c")

    # Verify TOC on page 3..5 contains leader dots and page numbers
    toc_text = "\n".join(pages[2:5])
    assert "..." in toc_text
    assert "Book I — Foundations & Architecture" in toc_text
    assert "[SYM-GEN]" in toc_text
    assert "Part VI — Canonical Component Catalog" in toc_text


def test_18_inline_markdown_runs() -> None:
    """18. Inline markdown parser correctly extracts bold, italic, code without syntax leakage."""
    from publishers.docx import parse_inline_markdown, render_inline_runs

    sample = "The **Symbiont** kernel enforces `INV-BOUNDARY-001` with *strict* isolation."
    tokens = parse_inline_markdown(sample)
    kinds = [t[0] for t in tokens]
    assert "bold" in kinds
    assert "code" in kinds
    assert "italic" in kinds

    runs = render_inline_runs(sample)
    assert "<w:b/>" in runs
    assert "Consolas" in runs
    assert "<w:i/>" in runs
    # Confirm markdown syntax markers are not in the text content
    assert "**Symbiont**" not in runs
    assert "`INV-BOUNDARY-001`" not in runs


def test_19_mermaid_diagram_embedding(tmp_path: Path) -> None:
    """19. Mermaid diagram is rendered to vector SVG and embedded into DrawingML."""
    if not shutil.which("mmdc"):
        pytest.skip("mmdc (Mermaid CLI) not available in environment")

    from publishers.mermaid import render_mermaid_diagram, verify_mmdc_binary

    mmdc = verify_mmdc_binary()
    assert mmdc

    cache = tmp_path / "diagrams"
    code = "graph LR\n  A[Origin] --> B[Target]\n"
    svg_p, png_p, digest, w, h = render_mermaid_diagram(code, cache)
    assert svg_p.is_file() and svg_p.stat().st_size > 100
    assert png_p.is_file() and png_p.stat().st_size > 100
    assert w > 0 and h > 0


def test_20_component_sheet_single_page_invariant(
    default_projection: MasterProjection, tmp_path: Path
) -> None:
    """20. Every SYM-* component sheet strictly occupies exactly 1 page in generated PDF."""
    from publish_master import verify_component_sheet_overflow

    # Test against freshly generated master in build/master or tmp
    out_dir = tmp_path / "master_qa"
    from publish_master import run_pipeline

    soffice = find_soffice()
    if not soffice:
        pytest.skip("LibreOffice soffice not available")

    ret = run_pipeline(output_dir=out_dir, generate_pdf=True)
    assert ret == 0
    pdf_p = out_dir / "Symbiont-Master.pdf"
    assert pdf_p.is_file()

    # Should complete without LayoutOverflowError
    verify_component_sheet_overflow(pdf_p, default_projection.components)


def test_21_mermaid_fails_closed_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """21. Mermaid CLI raises MermaidEnvironmentError when mmdc is not in PATH."""
    from publishers.mermaid import MermaidEnvironmentError, verify_mmdc_binary

    monkeypatch.setattr("shutil.which", lambda cmd: None)
    with pytest.raises(MermaidEnvironmentError, match="Mermaid CLI.*not found in PATH"):
        verify_mmdc_binary()


def test_22_mermaid_fails_closed_when_version_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """22. Mermaid CLI raises MermaidEnvironmentError when mmdc version is incompatible."""
    from publishers.mermaid import MermaidEnvironmentError, verify_mmdc_binary

    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/mmdc")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, stdout="10.0.0", stderr=""),
    )
    with pytest.raises(MermaidEnvironmentError, match="version mismatch"):
        verify_mmdc_binary()


def test_23_mermaid_relationship_targets_resolve(
    default_projection: MasterProjection, tmp_path: Path
) -> None:
    """23. Every OpenXML image relationship resolves to an existing package part."""
    import posixpath

    docx_file = tmp_path / "test-master-media.docx"
    build_docx(default_projection, docx_file)

    rel_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    with zipfile.ZipFile(docx_file, "r") as zf:
        names = set(zf.namelist())
        rel_root = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
        image_rels = [
            rel
            for rel in rel_root.findall("r:Relationship", rel_ns)
            if rel.attrib.get("Type", "").endswith("/image")
        ]
        assert image_rels, "Expected at least one embedded image relationship"

        for rel in image_rels:
            target = rel.attrib["Target"]
            resolved = posixpath.normpath(posixpath.join("word", target))
            assert resolved in names, (
                f"Broken image relationship {rel.attrib.get('Id')}: "
                f"Target={target!r} resolves to missing package part {resolved!r}"
            )


def test_24_mermaid_visible_in_rendered_pdf(tmp_path: Path) -> None:
    """24. Publication PDF contains a rendered Mermaid image, not only source/fallback text."""
    from publish_master import run_pipeline

    soffice = find_soffice()
    if not soffice:
        pytest.skip("LibreOffice soffice not available")
    if not shutil.which("mmdc"):
        pytest.skip("mmdc (Mermaid CLI) not available")
    if not shutil.which("pdfimages"):
        pytest.skip("pdfimages not available")

    out_dir = tmp_path / "master_mermaid_qa"
    assert run_pipeline(output_dir=out_dir, generate_pdf=True) == 0

    pdf_file = out_dir / "Symbiont-Master.pdf"
    proc = subprocess.run(
        ["pdfimages", "-list", str(pdf_file)],
        capture_output=True,
        text=True,
        check=True,
    )

    # pdfimages emits two header lines followed by one line per rasterized/vector image.
    image_lines = [
        line
        for line in proc.stdout.splitlines()
        if line.strip() and line.lstrip()[:1].isdigit()
    ]
    assert image_lines, "No rendered images found in publication PDF"
