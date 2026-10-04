from __future__ import annotations

import re

from .conftest import REPO_ROOT

_MARKDOWN_LINK_RE = re.compile(r"\]\(([^)]+)\)")


def test_architecture_directory_and_old_file_are_gone():
    assert not (REPO_ROOT / "docs" / "architecture").exists()
    assert not (REPO_ROOT / "docs" / "artificial-life-model.md").exists()


def test_architecture_page_routes_to_current_canonical_sources():
    text = (REPO_ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    assert "../symbiont/docs/index.md" in text
    assert "legacy package layout" in text
    assert "current-state specification" in text
    assert "docs/math/" not in text


def test_portal_index_points_at_merged_file():
    text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "docs/architecture.md" in text or "architecture.md" in text
    assert "architecture/entidad-symbiont.md" not in text
    assert "artificial-life-model.md" not in text or "docs/architecture.md" in text


def test_fuentes_taxonomy_points_at_canonical_architecture_sources():
    text = (REPO_ROOT / "symbiont" / "docs" / "explanation" / "concepts" / "SOURCES.md").read_text(
        encoding="utf-8"
    )
    assert "symbiont/docs/" in text
    assert "symbiont/docs/14-mathematical-map.md" in text
    assert "docs/math/" not in text


def test_architecture_page_relative_links_resolve():
    """Keep the current architecture navigation page's local links valid."""
    doc_path = REPO_ROOT / "docs" / "architecture.md"
    text = doc_path.read_text(encoding="utf-8")
    links = _MARKDOWN_LINK_RE.findall(text)
    assert links, "expected docs/architecture.md to contain markdown links"

    broken: list[str] = []
    checked = 0
    for link in links:
        if link.startswith(("http://", "https://", "#")):
            continue
        path_part = link.split("#", 1)[0]
        if not path_part:
            continue
        checked += 1
        target = (doc_path.parent / path_part).resolve()
        if not target.exists():
            broken.append(f"{link} -> {target}")

    assert checked >= 5, f"expected the current source links, found {checked}"
    assert not broken, "broken relative link(s) in docs/architecture.md:\n" + "\n".join(broken)


def test_root_readme_points_at_architecture_navigation_page():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "artificial-life-model.md" not in text
    assert "docs/architecture.md" in text


def test_web_readme_points_at_current_canonical_description():
    text = (REPO_ROOT / "symbiont" / "docs" / "explanation" / "concepts" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "symbiont/docs/index.md" in text
    assert "docs/math/" not in text
