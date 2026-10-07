"""Canonical reference registry and knowledge graph validation.

Deterministically verifies that the five canonical artifacts:
  - symbiont/docs/coverage.yaml
  - symbiont/docs/reference/components.yaml
  - symbiont/docs/reference/parameters.yaml
  - symbiont/docs/reference/metrics.yaml
  - symbiont/docs/reference/notation.yaml
maintain strict referential integrity, schema constraints, domain topology,
AST symbol anchors, and epistemic boundaries.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]

CANONICAL_DOMAINS = frozenset({"symbiont", "embodiment", "modality", "environment", "lab"})

ALLOWED_KINDS = frozenset(
    {
        "algorithm",
        "component",
        "concept",
        "equation",
        "mechanism",
        "metric",
    }
)

ALLOWED_STATUSES = frozenset({"CURRENT", "DESIGN", "HISTORICAL", "EXPERIMENTAL", "UNRESOLVED"})

ALLOWED_STATE_FAMILIES = frozenset(
    {
        "ephemeral",
        "episode_bound",
        "adaptive_longitudinal",
        "identity_longitudinal",
        "embodiment_local",
        "infrastructure",
    }
)

LIFECYCLE_VOCABULARY = {
    "birth": frozenset({"empty", "initialize"}),
    "checkpoint": frozenset({"not_applicable", "preserve", "reset"}),
    "restart": frozenset({"preserve", "reset"}),
    "reembodiment": frozenset({"invalidate_authority", "preserve", "rebind", "reset"}),
    "reproduction": frozenset(
        {"conditional", "inherit_allowed", "not_applicable", "not_inherited"}
    ),
}

PARAMETER_SOURCES = frozenset({"CODE", "DESIGN", "STUDY", "FORMAL"})

METRIC_CLASSES = frozenset(
    {"organism_internal", "scientific_evaluation", "operational", "historical"}
)

CANONICAL_ID_RE = re.compile(r"^[a-z]+[a-z0-9_-]*\.[a-z0-9_-]+$")


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML Loader that strictly rejects duplicate keys."""

    pass


def _construct_mapping(loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
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
    with path.open("r", encoding="utf-8") as fp:
        return yaml.load(fp, Loader=UniqueKeySafeLoader)


def resolve_symbol_in_ast(path: Path, symbol: str) -> bool:
    """Resolve a symbol (function, class, module constant, Class.attribute) statically via AST."""
    if not path.is_file():
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False

    parts = symbol.split(".")
    if len(parts) == 1:
        name = parts[0]
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == name:
                    return True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return True
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    return True
        return False
    elif len(parts) == 2:
        cls_name, attr_name = parts
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if sub.name == attr_name:
                            return True
                    elif isinstance(sub, ast.Assign):
                        for target in sub.targets:
                            if isinstance(target, ast.Name) and target.id == attr_name:
                                return True
                    elif isinstance(sub, ast.AnnAssign):
                        if isinstance(sub.target, ast.Name) and sub.target.id == attr_name:
                            return True
        return False
    return False


@pytest.fixture(scope="module")
def coverage_data() -> dict[str, Any]:
    return load_strict_yaml(ROOT / "symbiont/docs/coverage.yaml")


@pytest.fixture(scope="module")
def components_data() -> dict[str, Any]:
    return load_strict_yaml(ROOT / "symbiont/docs/reference/components.yaml")


@pytest.fixture(scope="module")
def parameters_data() -> dict[str, Any]:
    return load_strict_yaml(ROOT / "symbiont/docs/reference/parameters.yaml")


@pytest.fixture(scope="module")
def metrics_data() -> dict[str, Any]:
    return load_strict_yaml(ROOT / "symbiont/docs/reference/metrics.yaml")


@pytest.fixture(scope="module")
def notation_data() -> dict[str, Any]:
    return load_strict_yaml(ROOT / "symbiont/docs/reference/notation.yaml")


# =============================================================================
# 1. Strict YAML Loading
# =============================================================================


def test_strict_yaml_loading_no_duplicate_keys() -> None:
    targets = [
        ROOT / "symbiont/docs/coverage.yaml",
        ROOT / "symbiont/docs/reference/components.yaml",
        ROOT / "symbiont/docs/reference/parameters.yaml",
        ROOT / "symbiont/docs/reference/metrics.yaml",
        ROOT / "symbiont/docs/reference/notation.yaml",
    ]
    for target in targets:
        assert target.is_file(), f"Target file missing: {target}"
        data = load_strict_yaml(target)
        assert isinstance(data, dict), f"YAML root in {target} must be a mapping"


# =============================================================================
# 2. coverage.yaml Validation
# =============================================================================


def test_coverage_schema_and_domain_topology(coverage_data: dict[str, Any]) -> None:
    assert coverage_data.get("schema_version") == 2, "coverage.yaml schema_version must be 2"
    units = coverage_data.get("units")
    assert isinstance(units, dict), "coverage.yaml 'units' must be a mapping"
    assert len(units) > 0, "coverage.yaml units mapping cannot be empty"

    errors: list[str] = []
    for uid, unit in units.items():
        if not isinstance(unit, dict):
            errors.append(f"Unit {uid}: definition must be a mapping")
            continue

        kind = unit.get("kind")
        if kind not in ALLOWED_KINDS:
            errors.append(f"Unit {uid}: kind {kind!r} not in {sorted(ALLOWED_KINDS)}")

        status = unit.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"Unit {uid}: status {status!r} not in {sorted(ALLOWED_STATUSES)}")

        owner = unit.get("owner_domain")
        if owner not in CANONICAL_DOMAINS:
            errors.append(f"Unit {uid}: owner_domain {owner!r} not in {sorted(CANONICAL_DOMAINS)}")

        part = unit.get("participating_domains", [])
        if part:
            if not isinstance(part, list):
                errors.append(f"Unit {uid}: participating_domains must be a list")
            else:
                seen_part = set()
                for p in part:
                    if p in seen_part:
                        errors.append(f"Unit {uid}: duplicate participating_domain {p!r}")
                    seen_part.add(p)
                    if p not in CANONICAL_DOMAINS:
                        errors.append(
                            f"Unit {uid}: participating_domain {p!r} not in {sorted(CANONICAL_DOMAINS)}"
                        )
                    if p == owner:
                        errors.append(
                            f"Unit {uid}: owner_domain {owner!r} repeated in participating_domains"
                        )

    assert not errors, "\n".join(errors)


def test_coverage_file_references_resolve(coverage_data: dict[str, Any]) -> None:
    units = coverage_data.get("units", {})
    errors: list[str] = []
    checked_paths = 0

    path_fields = ("canonical_docs", "implementation", "tests", "design", "adrs")

    for uid, unit in units.items():
        for field in path_fields:
            val = unit.get(field)
            if not val:
                continue
            paths = [val] if isinstance(val, str) else val
            for rel_path in paths:
                checked_paths += 1
                target = ROOT / rel_path
                if not target.exists():
                    errors.append(
                        f"Unit {uid} [{unit.get('status')}]: {field} references missing path: {rel_path}"
                    )

    assert checked_paths > 0, "No file references found in coverage.yaml"
    assert not errors, f"{len(errors)} broken file reference(s):\n" + "\n".join(errors)


def test_coverage_dependencies_resolve(coverage_data: dict[str, Any]) -> None:
    units = coverage_data.get("units", {})
    existing_uids = set(units.keys())
    errors: list[str] = []
    checked_deps = 0

    for uid, unit in units.items():
        deps = unit.get("depends_on", [])
        if not deps:
            continue
        dep_list = [deps] if isinstance(deps, str) else deps
        for d in dep_list:
            checked_deps += 1
            if d not in existing_uids:
                errors.append(f"Unit {uid}: depends_on references non-existent unit: {d!r}")

    assert checked_deps > 0, "No depends_on declarations found in coverage.yaml"
    assert not errors, f"{len(errors)} dangling dependencie(s):\n" + "\n".join(errors)


def test_coverage_master_ids_unique_and_complete(coverage_data: dict[str, Any]) -> None:
    units = coverage_data.get("units", {})
    sym_ids: list[str] = []
    errors: list[str] = []

    for uid, unit in units.items():
        master = unit.get("master")
        if isinstance(master, dict):
            ids = master.get("ids", [])
            id_list = [ids] if isinstance(ids, str) else ids
            for sid in id_list:
                if not sid.startswith("SYM-"):
                    errors.append(f"Unit {uid}: master ID {sid!r} does not match 'SYM-*' format")
                sym_ids.append(sid)

    assert not errors, "\n".join(errors)
    assert len(sym_ids) == 48, f"Expected exactly 48 Master IDs, found {len(sym_ids)}"
    assert len(set(sym_ids)) == 48, (
        f"Master IDs contain duplicates: {[x for x in sym_ids if sym_ids.count(x) > 1]}"
    )


# =============================================================================
# 3. components.yaml Validation
# =============================================================================


def test_components_canonical_alignment(
    coverage_data: dict[str, Any], components_data: dict[str, Any]
) -> None:
    components = components_data.get("components", {})
    cov_units = coverage_data.get("units", {})

    assert len(components) == 48, (
        f"Expected 48 components in components.yaml, got {len(components)}"
    )

    # Map coverage components -> SYM ID
    cov_comp_to_sym: dict[str, str] = {}
    for uid, u in cov_units.items():
        if u.get("kind") == "component":
            m = u.get("master", {})
            ids = m.get("ids", []) if isinstance(m, dict) else []
            id_list = [ids] if isinstance(ids, str) else ids
            assert len(id_list) == 1, (
                f"Coverage component {uid} must have exactly 1 SYM ID, found {id_list}"
            )
            cov_comp_to_sym[uid] = id_list[0]

    assert len(cov_comp_to_sym) == 48, (
        f"Expected 48 coverage components, got {len(cov_comp_to_sym)}"
    )

    errors: list[str] = []
    for sym_id, comp in components.items():
        if not sym_id.startswith("SYM-"):
            errors.append(f"Component key {sym_id!r} must start with 'SYM-'")

        cov_unit = comp.get("coverage_unit")
        if not cov_unit or cov_unit not in cov_units:
            errors.append(f"{sym_id}: coverage_unit {cov_unit!r} missing from coverage.yaml")
            continue

        cov_entry = cov_units[cov_unit]
        if cov_entry.get("kind") != "component":
            errors.append(
                f"{sym_id}: coverage_unit {cov_unit!r} has kind {cov_entry.get('kind')!r}, expected 'component'"
            )

        if cov_comp_to_sym.get(cov_unit) != sym_id:
            errors.append(
                f"{sym_id}: bidirectional mismatch (coverage unit {cov_unit} maps to {cov_comp_to_sym.get(cov_unit)} in coverage.yaml)"
            )

        # State ownership coherence
        state = comp.get("state", {})
        comp_owner = state.get("owner")
        cov_owner = cov_entry.get("owner_domain")
        if comp_owner != cov_owner:
            errors.append(
                f"{sym_id}: state.owner {comp_owner!r} != coverage.owner_domain {cov_owner!r}"
            )

        state_family = state.get("family")
        if state_family not in ALLOWED_STATE_FAMILIES:
            errors.append(
                f"{sym_id}: state.family {state_family!r} not in {sorted(ALLOWED_STATE_FAMILIES)}"
            )

        # Authority boundary checks
        authority = comp.get("authority", {})
        if not authority.get("owns"):
            errors.append(f"{sym_id}: authority.owns is missing or empty")
        if not authority.get("may_decide"):
            errors.append(f"{sym_id}: authority.may_decide is missing or empty")
        must_not = authority.get("must_not")
        if not must_not:
            errors.append(f"{sym_id}: authority.must_not is missing or empty")

        # Lifecycle axes checks
        lifecycle = comp.get("lifecycle", {})
        for axis, allowed_values in LIFECYCLE_VOCABULARY.items():
            val = lifecycle.get(axis)
            if val not in allowed_values:
                errors.append(
                    f"{sym_id}: lifecycle.{axis} value {val!r} not in {sorted(allowed_values)}"
                )

        # Canonical consumer resolution
        for consumer in comp.get("consumers", []):
            if CANONICAL_ID_RE.match(consumer):
                if consumer not in cov_units:
                    errors.append(
                        f"{sym_id}: consumer reference {consumer!r} does not resolve in coverage.yaml"
                    )

    assert not errors, f"{len(errors)} component validation error(s):\n" + "\n".join(errors)


# =============================================================================
# 4. parameters.yaml Validation
# =============================================================================


def test_parameters_ast_resolution_and_schema(
    coverage_data: dict[str, Any], parameters_data: dict[str, Any]
) -> None:
    parameters = parameters_data.get("parameters", {})
    cov_units = coverage_data.get("units", {})
    assert len(parameters) > 0, "parameters.yaml cannot be empty"

    errors: list[str] = []
    code_params_checked = 0

    for param_id, param in parameters.items():
        owner = param.get("owner")
        if not owner or owner not in cov_units:
            errors.append(
                f"Parameter {param_id}: owner {owner!r} does not resolve in coverage.yaml"
            )

        source = param.get("source")
        if source not in PARAMETER_SOURCES:
            errors.append(
                f"Parameter {param_id}: source {source!r} not in {sorted(PARAMETER_SOURCES)}"
            )

        for required_field in ("symbol", "dimension", "unit"):
            if not param.get(required_field):
                errors.append(f"Parameter {param_id}: missing required field {required_field!r}")

        if source == "CODE":
            code_params_checked += 1
            impl = param.get("implementation")
            if not isinstance(impl, dict):
                errors.append(f"Parameter {param_id}: source CODE requires implementation mapping")
                continue
            path_str = impl.get("path")
            symbol_str = impl.get("symbol")
            if not path_str or not symbol_str:
                errors.append(f"Parameter {param_id}: implementation requires 'path' and 'symbol'")
                continue

            target_path = ROOT / path_str
            if not target_path.is_file():
                errors.append(
                    f"Parameter {param_id}: implementation path {path_str!r} does not exist"
                )
                continue

            if not resolve_symbol_in_ast(target_path, symbol_str):
                errors.append(
                    f"Parameter {param_id}: AST symbol {symbol_str!r} not found in {path_str}"
                )

    assert code_params_checked > 0, "No CODE parameters found to validate"
    assert not errors, f"{len(errors)} parameter validation error(s):\n" + "\n".join(errors)


# =============================================================================
# 5. metrics.yaml Validation
# =============================================================================


def test_metrics_schema_and_epistemic_invariants(
    coverage_data: dict[str, Any], metrics_data: dict[str, Any]
) -> None:
    metrics = metrics_data.get("metrics", {})
    cov_units = coverage_data.get("units", {})
    assert len(metrics) > 0, "metrics.yaml cannot be empty"

    errors: list[str] = []
    for metric_id, metric in metrics.items():
        m_class = metric.get("class")
        if m_class not in METRIC_CLASSES:
            errors.append(f"Metric {metric_id}: class {m_class!r} not in {sorted(METRIC_CLASSES)}")

        owner = metric.get("owner_domain")
        if owner not in CANONICAL_DOMAINS:
            errors.append(
                f"Metric {metric_id}: owner_domain {owner!r} not in {sorted(CANONICAL_DOMAINS)}"
            )

        # Epistemic invariant: scientific_evaluation is owned by lab
        if m_class == "scientific_evaluation" and owner != "lab":
            errors.append(
                f"Metric {metric_id}: scientific_evaluation must have owner_domain == 'lab', got {owner!r}"
            )

        # Epistemic invariant: historical threat assessment metrics are owned by lab
        if metric_id.startswith("legacy.") and owner != "lab":
            errors.append(
                f"Metric {metric_id}: historical threat assessment metric must have owner_domain == 'lab', got {owner!r}"
            )

        # Consumer reference resolution if shaped as canonical ID
        consumer = metric.get("consumer")
        if consumer and CANONICAL_ID_RE.match(consumer):
            if consumer not in cov_units:
                errors.append(
                    f"Metric {metric_id}: consumer reference {consumer!r} does not resolve in coverage.yaml"
                )

    assert not errors, f"{len(errors)} metric validation error(s):\n" + "\n".join(errors)


# =============================================================================
# 6. notation.yaml Validation
# =============================================================================


def test_notation_symbols_and_invariants(notation_data: dict[str, Any]) -> None:
    symbols = notation_data.get("symbols", {})
    assert len(symbols) > 0, "notation.yaml cannot be empty"

    errors: list[str] = []
    all_aliases: dict[str, str] = {}

    for sym, entry in symbols.items():
        meaning = entry.get("meaning")
        if not meaning or not meaning.strip():
            errors.append(f"Symbol {sym}: meaning is missing or empty")

        scope = entry.get("scope")
        if scope not in {"global", "local", "contextual"}:
            errors.append(f"Symbol {sym}: invalid scope {scope!r}")

        owner = entry.get("owner")
        if not owner or not owner.strip():
            errors.append(f"Symbol {sym}: owner is missing or empty")

        forbidden = entry.get("forbidden_meanings")
        if not forbidden:
            errors.append(f"Symbol {sym}: forbidden_meanings must be a non-empty list")

        aliases = entry.get("aliases", [])
        for alias in aliases:
            if alias == sym:
                continue
            if alias in symbols:
                errors.append(
                    f"Symbol {sym}: alias {alias!r} collides with canonical symbol {alias!r}"
                )
            if alias in all_aliases:
                errors.append(
                    f"Symbol {sym}: alias {alias!r} collides with existing alias declared by {all_aliases[alias]!r}"
                )
            all_aliases[alias] = sym

    # Specific permanent invariants
    if "S_t" in symbols:
        s_forbidden = symbols["S_t"].get("forbidden_meanings", [])
        if "cognitive-state-only" not in s_forbidden:
            errors.append("S_t: must forbid 'cognitive-state-only'")

    if "W_t" in symbols and symbols["W_t"].get("observable_by_symbiont") is not False:
        errors.append("W_t: observable_by_symbiont must be explicitly False")

    if "B_t" in symbols and symbols["B_t"].get("observable_by_symbiont") is not False:
        errors.append("B_t: observable_by_symbiont must be explicitly False")

    if "O_t" in symbols:
        o_forbidden = symbols["O_t"].get("forbidden_meanings", [])
        if "world-ground-truth" not in o_forbidden:
            errors.append("O_t: must forbid 'world-ground-truth'")

    if "H_t" in symbols:
        h_forbidden = symbols["H_t"].get("forbidden_meanings", [])
        if "generative-hypothesis" not in h_forbidden:
            errors.append("H_t: must forbid 'generative-hypothesis'")

    if "e_t" in symbols:
        e_forbidden = symbols["e_t"].get("forbidden_meanings", [])
        if "episodic-memory-trace" not in e_forbidden:
            errors.append("e_t: must forbid 'episodic-memory-trace'")

    if "tau" in symbols:
        tau_forbidden = symbols["tau"].get("forbidden_meanings", [])
        if "discrete-tick-index" not in tau_forbidden:
            errors.append("tau: must forbid 'discrete-tick-index'")

    if "theta" in symbols:
        theta_forbidden = symbols["theta"].get("forbidden_meanings", [])
        if "single-synaptic-weight" not in theta_forbidden:
            errors.append("theta: must forbid 'single-synaptic-weight'")

    assert not errors, f"{len(errors)} notation validation error(s):\n" + "\n".join(errors)


# =============================================================================
# 7. Validator Sentinel Tests (Detect Injected Inconsistencies)
# =============================================================================


def test_sentinel_catches_duplicate_yaml_keys(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("key: 1\nkey: 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate YAML key found"):
        load_strict_yaml(bad_yaml)


def test_sentinel_catches_dangling_depends_on(coverage_data: dict[str, Any]) -> None:
    import copy

    corrupted = copy.deepcopy(coverage_data)
    first_uid = next(iter(corrupted["units"]))
    corrupted["units"][first_uid]["depends_on"] = ["non.existent.unit"]

    with pytest.raises(AssertionError, match="dangling dependencie"):
        test_coverage_dependencies_resolve(corrupted)


def test_sentinel_catches_broken_file_reference(coverage_data: dict[str, Any]) -> None:
    import copy

    corrupted = copy.deepcopy(coverage_data)
    first_uid = next(iter(corrupted["units"]))
    corrupted["units"][first_uid]["implementation"] = "symbiont/src/non_existent_file.py"

    with pytest.raises(AssertionError, match="broken file reference"):
        test_coverage_file_references_resolve(corrupted)


def test_sentinel_catches_invalid_owner_domain(coverage_data: dict[str, Any]) -> None:
    import copy

    corrupted = copy.deepcopy(coverage_data)
    first_uid = next(iter(corrupted["units"]))
    corrupted["units"][first_uid]["owner_domain"] = "invalid_domain"

    with pytest.raises(AssertionError, match="owner_domain 'invalid_domain'"):
        test_coverage_schema_and_domain_topology(corrupted)


def test_sentinel_catches_owner_in_participating_domains(
    coverage_data: dict[str, Any],
) -> None:
    import copy

    corrupted = copy.deepcopy(coverage_data)
    first_uid = next(iter(corrupted["units"]))
    owner = corrupted["units"][first_uid]["owner_domain"]
    corrupted["units"][first_uid]["participating_domains"] = [owner]

    with pytest.raises(AssertionError, match="repeated in participating_domains"):
        test_coverage_schema_and_domain_topology(corrupted)


def test_sentinel_catches_duplicate_sym_mapping(coverage_data: dict[str, Any]) -> None:
    import copy

    corrupted = copy.deepcopy(coverage_data)
    units_with_sym = [
        uid
        for uid, u in corrupted["units"].items()
        if isinstance(u.get("master"), dict) and u["master"].get("ids")
    ]
    # Replace second unit's SYM ID with SYM-GEN to create a duplicate
    corrupted["units"][units_with_sym[1]]["master"]["ids"] = ["SYM-GEN"]

    with pytest.raises(AssertionError, match="contain duplicates"):
        test_coverage_master_ids_unique_and_complete(corrupted)


def test_sentinel_catches_component_coverage_mismatch(
    coverage_data: dict[str, Any], components_data: dict[str, Any]
) -> None:
    import copy

    corrupted = copy.deepcopy(components_data)
    # Point SYM-GEN to non-existent unit
    corrupted["components"]["SYM-GEN"]["coverage_unit"] = "component.missing"

    with pytest.raises(AssertionError, match="missing from coverage.yaml"):
        test_components_canonical_alignment(coverage_data, corrupted)


def test_sentinel_catches_unknown_lifecycle_value(
    coverage_data: dict[str, Any], components_data: dict[str, Any]
) -> None:
    import copy

    corrupted = copy.deepcopy(components_data)
    corrupted["components"]["SYM-GEN"]["lifecycle"]["birth"] = "resurrect_invalid"

    with pytest.raises(AssertionError, match="lifecycle.birth value 'resurrect_invalid'"):
        test_components_canonical_alignment(coverage_data, corrupted)


def test_sentinel_catches_missing_ast_symbol(
    coverage_data: dict[str, Any], parameters_data: dict[str, Any]
) -> None:
    import copy

    corrupted = copy.deepcopy(parameters_data)
    first_param = next(iter(corrupted["parameters"]))
    corrupted["parameters"][first_param]["source"] = "CODE"
    corrupted["parameters"][first_param]["implementation"] = {
        "path": "symbiont/src/symbiont/actuation/competence.py",
        "symbol": "NonExistentClass.non_existent_method",
    }

    with pytest.raises(
        AssertionError, match="AST symbol 'NonExistentClass.non_existent_method' not found"
    ):
        test_parameters_ast_resolution_and_schema(coverage_data, corrupted)


def test_sentinel_catches_invalid_metric_class(
    coverage_data: dict[str, Any], metrics_data: dict[str, Any]
) -> None:
    import copy

    corrupted = copy.deepcopy(metrics_data)
    first_metric = next(iter(corrupted["metrics"]))
    corrupted["metrics"][first_metric]["class"] = "unauthorized_class"

    with pytest.raises(AssertionError, match="class 'unauthorized_class' not in"):
        test_metrics_schema_and_epistemic_invariants(coverage_data, corrupted)


def test_sentinel_catches_notation_alias_collision(notation_data: dict[str, Any]) -> None:
    import copy

    corrupted = copy.deepcopy(notation_data)
    # Add alias colliding with canonical symbol W_t
    corrupted["symbols"]["S_t"]["aliases"] = ["W_t"]

    with pytest.raises(AssertionError, match="collides with canonical symbol 'W_t'"):
        test_notation_symbols_and_invariants(corrupted)
