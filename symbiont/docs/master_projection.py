# symbiont/docs/master_projection.py
"""Master Projection data models, assembly engine, and validation.

Constructs the Living Master projection model deterministically from the canonical
corpus and reference registries without inventing semantics, modifying canonical sources,
or relying on external runtime dependencies.

Closed field authority mapping:
  - ID SYM-*: coverage.yaml / components.yaml
  - Name: components.yaml
  - Status, Owner domain, Participating domains: coverage.yaml
  - Authority (owns, may_decide, must_not), State family, Lifecycle: components.yaml
  - Implementation, Tests, Design, ADRs, Dependencies: coverage.yaml
  - Parameters: parameters.yaml (where owner == coverage_unit)
  - Metrics: metrics.yaml (where consumer == coverage_unit)
  - Notation: notation.yaml
  - Narrative: canonical Markdown chapters
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT / "symbiont/docs/reference/master-projection.yaml"
DEFAULT_COVERAGE_PATH = ROOT / "symbiont/docs/coverage.yaml"
DEFAULT_COMPONENTS_PATH = ROOT / "symbiont/docs/reference/components.yaml"
DEFAULT_PARAMETERS_PATH = ROOT / "symbiont/docs/reference/parameters.yaml"
DEFAULT_METRICS_PATH = ROOT / "symbiont/docs/reference/metrics.yaml"
DEFAULT_NOTATION_PATH = ROOT / "symbiont/docs/reference/notation.yaml"

TAG_PATTERN = re.compile(r"\[(CODE|FORMAL|DESIGN|SCIENCE|OPEN)\]")


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML Loader that strictly rejects duplicate keys."""

    pass


def _construct_mapping(
    loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, Any]:
    loader.flatten_mapping(node)
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(
                f"Duplicate YAML key found: {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_strict_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file enforcing unique mapping keys and fail-closed syntax."""
    if not path.is_file():
        raise FileNotFoundError(f"Canonical YAML file not found: {path}")
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.load(fp, Loader=UniqueKeySafeLoader)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root at {path} must be a dictionary, got {type(data).__name__}")
    return data


@dataclass(frozen=True)
class MarkdownBlock:
    """A semantic block parsed from a canonical Markdown chapter."""

    block_type: str  # heading, paragraph, bullet_list, numbered_list, blockquote, code_block, table
    content: Any  # str, list[str], or dict with headers/rows for table
    level: int = 0
    language: str = ""
    epistemic_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_type": self.block_type,
            "content": self.content,
            "level": self.level,
            "language": self.language,
            "epistemic_tags": list(self.epistemic_tags),
        }


@dataclass(frozen=True)
class ChapterProjection:
    """A single canonical chapter projected within a Book."""

    id: str
    title: str
    source_path: str
    blocks: list[MarkdownBlock]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source_path": self.source_path,
            "blocks": [b.to_dict() for b in self.blocks],
        }


@dataclass(frozen=True)
class BookProjection:
    """A thematic Book grouping canonical chapters."""

    id: str
    title: str
    description: str
    chapters: list[ChapterProjection]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "chapters": [c.to_dict() for c in self.chapters],
        }


@dataclass(frozen=True)
class ComponentSheet:
    """Complete semantic authority specification for a canonical SYM-* component."""

    sym_id: str
    coverage_unit: str
    name: str
    status: str
    owner_domain: str
    participating_domains: list[str]
    state_family: str
    authority_owns: str
    authority_may_decide: list[str]
    authority_must_not: list[str]
    lifecycle: dict[str, str]
    inputs: list[str]
    outputs: list[str]
    consumers: list[str]
    implementation: list[str]
    tests: list[str]
    design: list[str]
    adrs: list[str]
    depends_on: list[str]
    canonical_docs: list[str]
    parameters: list[dict[str, Any]]
    metrics: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ParameterEntry:
    """Architectural or scientific parameter definition."""

    id: str
    symbol: str
    dimension: str
    unit: str
    source: str
    range: str
    canonical_default: Any
    owner: str
    interpretation: str
    implementation: dict[str, str] | None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class MetricEntry:
    """Measurement metric definition partitioned by epistemic class."""

    id: str
    owner_domain: str
    epistemic_class: str
    definition: str
    unit: str
    consumer: str | None
    target: str | None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class NotationEntry:
    """Formal mathematical symbol entry from the notation registry."""

    symbol: str
    meaning: str
    scope: str
    owner: str
    observable_by_symbiont: bool
    domain: str
    aliases: list[str]
    forbidden_meanings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ProvenanceMetadata:
    """Source provenance and build integrity metadata."""

    commit_sha: str
    source_digest: str
    canonical_files: list[str]
    built_at: str
    counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class MasterProjection:
    """Complete semantic projection of the Symbiont Technical & Scientific Master."""

    provenance: ProvenanceMetadata
    publication: dict[str, Any]
    books: list[BookProjection]
    components: list[ComponentSheet]
    parameters: list[ParameterEntry]
    metrics: dict[str, list[MetricEntry]]  # epistemic_class -> list[MetricEntry]
    notation: list[NotationEntry]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance": self.provenance.to_dict(),
            "publication": dict(self.publication),
            "books": [b.to_dict() for b in self.books],
            "components": [c.to_dict() for c in self.components],
            "parameters": [p.to_dict() for p in self.parameters],
            "metrics": {k: [m.to_dict() for m in v] for k, v in self.metrics.items()},
            "notation": [n.to_dict() for n in self.notation],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def summary_dict(self) -> dict[str, Any]:
        """Compact determinism snapshot for regression testing."""
        return {
            "source_digest": self.provenance.source_digest,
            "counts": dict(self.provenance.counts),
            "books": [
                {
                    "id": b.id,
                    "title": b.title,
                    "chapter_count": len(b.chapters),
                    "chapters": [c.id for c in b.chapters],
                }
                for b in self.books
            ],
            "component_order": [c.sym_id for c in self.components],
            "parameters": [p.id for p in self.parameters],
            "metrics_by_class": {
                cls: [m.id for m in metrics] for cls, metrics in sorted(self.metrics.items())
            },
            "notation_symbols": [n.symbol for n in self.notation],
        }


def parse_markdown_blocks(text: str) -> list[MarkdownBlock]:
    """Parse Markdown text into structured blocks with epistemic tags."""
    lines = text.splitlines()
    blocks: list[MarkdownBlock] = []
    i = 0
    n = len(lines)

    while i < n:
        raw_line = lines[i]
        stripped = raw_line.strip()
        if not stripped:
            i += 1
            continue

        # Code block
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(
                MarkdownBlock(
                    block_type="code_block",
                    content="\n".join(code_lines),
                    language=lang,
                    epistemic_tags=[],
                )
            )
            continue

        # Heading
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading_title = stripped.lstrip("#").strip()
            tags = TAG_PATTERN.findall(heading_title)
            blocks.append(
                MarkdownBlock(
                    block_type="heading",
                    content=heading_title,
                    level=level,
                    epistemic_tags=tags,
                )
            )
            i += 1
            continue

        # Table
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines: list[str] = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            headers: list[str] = []
            data_rows: list[list[str]] = []
            if table_lines:
                raw_headers = [c.strip() for c in table_lines[0].strip("|").split("|")]
                headers = raw_headers
                # skip separator row if present
                start_row = 2 if len(table_lines) > 1 and "---" in table_lines[1] else 1
                for r in table_lines[start_row:]:
                    row_cells = [c.strip() for c in r.strip("|").split("|")]
                    data_rows.append(row_cells)

            tags: list[str] = []
            for h in headers:
                tags.extend(TAG_PATTERN.findall(h))
            for r in data_rows:
                for c in r:
                    tags.extend(TAG_PATTERN.findall(c))

            blocks.append(
                MarkdownBlock(
                    block_type="table",
                    content={"headers": headers, "rows": data_rows},
                    epistemic_tags=sorted(list(set(tags))),
                )
            )
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            joined_quote = "\n".join(quote_lines)
            tags = TAG_PATTERN.findall(joined_quote)
            blocks.append(
                MarkdownBlock(
                    block_type="blockquote",
                    content=joined_quote,
                    epistemic_tags=tags,
                )
            )
            continue

        # Bullet list
        if stripped.startswith(("- ", "* ")):
            items: list[str] = []
            while i < n and (
                lines[i].strip().startswith(("- ", "* ")) or (lines[i].startswith("  ") and items)
            ):
                line_str = lines[i].strip()
                if line_str.startswith(("- ", "* ")):
                    items.append(line_str[2:].strip())
                elif items:
                    items[-1] += " " + line_str
                i += 1
            tags: list[str] = []
            for it in items:
                tags.extend(TAG_PATTERN.findall(it))
            blocks.append(
                MarkdownBlock(
                    block_type="bullet_list",
                    content=items,
                    epistemic_tags=sorted(list(set(tags))),
                )
            )
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", stripped):
            items: list[str] = []
            while i < n and (
                re.match(r"^\d+\.\s", lines[i].strip()) or (lines[i].startswith("  ") and items)
            ):
                line_str = lines[i].strip()
                m = re.match(r"^\d+\.\s+(.*)", line_str)
                if m:
                    items.append(m.group(1))
                elif items:
                    items[-1] += " " + line_str
                i += 1
            tags = []
            for it in items:
                tags.extend(TAG_PATTERN.findall(it))
            blocks.append(
                MarkdownBlock(
                    block_type="numbered_list",
                    content=items,
                    epistemic_tags=sorted(list(set(tags))),
                )
            )
            continue

        # Paragraph
        para_lines = [stripped]
        i += 1
        while i < n:
            next_line = lines[i]
            next_strip = next_line.strip()
            if not next_strip:
                break
            if next_strip.startswith(("#", "```", ">", "|", "- ", "* ")) or re.match(
                r"^\d+\.\s", next_strip
            ):
                break
            para_lines.append(next_strip)
            i += 1
        full_text = " ".join(para_lines)
        tags = TAG_PATTERN.findall(full_text)
        blocks.append(
            MarkdownBlock(
                block_type="paragraph",
                content=full_text,
                epistemic_tags=tags,
            )
        )

    return blocks


def compute_source_digest(repo_root: Path, file_paths: list[Path]) -> str:
    """Calculate deterministic SHA-256 digest across canonical source files."""
    hasher = hashlib.sha256()
    # Sort files by relative POSIX path for byte-level stability across platforms
    sorted_files = sorted(file_paths, key=lambda p: p.relative_to(repo_root).as_posix())
    for p in sorted_files:
        rel_posix = p.relative_to(repo_root).as_posix()
        if not p.is_file():
            raise FileNotFoundError(f"Canonical source file missing during digest computation: {p}")
        data = p.read_bytes()
        hasher.update(rel_posix.encode("utf-8") + b"\0" + data + b"\0")
    return hasher.hexdigest()


def get_git_commit(repo_root: Path) -> str:
    """Read the current git commit SHA cleanly, or return UNKNOWN."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return "UNKNOWN"


def build_master_projection(
    repo_root: Path | None = None,
    manifest_path: Path | None = None,
    built_at: str = "2026-10-07T00:00:00Z",
) -> MasterProjection:
    """Build and validate the complete MasterProjection model.

    Fail-closed:
      - Validates manifest structure and all referenced files exist.
      - Enforces that exactly 48 SYM-* components are cataloged and mapped.
      - Enforces that all parameters, metrics, and notation symbols load without error.
      - Verifies that closed authority table rules are satisfied.
    """
    root = (repo_root or ROOT).resolve()
    manifest_p = (
        manifest_path or (root / "symbiont/docs/reference/master-projection.yaml")
    ).resolve()

    manifest_data = load_strict_yaml(manifest_p)
    coverage_p = root / "symbiont/docs/coverage.yaml"
    components_p = root / "symbiont/docs/reference/components.yaml"
    parameters_p = root / "symbiont/docs/reference/parameters.yaml"
    metrics_p = root / "symbiont/docs/reference/metrics.yaml"
    notation_p = root / "symbiont/docs/reference/notation.yaml"

    coverage_data = load_strict_yaml(coverage_p)
    components_data = load_strict_yaml(components_p)
    parameters_data = load_strict_yaml(parameters_p)
    metrics_data = load_strict_yaml(metrics_p)
    notation_data = load_strict_yaml(notation_p)

    # 1. Collect all canonical files for digest
    canonical_files = [
        manifest_p,
        coverage_p,
        components_p,
        parameters_p,
        metrics_p,
        notation_p,
    ]

    # Validate publication
    publication = manifest_data.get("publication")
    if not isinstance(publication, dict):
        raise ValueError("Manifest must contain a 'publication' dictionary.")

    # 2. Build Books and Chapters
    books_data = manifest_data.get("books", [])
    if not isinstance(books_data, list) or not books_data:
        raise ValueError("Manifest must specify a non-empty 'books' list.")

    books: list[BookProjection] = []
    for b_dict in books_data:
        b_id = b_dict.get("id")
        b_title = b_dict.get("title")
        b_desc = b_dict.get("description", "")
        ch_list_data = b_dict.get("chapters", [])
        if not b_id or not b_title:
            raise ValueError(f"Book entry missing id or title: {b_dict}")

        chapters: list[ChapterProjection] = []
        for ch_dict in ch_list_data:
            ch_id = ch_dict.get("id")
            ch_title = ch_dict.get("title")
            ch_source = ch_dict.get("source")
            if not ch_id or not ch_title or not ch_source:
                raise ValueError(f"Chapter in book {b_id} missing id, title or source: {ch_dict}")

            src_path = (root / ch_source).resolve()
            if not src_path.is_file():
                raise FileNotFoundError(f"Chapter source file missing: {src_path}")
            canonical_files.append(src_path)

            chapter_text = src_path.read_text(encoding="utf-8")
            blocks = parse_markdown_blocks(chapter_text)
            chapters.append(
                ChapterProjection(
                    id=ch_id,
                    title=ch_title,
                    source_path=ch_source,
                    blocks=blocks,
                )
            )

        books.append(
            BookProjection(
                id=b_id,
                title=b_title,
                description=b_desc,
                chapters=chapters,
            )
        )

    # 3. Build Components (Closed authority table mapping)
    cov_units = coverage_data.get("units", {})
    comp_dict = components_data.get("components", {})
    catalog_config = manifest_data.get("component_catalog", {})
    ordering = catalog_config.get("ordering", [])

    if len(ordering) != 48:
        raise ValueError(f"Expected exactly 48 components in catalog ordering, got {len(ordering)}")

    # Pre-index parameters by owner and metrics by consumer
    params_by_owner: dict[str, list[dict[str, Any]]] = {}
    for pid, p in parameters_data.get("parameters", {}).items():
        owner = p.get("owner")
        if owner:
            param_copy = dict(p)
            param_copy["id"] = pid
            params_by_owner.setdefault(owner, []).append(param_copy)

    metrics_by_consumer: dict[str, list[dict[str, Any]]] = {}
    for mid, m in metrics_data.get("metrics", {}).items():
        consumer = m.get("consumer")
        if consumer:
            metric_copy = dict(m)
            metric_copy["id"] = mid
            metrics_by_consumer.setdefault(consumer, []).append(metric_copy)

    # Build ComponentSheets according to ordering
    component_sheets: list[ComponentSheet] = []
    seen_syms: set[str] = set()

    for sym_id in ordering:
        if sym_id in seen_syms:
            raise ValueError(f"Duplicate SYM ID in catalog ordering: {sym_id}")
        seen_syms.add(sym_id)

        if sym_id not in comp_dict:
            raise ValueError(
                f"Component {sym_id} declared in manifest ordering not found in components.yaml"
            )

        comp_spec = comp_dict[sym_id]
        cov_uid = comp_spec.get("coverage_unit")
        if not cov_uid or cov_uid not in cov_units:
            raise ValueError(f"Component {sym_id} references missing coverage_unit {cov_uid}")

        cov_entry = cov_units[cov_uid]

        # Verify coverage.yaml master.ids contains sym_id
        master_ids = cov_entry.get("master", {}).get("ids", [])
        if sym_id not in master_ids:
            raise ValueError(
                f"Coverage unit {cov_uid} master.ids {master_ids} does not contain {sym_id}"
            )

        # Extract according to Closed Field Authority Table
        name = comp_spec.get("name", "")
        status = cov_entry.get("status", "")
        owner_domain = cov_entry.get("owner_domain", "")
        participating_domains = list(cov_entry.get("participating_domains", []))

        auth = comp_spec.get("authority", {})
        authority_owns = auth.get("owns", "")
        authority_may_decide = list(auth.get("may_decide", []))
        authority_must_not = list(auth.get("must_not", []))

        state_family = comp_spec.get("state", {}).get("family", "")
        lifecycle = dict(comp_spec.get("lifecycle", {}))

        inputs = list(comp_spec.get("inputs", []))
        outputs = list(comp_spec.get("outputs", []))
        consumers = list(comp_spec.get("consumers", []))

        implementation = list(cov_entry.get("implementation", []))
        tests = list(cov_entry.get("tests", []))
        design = list(cov_entry.get("design", []))
        adrs = list(cov_entry.get("adrs", []))
        depends_on = list(cov_entry.get("depends_on", []))
        canonical_docs = list(cov_entry.get("canonical_docs", []))

        owned_parameters = sorted(
            params_by_owner.get(cov_uid, []),
            key=lambda x: x["id"],
        )
        consumed_metrics = sorted(
            metrics_by_consumer.get(cov_uid, []),
            key=lambda x: x["id"],
        )

        sheet = ComponentSheet(
            sym_id=sym_id,
            coverage_unit=cov_uid,
            name=name,
            status=status,
            owner_domain=owner_domain,
            participating_domains=participating_domains,
            state_family=state_family,
            authority_owns=authority_owns,
            authority_may_decide=authority_may_decide,
            authority_must_not=authority_must_not,
            lifecycle=lifecycle,
            inputs=inputs,
            outputs=outputs,
            consumers=consumers,
            implementation=implementation,
            tests=tests,
            design=design,
            adrs=adrs,
            depends_on=depends_on,
            canonical_docs=canonical_docs,
            parameters=owned_parameters,
            metrics=consumed_metrics,
        )
        component_sheets.append(sheet)

    # 4. Build Parameters
    parameters: list[ParameterEntry] = []
    for pid, p in sorted(parameters_data.get("parameters", {}).items()):
        parameters.append(
            ParameterEntry(
                id=pid,
                symbol=p.get("symbol", ""),
                dimension=p.get("dimension", ""),
                unit=p.get("unit", ""),
                source=p.get("source", ""),
                range=str(p.get("range", "")),
                canonical_default=p.get("canonical_default"),
                owner=p.get("owner", ""),
                interpretation=p.get("interpretation", ""),
                implementation=p.get("implementation"),
            )
        )

    # 5. Build Metrics partitioned by epistemic_class
    metrics_by_class: dict[str, list[MetricEntry]] = {}
    for mid, m in sorted(metrics_data.get("metrics", {}).items()):
        cls = m.get("class", "unclassified")
        entry = MetricEntry(
            id=mid,
            owner_domain=m.get("owner_domain", ""),
            epistemic_class=cls,
            definition=m.get("definition", ""),
            unit=m.get("unit", ""),
            consumer=m.get("consumer"),
            target=m.get("target"),
        )
        metrics_by_class.setdefault(cls, []).append(entry)

    # 6. Build Notation
    notation: list[NotationEntry] = []
    for sym, n in sorted(notation_data.get("symbols", {}).items()):
        notation.append(
            NotationEntry(
                symbol=sym,
                meaning=n.get("meaning", ""),
                scope=n.get("scope", ""),
                owner=n.get("owner", ""),
                observable_by_symbiont=bool(n.get("observable_by_symbiont", False)),
                domain=n.get("domain", ""),
                aliases=list(n.get("aliases", [])),
                forbidden_meanings=list(n.get("forbidden_meanings", [])),
            )
        )

    # 7. Compute Digest and Provenance
    source_digest = compute_source_digest(root, canonical_files)
    commit_sha = get_git_commit(root)
    counts = {
        "canonical_files": len(canonical_files),
        "books": len(books),
        "chapters": sum(len(b.chapters) for b in books),
        "components": len(component_sheets),
        "parameters": len(parameters),
        "metrics": sum(len(ml) for ml in metrics_by_class.values()),
        "notation_symbols": len(notation),
    }

    provenance = ProvenanceMetadata(
        commit_sha=commit_sha,
        source_digest=source_digest,
        canonical_files=[p.relative_to(root).as_posix() for p in sorted(canonical_files)],
        built_at=built_at,
        counts=counts,
    )

    return MasterProjection(
        provenance=provenance,
        publication=publication,
        books=books,
        components=component_sheets,
        parameters=parameters,
        metrics=metrics_by_class,
        notation=notation,
    )
