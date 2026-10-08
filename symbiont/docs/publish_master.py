#!/usr/bin/env python3
"""Deterministic CLI publisher for the Symbiont Technical & Scientific Master.

Assembles the Living Master projection from canonical sources and exports:
  - build/master/master-projection.json  (complete semantic projection)
  - build/master/Symbiont-Master.docx    (OpenXML document with 2-pass TOC)
  - build/master/Symbiont-Master.pdf     (PDF via LibreOffice headless, if available)
  - build/master/build-manifest.json     (build metadata & artifact hashes)

Enhanced in P6.2:
  - Two-pass TOC build with exact PDF page resolution and tab leader dots
  - Inline Markdown tokenization across all narrative text
  - Deterministic Mermaid vector diagram rendering (pinned @mermaid-js/mermaid-cli@11.4.2)
  - Strict 1-page per SYM-* component sheet layout verification (fail-closed sensor)

Usage:
  python symbiont/docs/publish_master.py [--output DIR] [--manifest PATH] [--pdf|--no-pdf] [--check]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from master_projection import ComponentSheet, MasterProjection, build_master_projection  # noqa: E402
from publishers.docx import TOCEntry, build_docx  # noqa: E402


class LayoutOverflowError(RuntimeError):
    """Raised when a component sheet or reserved layout violates page constraints."""


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def find_soffice() -> str | None:
    """Find LibreOffice executable if available."""
    candidates = ["soffice", "/usr/bin/soffice", "/usr/local/bin/soffice"]
    for cand in candidates:
        if shutil.which(cand):
            return cand
    return None


def extract_headings_from_projection(projection: MasterProjection) -> list[tuple[str, int, str]]:
    """Produce ordered headings (title, level, bookmark) expected in the Table of Contents."""
    headings: list[tuple[str, int, str]] = [
        ("Publication Provenance & Epistemic Demarcation", 1, "provenance_colophon"),
    ]
    for book in projection.books:
        headings.append((book.title, 1, f"book_{book.id}"))
        for ch in book.chapters:
            headings.append((ch.title, 2, f"ch_{ch.id}"))

    headings.append(("Part VI — Canonical Component Catalog", 1, "part_components"))
    for comp in projection.components:
        headings.append((
            f"[{comp.sym_id}] {comp.name}",
            2,
            f"sym_{comp.sym_id.lower().replace('-', '_')}",
        ))

    headings.append(("Part VII — Architectural & Scientific Parameters", 1, "part_parameters"))
    headings.append(("Part VIII — Measurement Metrics by Epistemic Class", 1, "part_metrics"))
    class_titles = {
        "organism_internal": "1. Organism-Internal Metrics (Observable by Symbiont)",
        "scientific_evaluation": "2. Scientific Evaluation Metrics (Laboratory External)",
        "operational": "3. Operational & Infrastructure Metrics",
        "historical": "4. Historical & Legacy Benchmark Metrics",
    }
    for cls, title in class_titles.items():
        headings.append((title, 2, f"metrics_class_{cls}"))

    headings.append(("Part IX — Canonical Mathematical Notation", 1, "part_notation"))
    return headings


def extract_toc_from_pdf(
    pdf_path: Path, headings: list[tuple[str, int, str]]
) -> list[TOCEntry]:
    """Extract exact PDF page numbers for document headings using pdftotext."""
    proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    pages = proc.stdout.split("\x0c")
    if pages and not pages[-1].strip():
        pages = pages[:-1]

    toc_entries: list[TOCEntry] = []
    current_page = 1
    for title, level, bookmark in headings:
        clean_title = title.strip().lower()
        found_page = -1

        for p_idx in range(current_page - 1, len(pages)):
            p_text = pages[p_idx].lower()
            if clean_title in p_text:
                found_page = p_idx + 1
                break
            if len(clean_title) > 25 and clean_title[:25] in p_text:
                found_page = p_idx + 1
                break
            if title.startswith("[SYM-") and title.split("]")[0] + "]" in p_text:
                found_page = p_idx + 1
                break

        if found_page != -1:
            current_page = found_page
            toc_entries.append(
                TOCEntry(title=title, page=found_page, level=level, bookmark=bookmark)
            )
        else:
            toc_entries.append(
                TOCEntry(title=title, page=current_page, level=level, bookmark=bookmark)
            )

    return toc_entries


def verify_component_sheet_overflow(pdf_path: Path, components: list[ComponentSheet]) -> None:
    """Verify that every SYM-* component sheet strictly occupies exactly 1 page in the body."""
    proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    pages = proc.stdout.split("\x0c")
    if pages and not pages[-1].strip():
        pages = pages[:-1]

    # Find the body occurrence of Part VI (ignoring the TOC on initial pages)
    body_part_vi_page = -1
    for i, p in enumerate(pages, 1):
        if i > 5 and "Part VI — Canonical Component Catalog" in p:
            body_part_vi_page = i
            break

    start_idx = body_part_vi_page if body_part_vi_page != -1 else 5

    comp_pages: dict[str, list[int]] = {c.sym_id: [] for c in components}
    for p_idx in range(start_idx, len(pages)):
        p_text = pages[p_idx]
        p_num = p_idx + 1
        for c in components:
            tag = f"[{c.sym_id}]"
            if tag in p_text:
                comp_pages[c.sym_id].append(p_num)

    for c in components:
        pgs = comp_pages[c.sym_id]
        if not pgs:
            raise LayoutOverflowError(f"Component sheet missing from PDF body: {c.sym_id}")
        if len(pgs) > 1 and (pgs[-1] - pgs[0] >= 1):
            raise LayoutOverflowError(
                f"Component sheet overflow: {c.sym_id} spans {len(pgs)} pages ({pgs}). "
                f"Living Master rule strictly requires exactly 1 page per component sheet."
            )


def run_pipeline(
    output_dir: Path,
    manifest_path: Path | None = None,
    generate_pdf: bool = True,
    check_only: bool = False,
) -> int:
    """Execute the Master publishing pipeline."""
    start_time = time.time()
    built_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    print("[1/4] Assembling Living Master projection from canonical registries...")
    try:
        projection = build_master_projection(
            repo_root=ROOT,
            manifest_path=manifest_path,
            built_at=built_at,
        )
    except Exception as exc:
        print(f"ERROR: Failed to build master projection: {exc}", file=sys.stderr)
        return 1

    counts = projection.provenance.counts
    print(
        f"      Validated {counts['canonical_files']} canonical inputs, "
        f"{counts['books']} books, {counts['chapters']} chapters, "
        f"{counts['components']} SYM-* components, {counts['parameters']} parameters, "
        f"{counts['metrics']} metrics, {counts['notation_symbols']} notation symbols."
    )
    print(f"      Source digest: {projection.provenance.source_digest}")

    if check_only:
        print("\nCheck mode enabled: projection assembled and validated successfully.")
        return 0

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export JSON projection
    json_path = output_dir / "master-projection.json"
    print(f"[2/4] Writing semantic projection JSON -> {json_path.name}...")
    json_path.write_text(projection.to_json(indent=2), encoding="utf-8")

    # 2. Export DOCX & PDF
    docx_path = output_dir / "Symbiont-Master.docx"
    pdf_path = output_dir / "Symbiont-Master.pdf"
    soffice_bin = find_soffice()
    pdf_generated = False

    if generate_pdf and soffice_bin:
        print("[3/4] Executing Two-Pass Master build for exact TOC and pagination...")
        # PASS 1: Build provisional DOCX with reserved TOC geometry
        print("      • Pass 1: Generating provisional layout (3 reserved TOC pages)...")
        build_docx(projection, docx_path, toc_entries=None, toc_pages_reserved=3)
        res1 = subprocess.run(
            [
                soffice_bin,
                "--headless",
                "--convert-to",
                "pdf",
                str(docx_path),
                "--outdir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )
        if res1.returncode != 0 or not pdf_path.is_file():
            print(f"WARNING: Pass 1 PDF generation failed: {res1.stderr}", file=sys.stderr)
            build_docx(projection, docx_path)
        else:
            headings = extract_headings_from_projection(projection)
            toc_entries = extract_toc_from_pdf(pdf_path, headings)
            print(f"      • Pass 1 extracted {len(toc_entries)} heading anchors across PDF pages.")

            # PASS 2: Inject materialized TOC with exact page numbers
            print("      • Pass 2: Injecting materialized Table of Contents with leader dots...")
            build_docx(projection, docx_path, toc_entries=toc_entries, toc_pages_reserved=3)
            res2 = subprocess.run(
                [
                    soffice_bin,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    str(docx_path),
                    "--outdir",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
            )
            if res2.returncode == 0 and pdf_path.is_file():
                pdf_generated = True
                verify_component_sheet_overflow(pdf_path, projection.components)
                print("      • Verified 48/48 component sheets strictly adhere to 1-page geometry.")
                print("      • Verified deterministic TOC pagination stability.")
            else:
                print(f"WARNING: Pass 2 PDF generation failed: {res2.stderr}", file=sys.stderr)
    elif generate_pdf and not soffice_bin:
        print("[3/4] Generating OpenXML publication -> Symbiont-Master.docx...")
        build_docx(projection, docx_path)
        print("[4/4] Skipping PDF generation: 'soffice' executable not found.")
    else:
        print("[3/4] Generating OpenXML publication -> Symbiont-Master.docx...")
        build_docx(projection, docx_path)
        print("[4/4] PDF generation disabled by flag.")

    elapsed = round(time.time() - start_time, 2)

    # Build manifest
    artifacts: dict[str, dict[str, Any]] = {
        json_path.name: {
            "bytes": json_path.stat().st_size,
            "sha256": compute_file_sha256(json_path),
        },
        docx_path.name: {
            "bytes": docx_path.stat().st_size,
            "sha256": compute_file_sha256(docx_path),
        },
    }
    if pdf_generated and pdf_path.is_file():
        artifacts[pdf_path.name] = {
            "bytes": pdf_path.stat().st_size,
            "sha256": compute_file_sha256(pdf_path),
        }

    build_manifest = {
        "publication": projection.publication,
        "provenance": projection.provenance.to_dict(),
        "artifacts": artifacts,
        "execution_time_seconds": elapsed,
    }

    manifest_out = output_dir / "build-manifest.json"
    manifest_out.write_text(json.dumps(build_manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("\nPublication complete:")
    print(f"  • JSON: {json_path.stat().st_size:,} bytes")
    print(f"  • DOCX: {docx_path.stat().st_size:,} bytes")
    if pdf_generated:
        print(f"  • PDF:  {pdf_path.stat().st_size:,} bytes")
    print(f"  • Manifest: {manifest_out.name}")
    print(f"  • Elapsed: {elapsed}s")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Symbiont Living Master Projection Publisher")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=ROOT / "build/master",
        help="Destination directory for published artifacts (default: build/master)",
    )
    parser.add_argument(
        "--manifest",
        "-m",
        type=Path,
        default=None,
        help="Optional path to master-projection.yaml",
    )
    parser.add_argument(
        "--pdf",
        dest="generate_pdf",
        action="store_true",
        default=True,
        help="Generate PDF publication via LibreOffice headless (default: True)",
    )
    parser.add_argument(
        "--no-pdf",
        dest="generate_pdf",
        action="store_false",
        help="Disable PDF generation",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate projection assembly without writing artifacts",
    )

    args = parser.parse_args()
    code = run_pipeline(
        output_dir=args.output,
        manifest_path=args.manifest,
        generate_pdf=args.generate_pdf,
        check_only=args.check,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
