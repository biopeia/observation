# symbiont/docs/publishers/mermaid.py
"""Deterministic Mermaid diagram renderer for publication pipelines.

Enforces:
1. Pinned CLI version: @mermaid-js/mermaid-cli@11.4.2.
2. Fail-closed execution: raises descriptive error if mmdc is missing or version mismatches.
3. Zero runtime network downloads: no dynamic npx fetches.
4. Deterministic content hashing: SHA-256 over pinned version + configuration + source code.
5. Dual output: primary vector SVG with high-DPI raster PNG fallback.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PINNED_MMDC_VERSION = "11.4.2"

# Deterministic render styling: clean neutral theme for technical publication
MERMAID_CONFIG = {
    "theme": "neutral",
    "themeVariables": {
        "primaryColor": "#EEF2F6",
        "primaryTextColor": "#0F172A",
        "primaryBorderColor": "#94A3B8",
        "lineColor": "#475569",
        "secondaryColor": "#F8FAFC",
        "tertiaryColor": "#FFFFFF",
        "fontFamily": "Calibri, system-ui, sans-serif",
        "fontSize": "14px",
    },
}


class MermaidEnvironmentError(RuntimeError):
    """Raised when Mermaid CLI environment does not meet pinned invariants."""


def verify_mmdc_binary() -> str:
    """Verify that mmdc is installed and matches the pinned version."""
    bin_path = shutil.which("mmdc")
    if not bin_path:
        raise MermaidEnvironmentError(
            f"Mermaid CLI (mmdc) is not found in PATH. "
            f"Publication requires pinned @mermaid-js/mermaid-cli@{PINNED_MMDC_VERSION}."
        )

    try:
        proc = subprocess.run(
            [bin_path, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = proc.stdout.strip()
    except Exception as exc:
        raise MermaidEnvironmentError(
            f"Failed to query mmdc version from {bin_path}: {exc}"
        ) from exc

    if version != PINNED_MMDC_VERSION:
        raise MermaidEnvironmentError(
            f"Mermaid CLI version mismatch: found '{version}', "
            f"expected strictly pinned '{PINNED_MMDC_VERSION}'."
        )

    return bin_path


def parse_svg_dimensions(svg_content: str) -> tuple[float, float]:
    """Extract natural width and height (or viewBox) from an SVG string."""
    # Try viewBox="minX minY width height"
    vb_match = re.search(r'viewBox=[\"\']([\d\.\s\-]+)[\"\']', svg_content)
    if vb_match:
        parts = [float(x) for x in vb_match.group(1).split()]
        if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
            return parts[2], parts[3]

    # Try explicit width/height
    w_match = re.search(r'width=[\"\']([\d\.]+)p?t?x?[\"\']', svg_content)
    h_match = re.search(r'height=[\"\']([\d\.]+)p?t?x?[\"\']', svg_content)
    if w_match and h_match:
        return float(w_match.group(1)), float(h_match.group(1))

    # Safe fallback aspect ratio: 800 x 400
    return 800.0, 400.0


def render_mermaid_diagram(
    code: str,
    cache_dir: Path,
) -> tuple[Path, Path, str, float, float]:
    """Render a mermaid diagram deterministically to SVG and PNG.

    Args:
        code: Mermaid diagram source code.
        cache_dir: Directory where rendered artifacts and cache are stored.

    Returns:
        tuple of (svg_path, png_path, digest, width, height)
    """
    mmdc_bin = verify_mmdc_binary()

    normalized_code = code.strip().replace("\r\n", "\n")
    config_bytes = json.dumps(MERMAID_CONFIG, sort_keys=True).encode("utf-8")
    hasher = hashlib.sha256()
    hasher.update(PINNED_MMDC_VERSION.encode("utf-8"))
    hasher.update(b":")
    hasher.update(config_bytes)
    hasher.update(b":")
    hasher.update(normalized_code.encode("utf-8"))
    digest = hasher.hexdigest()

    cache_dir.mkdir(parents=True, exist_ok=True)
    svg_file = cache_dir / f"mermaid-{digest}.svg"
    png_file = cache_dir / f"mermaid-{digest}.png"

    if svg_file.is_file() and png_file.is_file():
        svg_text = svg_file.read_text(encoding="utf-8")
        w, h = parse_svg_dimensions(svg_text)
        return svg_file, png_file, digest, w, h

    with tempfile.TemporaryDirectory() as tmp_d:
        tmp_path = Path(tmp_d)
        mmd_input = tmp_path / "diagram.mmd"
        cfg_input = tmp_path / "config.json"
        tmp_svg = tmp_path / "diagram.svg"
        tmp_png = tmp_path / "diagram.png"

        mmd_input.write_text(normalized_code, encoding="utf-8")
        cfg_input.write_text(json.dumps(MERMAID_CONFIG), encoding="utf-8")

        # 1. Render primary vector SVG
        cmd_svg = [
            mmdc_bin,
            "-i",
            str(mmd_input),
            "-o",
            str(tmp_svg),
            "-c",
            str(cfg_input),
            "-b",
            "transparent",
        ]
        res_svg = subprocess.run(cmd_svg, capture_output=True, text=True)
        if res_svg.returncode != 0 or not tmp_svg.is_file():
            raise RuntimeError(
                f"Mermaid SVG render failed (exit {res_svg.returncode}):\n{res_svg.stderr}\nCode:\n{code}"
            )

        # 2. Render fallback raster PNG (2x scale for print crispness)
        cmd_png = [
            mmdc_bin,
            "-i",
            str(mmd_input),
            "-o",
            str(tmp_png),
            "-c",
            str(cfg_input),
            "-b",
            "white",
            "-s",
            "2",
        ]
        res_png = subprocess.run(cmd_png, capture_output=True, text=True)
        if res_png.returncode != 0 or not tmp_png.is_file():
            raise RuntimeError(
                f"Mermaid PNG render failed (exit {res_png.returncode}):\n{res_png.stderr}\nCode:\n{code}"
            )

        # Copy to cache
        shutil.copyfile(tmp_svg, svg_file)
        shutil.copyfile(tmp_png, png_file)

    svg_text = svg_file.read_text(encoding="utf-8")
    w, h = parse_svg_dimensions(svg_text)
    return svg_file, png_file, digest, w, h
