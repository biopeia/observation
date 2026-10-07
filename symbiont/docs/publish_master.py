#!/usr/bin/env python3
"""Deterministic CLI publisher for the Symbiont Technical & Scientific Master.

Assembles the Living Master projection from canonical sources and exports:
  - build/master/master-projection.json  (complete semantic projection)
  - build/master/Symbiont-Master.docx    (OpenXML document)
  - build/master/Symbiont-Master.pdf     (PDF via LibreOffice headless, if available)
  - build/master/build-manifest.json     (build metadata & artifact hashes)

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

from master_projection import build_master_projection  # noqa: E402
from publishers.docx import build_docx  # noqa: E402


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

    # 2. Export DOCX
    docx_path = output_dir / "Symbiont-Master.docx"
    print(f"[3/4] Generating OpenXML publication -> {docx_path.name}...")
    build_docx(projection, docx_path)

    # 3. Export PDF
    pdf_path = output_dir / "Symbiont-Master.pdf"
    soffice_bin = find_soffice()
    pdf_generated = False

    if generate_pdf and soffice_bin:
        print(f"[4/4] Converting to PDF via {soffice_bin} -> {pdf_path.name}...")
        proc = subprocess.run(
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
        if proc.returncode == 0 and pdf_path.is_file():
            pdf_generated = True
        else:
            print(
                f"WARNING: LibreOffice conversion failed (exit {proc.returncode}): {proc.stderr}",
                file=sys.stderr,
            )
    elif generate_pdf and not soffice_bin:
        print("[4/4] Skipping PDF generation: 'soffice' executable not found.")
    else:
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
        help="Path to custom master-projection.yaml editorial manifest",
    )
    parser.add_argument(
        "--pdf",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable/disable headless LibreOffice PDF generation (default: true)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check projection assembly without generating files",
    )

    args = parser.parse_args()
    rc = run_pipeline(
        output_dir=args.output,
        manifest_path=args.manifest,
        generate_pdf=args.pdf,
        check_only=args.check,
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
