# symbiont/docs/publishers/docx.py
"""Pure standard-library OpenXML DOCX generator for the Living Master projection.

Generates a publication-grade WordprocessingML (.docx) document without external
Python dependencies (such as python-docx), guaranteeing 100% determinism, zero
modifications to pyproject.toml / uv.lock, and full compatibility with LibreOffice
headless PDF conversion.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from master_projection import (
    ComponentSheet,
    MarkdownBlock,
    MasterProjection,
    MetricEntry,
    NotationEntry,
    ParameterEntry,
)


def escape_xml(text: Any) -> str:
    """Escape special XML characters cleanly."""
    if text is None:
        return ""
    s = str(text)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class DocxBuilder:
    """Constructs WordprocessingML body elements deterministically."""

    def __init__(self) -> None:
        self.body_elements: list[str] = []

    def add_page_break(self) -> None:
        self.body_elements.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def add_heading(self, text: str, level: int = 1, page_break: bool = False) -> None:
        pb = "<w:pageBreakBefore/>" if page_break else ""
        style = f"Heading{min(max(level, 1), 4)}"
        color = "0F172A" if level == 1 else ("1E293B" if level == 2 else "334155")
        sz = 36 if level == 1 else (28 if level == 2 else (24 if level == 3 else 22))
        before = 280 if level == 1 else (200 if level == 2 else 140)
        after = 120 if level <= 2 else 80

        xml = (
            f"<w:p>"
            f"<w:pPr>"
            f'<w:pStyle w:val="{style}"/>'
            f"{pb}"
            f'<w:spacing w:before="{before}" w:after="{after}"/>'
            f'<w:outlineLvl w:val="{level - 1}"/>'
            f"</w:pPr>"
            f"<w:r>"
            f'<w:rPr><w:b/><w:sz w:val="{sz}"/><w:color w:val="{color}"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape_xml(text)}</w:t>'
            f"</w:r>"
            f"</w:p>"
        )
        self.body_elements.append(xml)

    def add_paragraph(
        self,
        text: str,
        style: str = "Normal",
        bold: bool = False,
        italic: bool = False,
        color: str = "1E293B",
        size: int = 21,
        space_after: int = 120,
        space_before: int = 0,
        align: str | None = None,
        code_font: bool = False,
    ) -> None:
        jc_xml = f'<w:jc w:val="{align}"/>' if align else ""
        font_name = "Consolas" if code_font else "Calibri"
        b_xml = "<w:b/>" if bold else ""
        i_xml = "<w:i/>" if italic else ""

        xml = (
            f"<w:p>"
            f"<w:pPr>"
            f'<w:pStyle w:val="{style}"/>'
            f"{jc_xml}"
            f'<w:spacing w:before="{space_before}" w:after="{space_after}"/>'
            f"</w:pPr>"
            f"<w:r>"
            f"<w:rPr>"
            f'<w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}"/>'
            f"{b_xml}{i_xml}"
            f'<w:sz w:val="{size}"/>'
            f'<w:color w:val="{color}"/>'
            f"</w:rPr>"
            f'<w:t xml:space="preserve">{escape_xml(text)}</w:t>'
            f"</w:r>"
            f"</w:p>"
        )
        self.body_elements.append(xml)

    def add_bullet_item(self, text: str, tag_prefix: str = "") -> None:
        tag_run = ""
        if tag_prefix:
            tag_run = (
                f'<w:r><w:rPr><w:b/><w:sz w:val="20"/><w:color w:val="2563EB"/></w:rPr>'
                f'<w:t xml:space="preserve">[{escape_xml(tag_prefix)}] </w:t></w:r>'
            )

        xml = (
            f"<w:p>"
            f"<w:pPr>"
            f'<w:pStyle w:val="ListBullet"/>'
            f'<w:spacing w:before="30" w:after="60"/>'
            f'<w:ind w:left="360" w:hanging="240"/>'
            f"</w:pPr>"
            f'<w:r><w:rPr><w:sz w:val="20"/><w:color w:val="64748B"/></w:rPr>'
            f'<w:t xml:space="preserve">• </w:t></w:r>'
            f"{tag_run}"
            f"<w:r>"
            f'<w:rPr><w:sz w:val="21"/><w:color w:val="1E293B"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape_xml(text)}</w:t>'
            f"</w:r>"
            f"</w:p>"
        )
        self.body_elements.append(xml)

    def add_numbered_item(self, index: int, text: str) -> None:
        xml = (
            f"<w:p>"
            f"<w:pPr>"
            f'<w:pStyle w:val="ListNumber"/>'
            f'<w:spacing w:before="30" w:after="60"/>'
            f'<w:ind w:left="480" w:hanging="360"/>'
            f"</w:pPr>"
            f'<w:r><w:rPr><w:b/><w:sz w:val="20"/><w:color w:val="64748B"/></w:rPr>'
            f'<w:t xml:space="preserve">{index}. </w:t></w:r>'
            f"<w:r>"
            f'<w:rPr><w:sz w:val="21"/><w:color w:val="1E293B"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape_xml(text)}</w:t>'
            f"</w:r>"
            f"</w:p>"
        )
        self.body_elements.append(xml)

    def add_blockquote(self, text: str) -> None:
        xml = (
            f"<w:p>"
            f"<w:pPr>"
            f'<w:ind w:left="720"/>'
            f"<w:pBdr>"
            f'<w:left w:val="single" w:sz="18" w:space="12" w:color="94A3B8"/>'
            f"</w:pBdr>"
            f'<w:spacing w:before="120" w:after="120"/>'
            f"</w:pPr>"
            f"<w:r>"
            f'<w:rPr><w:i/><w:sz w:val="20"/><w:color w:val="475569"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape_xml(text)}</w:t>'
            f"</w:r>"
            f"</w:p>"
        )
        self.body_elements.append(xml)

    def add_code_block(self, code: str, language: str = "") -> None:
        # Render code box with light slate background and soft border
        lines = code.splitlines()
        if not lines:
            lines = [""]

        p_elements = []
        for line in lines:
            p_elements.append(
                f"<w:p>"
                f"<w:pPr>"
                f'<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
                f"</w:pPr>"
                f"<w:r>"
                f"<w:rPr>"
                f'<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
                f'<w:sz w:val="18"/>'
                f'<w:color w:val="0F172A"/>'
                f"</w:rPr>"
                f'<w:t xml:space="preserve">{escape_xml(line)}</w:t>'
                f"</w:r>"
                f"</w:p>"
            )

        inner_p = "".join(p_elements)
        tbl_xml = (
            f"<w:tbl>"
            f"<w:tblPr>"
            f'<w:tblW w:w="9360" w:type="dxa"/>'
            f"<w:tblBorders>"
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'<w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f"</w:tblBorders>"
            f"<w:tblCellMar>"
            f'<w:top w:w="120" w:type="dxa"/>'
            f'<w:bottom w:w="120" w:type="dxa"/>'
            f'<w:left w:w="180" w:type="dxa"/>'
            f'<w:right w:w="180" w:type="dxa"/>'
            f"</w:tblCellMar>"
            f"</w:tblPr>"
            f'<w:tblGrid><w:gridCol w:w="9360"/></w:tblGrid>'
            f"<w:tr>"
            f"<w:tc>"
            f"<w:tcPr>"
            f'<w:tcW w:w="9360" w:type="dxa"/>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="F8FAFC"/>'
            f"</w:tcPr>"
            f"{inner_p}"
            f"</w:tc>"
            f"</w:tr>"
            f"</w:tbl>"
        )
        self.body_elements.append(tbl_xml)
        self.body_elements.append('<w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>')

    def add_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        col_widths: list[int] | None = None,
    ) -> None:
        num_cols = len(headers)
        if num_cols == 0 and rows:
            num_cols = len(rows[0])
        if num_cols == 0:
            return

        if col_widths is None or len(col_widths) != num_cols:
            base_w = 9360 // num_cols
            col_widths = [base_w] * num_cols

        grid_cols = "".join(f'<w:gridCol w:w="{w}"/>' for w in col_widths)

        # Build header row
        header_cells = []
        for i, h in enumerate(headers):
            w = col_widths[i]
            header_cells.append(
                f"<w:tc>"
                f"<w:tcPr>"
                f'<w:tcW w:w="{w}" w:type="dxa"/>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="F1F5F9"/>'
                f"</w:tcPr>"
                f"<w:p>"
                f'<w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
                f"<w:r>"
                f'<w:rPr><w:b/><w:sz w:val="19"/><w:color w:val="334155"/></w:rPr>'
                f'<w:t xml:space="preserve">{escape_xml(h)}</w:t>'
                f"</w:r>"
                f"</w:p>"
                f"</w:tc>"
            )
        header_tr = (
            f"<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>{''.join(header_cells)}</w:tr>"
        )

        # Build data rows
        data_trs = []
        for row_idx, r in enumerate(rows):
            cells = []
            shd_fill = "FFFFFF" if row_idx % 2 == 0 else "F8FAFC"
            for c_idx in range(num_cols):
                w = col_widths[c_idx]
                val = r[c_idx] if c_idx < len(r) else ""
                cells.append(
                    f"<w:tc>"
                    f"<w:tcPr>"
                    f'<w:tcW w:w="{w}" w:type="dxa"/>'
                    f'<w:shd w:val="clear" w:color="auto" w:fill="{shd_fill}"/>'
                    f"</w:tcPr>"
                    f"<w:p>"
                    f'<w:pPr><w:spacing w:before="50" w:after="50"/></w:pPr>'
                    f"<w:r>"
                    f'<w:rPr><w:sz w:val="18"/><w:color w:val="1E293B"/></w:rPr>'
                    f'<w:t xml:space="preserve">{escape_xml(val)}</w:t>'
                    f"</w:r>"
                    f"</w:p>"
                    f"</w:tc>"
                )
            data_trs.append(f"<w:tr><w:trPr><w:cantSplit/></w:trPr>{''.join(cells)}</w:tr>")

        tbl_xml = (
            f"<w:tbl>"
            f"<w:tblPr>"
            f'<w:tblW w:w="9360" w:type="dxa"/>'
            f"<w:tblBorders>"
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'<w:insideV w:val="none"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f"</w:tblBorders>"
            f"<w:tblCellMar>"
            f'<w:top w:w="80" w:type="dxa"/>'
            f'<w:bottom w:w="80" w:type="dxa"/>'
            f'<w:left w:w="140" w:type="dxa"/>'
            f'<w:right w:w="140" w:type="dxa"/>'
            f"</w:tblCellMar>"
            f"</w:tblPr>"
            f"<w:tblGrid>{grid_cols}</w:tblGrid>"
            f"{header_tr}"
            f"{''.join(data_trs)}"
            f"</w:tbl>"
        )
        self.body_elements.append(tbl_xml)
        self.body_elements.append('<w:p><w:pPr><w:spacing w:after="140"/></w:pPr></w:p>')


def render_markdown_block(builder: DocxBuilder, block: MarkdownBlock) -> None:
    """Render a single MarkdownBlock into docx elements."""
    if block.block_type == "heading":
        tag_prefix = ""
        if block.epistemic_tags:
            tag_prefix = " ".join(f"[{t}]" for t in block.epistemic_tags) + " "
        title = tag_prefix + str(block.content)
        # Shift chapter subheadings to levels 2..4
        level = min(max(block.level + 1, 2), 4)
        builder.add_heading(title, level=level)

    elif block.block_type == "paragraph":
        tag_prefix = ""
        if block.epistemic_tags:
            tag_prefix = " ".join(f"[{t}]" for t in block.epistemic_tags) + " "
        builder.add_paragraph(tag_prefix + str(block.content))

    elif block.block_type == "bullet_list":
        items = block.content if isinstance(block.content, list) else [str(block.content)]
        for item in items:
            builder.add_bullet_item(item)

    elif block.block_type == "numbered_list":
        items = block.content if isinstance(block.content, list) else [str(block.content)]
        for idx, item in enumerate(items, 1):
            builder.add_numbered_item(idx, item)

    elif block.block_type == "blockquote":
        builder.add_blockquote(str(block.content))

    elif block.block_type == "code_block":
        builder.add_code_block(str(block.content), language=block.language)

    elif block.block_type == "table":
        table_dict = block.content if isinstance(block.content, dict) else {}
        headers = table_dict.get("headers", [])
        rows = table_dict.get("rows", [])
        builder.add_table(headers, rows)


def render_component_sheet(builder: DocxBuilder, sheet: ComponentSheet) -> None:
    """Render a comprehensive canonical authority sheet for one SYM-* component."""
    builder.add_heading(f"[{sheet.sym_id}] {sheet.name}", level=2, page_break=True)

    headers = ["Canonical Authority Dimension", "Specification / Value"]
    col_widths = [2800, 6560]

    lifecycle_str = (
        f"birth: {sheet.lifecycle.get('birth', 'N/A')}; "
        f"checkpoint: {sheet.lifecycle.get('checkpoint', 'N/A')}; "
        f"restart: {sheet.lifecycle.get('restart', 'N/A')}; "
        f"reembodiment: {sheet.lifecycle.get('reembodiment', 'N/A')}; "
        f"reproduction: {sheet.lifecycle.get('reproduction', 'N/A')}"
    )

    may_decide_str = (
        "\n".join(f"• {x}" for x in sheet.authority_may_decide)
        if sheet.authority_may_decide
        else "None"
    )
    must_not_str = (
        "\n".join(f"• {x}" for x in sheet.authority_must_not)
        if sheet.authority_must_not
        else "None"
    )

    params_str = (
        ", ".join(f"{p['id']} ({p.get('symbol', '')})" for p in sheet.parameters)
        if sheet.parameters
        else "None"
    )
    metrics_str = ", ".join(m["id"] for m in sheet.metrics) if sheet.metrics else "None"

    rows: list[list[str]] = [
        ["Canonical ID", sheet.sym_id],
        ["Coverage Unit ID", sheet.coverage_unit],
        ["Implementation Status", sheet.status],
        ["Owner Domain", sheet.owner_domain],
        ["Participating Domains", ", ".join(sheet.participating_domains) or "None"],
        ["State Family", sheet.state_family],
        ["Authority: Owns", sheet.authority_owns],
        ["Authority: May Decide", may_decide_str],
        ["Authority: Must Not", must_not_str],
        ["Lifecycle Semantics", lifecycle_str],
        ["Interfaces: Inputs", ", ".join(sheet.inputs) or "None"],
        ["Interfaces: Outputs", ", ".join(sheet.outputs) or "None"],
        ["Consumers", ", ".join(sheet.consumers) or "None"],
        ["Implementation Sources", ", ".join(sheet.implementation) or "None (formal/design)"],
        ["Test Coverage", ", ".join(sheet.tests) or "None"],
        ["Design Documents & ADRs", ", ".join(sheet.design + sheet.adrs) or "None"],
        ["Direct Dependencies", ", ".join(sheet.depends_on) or "None"],
        ["Canonical Chapters", ", ".join(sheet.canonical_docs) or "None"],
        ["Owned Parameters", params_str],
        ["Consumed Metrics", metrics_str],
    ]

    builder.add_table(headers, rows, col_widths=col_widths)


def render_parameters_section(builder: DocxBuilder, parameters: list[ParameterEntry]) -> None:
    """Render Part VII: Architectural & Scientific Parameters."""
    builder.add_heading(
        "Part VII — Architectural & Scientific Parameters", level=1, page_break=True
    )
    builder.add_paragraph(
        "Canonical registry of numerical, architectural, and experimental parameters "
        "governing organism runtime behavior and experimental apparatus."
    )

    headers = [
        "Symbol",
        "Parameter ID",
        "Dim / Unit",
        "Source",
        "Range",
        "Default",
        "Owner Unit",
        "Code Anchor",
    ]
    col_widths = [1000, 2100, 1000, 800, 1100, 960, 1400, 1000]

    rows: list[list[str]] = []
    for p in parameters:
        dim_unit = f"{p.dimension} ({p.unit})" if p.unit != "1" else p.dimension
        impl_str = p.implementation.get("symbol", "") if p.implementation else ""
        rows.append(
            [
                p.symbol,
                p.id,
                dim_unit,
                p.source,
                p.range,
                str(p.canonical_default),
                p.owner,
                impl_str,
            ]
        )

    builder.add_table(headers, rows, col_widths=col_widths)


def render_metrics_section(
    builder: DocxBuilder, metrics_by_class: dict[str, list[MetricEntry]]
) -> None:
    """Render Part VIII: Measurement Metrics partitioned by Epistemic Class."""
    builder.add_heading(
        "Part VIII — Measurement Metrics by Epistemic Class", level=1, page_break=True
    )
    builder.add_paragraph(
        "Measurement metrics partitioned strictly by epistemic boundary: organism-internal state, "
        "scientific hypothesis evaluation, operational performance, and historical benchmarks."
    )

    class_titles = {
        "organism_internal": "1. Organism-Internal Metrics (Observable by Symbiont)",
        "scientific_evaluation": "2. Scientific Evaluation Metrics (Laboratory External)",
        "operational": "3. Operational & Infrastructure Metrics",
        "historical": "4. Historical & Legacy Benchmark Metrics",
    }

    headers = ["Metric ID", "Owner Domain", "Consumer Unit", "Unit", "Definition"]
    col_widths = [2200, 1100, 1800, 800, 3460]

    for cls in ["organism_internal", "scientific_evaluation", "operational", "historical"]:
        m_list = metrics_by_class.get(cls, [])
        if not m_list:
            continue
        builder.add_heading(class_titles.get(cls, cls.title()), level=2)
        rows: list[list[str]] = []
        for m in m_list:
            rows.append(
                [
                    m.id,
                    m.owner_domain,
                    m.consumer or "None (Lab)",
                    m.unit,
                    m.definition,
                ]
            )
        builder.add_table(headers, rows, col_widths=col_widths)


def render_notation_section(builder: DocxBuilder, notation: list[NotationEntry]) -> None:
    """Render Part IX: Canonical Mathematical Notation."""
    builder.add_heading("Part IX — Canonical Mathematical Notation", level=1, page_break=True)
    builder.add_paragraph(
        "Canonical formal notation reconciled against the Living Master state vector. "
        "All symbols enforce zero mathematical collision across the formal model."
    )

    headers = [
        "Symbol",
        "Domain",
        "Scope",
        "Organism Observable",
        "Meaning & Disallowed Semantic Drift",
    ]
    col_widths = [1100, 1100, 900, 1100, 5160]

    rows: list[list[str]] = []
    for n in notation:
        obs_str = "Yes" if n.observable_by_symbiont else "No (External/Hidden)"
        disallowed = (
            f" [Forbidden: {', '.join(n.forbidden_meanings)}]" if n.forbidden_meanings else ""
        )
        meaning_full = f"{n.meaning}{disallowed}"
        rows.append(
            [
                n.symbol,
                n.domain,
                n.scope,
                obs_str,
                meaning_full,
            ]
        )

    builder.add_table(headers, rows, col_widths=col_widths)


def build_docx(projection: MasterProjection, output_path: Path) -> Path:
    """Generate the full WordprocessingML .docx publication file."""
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    builder = DocxBuilder()

    # 1. Cover Page
    pub = projection.publication
    builder.add_paragraph(
        pub.get("title", "Symbiont"),
        style="Title",
        bold=True,
        color="0F172A",
        size=56,
        space_before=1440,
        space_after=200,
    )
    builder.add_paragraph(
        pub.get("subtitle", "Technical and Scientific Master Reference"),
        style="Subtitle",
        bold=False,
        color="475569",
        size=28,
        space_after=400,
    )
    builder.add_paragraph(
        pub.get("edition", "Living Master — Canonical Projection"),
        italic=True,
        color="64748B",
        size=22,
        space_after=200,
    )
    builder.add_paragraph(
        f"Authority: {pub.get('authority', 'Canonical Corpus')}",
        color="64748B",
        size=20,
        space_after=1440,
    )

    # Cover metadata card
    prov = projection.provenance
    builder.add_paragraph(
        f"Built at: {prov.built_at}", bold=False, color="475569", size=18, space_after=40
    )
    builder.add_paragraph(
        f"Commit SHA: {prov.commit_sha}", code_font=True, color="475569", size=18, space_after=40
    )
    builder.add_paragraph(
        f"Canonical Source Digest: {prov.source_digest}",
        code_font=True,
        color="475569",
        size=18,
        space_after=0,
    )
    builder.add_page_break()

    # 2. Colophon / Provenance Section
    builder.add_heading("Publication Provenance & Epistemic Demarcation", level=1)
    builder.add_paragraph(
        "This document is an automated, deterministic projection of the Symbiont canonical architecture "
        "and scientific reference registries. It does not introduce new specifications, alter existing invariants, "
        "or interpret experimental outcomes. All contents reflect the exact state of the canonical files at the "
        "recorded commit hash."
    )
    builder.add_paragraph(
        "Canonical Projection Inventory:",
        bold=True,
        color="334155",
        space_before=100,
        space_after=60,
    )
    counts = prov.counts
    inv_rows = [
        ["Total Canonical Input Files", str(counts.get("canonical_files", 0))],
        ["Thematic Books Projected", str(counts.get("books", 0))],
        ["Canonical Narrative Chapters", str(counts.get("chapters", 0))],
        ["Canonical SYM-* Components", str(counts.get("components", 0))],
        ["Architectural & Scientific Parameters", str(counts.get("parameters", 0))],
        ["Measurement Metrics (Epistemic Classes)", str(counts.get("metrics", 0))],
        ["Formal Mathematical Notation Symbols", str(counts.get("notation_symbols", 0))],
    ]
    builder.add_table(["Inventory Dimension", "Count"], inv_rows, col_widths=[4000, 5360])
    builder.add_page_break()

    # 3. Table of Contents Field
    builder.add_heading("Table of Contents", level=1)
    builder.body_elements.append(
        '<w:p><w:fldSimple w:instr="TOC \\o &quot;1-3&quot; \\h \\z \\u"/></w:p>'
    )
    builder.add_page_break()

    # 4. Books and Chapters
    for book in projection.books:
        builder.add_heading(book.title, level=1, page_break=True)
        if book.description:
            builder.add_paragraph(
                book.description, italic=True, color="64748B", size=22, space_after=200
            )

        for chapter in book.chapters:
            builder.add_heading(chapter.title, level=2)
            builder.add_paragraph(
                f"Source: {chapter.source_path}",
                italic=True,
                color="94A3B8",
                size=18,
                space_after=140,
            )
            for block in chapter.blocks:
                render_markdown_block(builder, block)

    # 5. Component Catalog (Part VI)
    builder.add_heading("Part VI — Canonical Component Catalog", level=1, page_break=True)
    builder.add_paragraph(
        "Structured semantic authority sheets for all 48 canonical SYM-* components. "
        "Each sheet unifies implementation paths, state families, lifecycle invariants, "
        "authority boundaries, dependencies, owned parameters, and consumed metrics."
    )
    for comp in projection.components:
        render_component_sheet(builder, comp)

    # 6. Registries
    render_parameters_section(builder, projection.parameters)
    render_metrics_section(builder, projection.metrics)
    render_notation_section(builder, projection.notation)

    # Final section properties with headers, footers and page numbering
    sect_pr = (
        "<w:sectPr>"
        '<w:headerReference w:type="default" r:id="rId2"/>'
        '<w:footerReference w:type="default" r:id="rId3"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720"/>'
        "</w:sectPr>"
    )

    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "<w:body>\n" + "".join(builder.body_elements) + sect_pr + "</w:body>\n"
        "</w:document>"
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
        '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>\n'
        '  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>\n'
        '  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>\n'
        "</Types>"
    )

    pkg_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
        "</Relationships>"
    )

    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
        '  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>\n'
        '  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>\n'
        "</Relationships>"
    )

    header_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
        "  <w:p>\n"
        '    <w:pPr><w:jc w:val="right"/></w:pPr>\n'
        '    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="64748B"/></w:rPr>'
        "    <w:t>Symbiont — Technical &amp; Scientific Master Reference</w:t></w:r>\n"
        "  </w:p>\n"
        "</w:hdr>"
    )

    footer_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
        "  <w:p>\n"
        '    <w:pPr><w:jc w:val="center"/></w:pPr>\n'
        '    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="64748B"/></w:rPr><w:t>Page </w:t></w:r>\n'
        '    <w:fldSimple w:instr="PAGE"/>\n'
        '    <w:r><w:rPr><w:sz w:val="18"/><w:color w:val="64748B"/></w:rPr><w:t> of </w:t></w:r>\n'
        '    <w:fldSimple w:instr="NUMPAGES"/>\n'
        "  </w:p>\n"
        "</w:ftr>"
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
        "  <w:docDefaults>\n"
        "    <w:rPrDefault>\n"
        "      <w:rPr>\n"
        '        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>\n'
        '        <w:sz w:val="21"/>\n'
        '        <w:color w:val="1E293B"/>\n'
        "      </w:rPr>\n"
        "    </w:rPrDefault>\n"
        "    <w:pPrDefault>\n"
        "      <w:pPr>\n"
        '        <w:spacing w:after="120" w:line="276" w:lineRule="auto"/>\n'
        "      </w:pPr>\n"
        "    </w:pPrDefault>\n"
        "  </w:docDefaults>\n"
        '  <w:style w:type="paragraph" w:styleId="Heading1">\n'
        '    <w:name w:val="heading 1"/>\n'
        '    <w:pPr><w:spacing w:before="280" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>\n'
        '    <w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="0F172A"/></w:rPr>\n'
        "  </w:style>\n"
        '  <w:style w:type="paragraph" w:styleId="Heading2">\n'
        '    <w:name w:val="heading 2"/>\n'
        '    <w:pPr><w:spacing w:before="200" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr>\n'
        '    <w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1E293B"/></w:rPr>\n'
        "  </w:style>\n"
        '  <w:style w:type="paragraph" w:styleId="Heading3">\n'
        '    <w:name w:val="heading 3"/>\n'
        '    <w:pPr><w:spacing w:before="160" w:after="80"/><w:outlineLvl w:val="2"/></w:pPr>\n'
        '    <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="334155"/></w:rPr>\n'
        "  </w:style>\n"
        '  <w:style w:type="paragraph" w:styleId="Heading4">\n'
        '    <w:name w:val="heading 4"/>\n'
        '    <w:pPr><w:spacing w:before="120" w:after="60"/><w:outlineLvl w:val="3"/></w:pPr>\n'
        '    <w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="475569"/></w:rPr>\n'
        "  </w:style>\n"
        '  <w:style w:type="paragraph" w:styleId="Title">\n'
        '    <w:name w:val="Title"/>\n'
        '    <w:rPr><w:b/><w:sz w:val="56"/><w:color w:val="0F172A"/></w:rPr>\n'
        "  </w:style>\n"
        '  <w:style w:type="paragraph" w:styleId="Subtitle">\n'
        '    <w:name w:val="Subtitle"/>\n'
        '    <w:rPr><w:sz w:val="28"/><w:color w:val="475569"/></w:rPr>\n'
        "  </w:style>\n"
        "</w:styles>"
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", pkg_rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/header1.xml", header_xml)
        zf.writestr("word/footer1.xml", footer_xml)
        zf.writestr("word/styles.xml", styles_xml)
        zf.writestr("word/document.xml", doc_xml)

    return output_path
