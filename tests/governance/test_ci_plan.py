from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from governance import ci_plan
from governance.classify import ChangeClass


def _plan(
    monkeypatch,
    classification: ChangeClass,
    paths: list[str],
    *,
    sections: tuple[str, ...],
    lanes: set[str],
):
    calls = iter(["\n".join(paths), "diff"])
    monkeypatch.setattr(ci_plan, "_git", lambda *args: next(calls))
    monkeypatch.setattr(
        ci_plan,
        "assess",
        lambda *args, **kwargs: SimpleNamespace(
            classification=classification,
            reasons=("test",),
        ),
    )
    monkeypatch.setattr(ci_plan, "_selected_matrix_sections", lambda *args: sections)
    monkeypatch.setattr(ci_plan, "_lanes_for_sections", lambda *args: set(lanes))
    monkeypatch.setattr(ci_plan, "_budget_for", lambda *args: 120)
    monkeypatch.setattr(ci_plan, "_audit_plan", lambda *args: ())
    return ci_plan.build_plan("base", "head")


def test_ordinary_docs_change_runs_docs_lane_only(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.ORDINARY,
        ["symbiont/docs/explanation/readme.md"],
        sections=("docs",),
        lanes={"docs"},
    )

    assert plan.docs
    assert not plan.code_quality
    assert not plan.software_core
    assert not plan.architecture_integrity
    assert not plan.python_compat
    assert not plan.host_portability
    assert not plan.physics3d
    assert not plan.modeling
    assert not plan.protocol_mechanics


def test_scientific_class_does_not_expand_unrelated_lanes(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["symbiont/src/symbiont/core/example.py"],
        sections=("subject",),
        lanes={"software_core", "architecture_integrity", "runtime_contracts"},
    )

    assert plan.software_core
    assert plan.architecture_integrity
    assert plan.runtime_contracts
    assert not plan.python_compat
    assert not plan.protocol_mechanics
    assert not plan.host_portability
    assert not plan.physics3d
    assert not plan.modeling


def test_world_change_uses_targeted_world_lane(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["environment/src/environment/example.py"],
        sections=("world",),
        lanes={"world", "architecture_integrity", "physics3d"},
    )

    assert plan.world
    assert not plan.software_core
    assert plan.architecture_integrity
    assert plan.physics3d


def test_observatory_change_does_not_imply_architecture(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.ORDINARY,
        ["lab/src/lab/observatory/server.py"],
        sections=("observatory",),
        lanes={"observatory"},
    )

    assert plan.observatory
    assert not plan.architecture_integrity
    assert not plan.performance
    assert not plan.physics3d
    assert not plan.modeling
    assert not plan.python_compat


def test_experiment_change_selects_only_declared_scientific_mechanics(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["lab/src/lab/studies/example.py"],
        sections=("experiment_protocol",),
        lanes={"experiment_mechanics", "protocol_mechanics", "architecture_integrity"},
    )

    assert plan.experiment_mechanics
    assert plan.architecture_integrity
    assert plan.protocol_mechanics
    assert not plan.runtime_contracts
    assert not plan.python_compat


def test_physics3d_change_adds_physics_lane_without_host_matrix(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["lab/src/lab/physics3d/engine.py"],
        sections=("lab", "lab_physics3d"),
        lanes={"software_core", "architecture_integrity", "physics3d"},
    )

    assert plan.physics3d
    assert not plan.modeling
    assert not plan.host_portability
    assert not plan.performance


def test_modeling_change_selects_modeling_not_physics(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["lab/src/lab/modeling/trainer.py"],
        sections=("lab", "modeling"),
        lanes={"software_core", "architecture_integrity", "modeling"},
    )

    assert plan.modeling
    assert not plan.physics3d
    assert not plan.performance


def test_host_change_adds_portability_lanes_by_impact(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["symbiont/src/symbiont/host/providers/example.py"],
        sections=("subject", "subject_host"),
        lanes={
            "software_core",
            "architecture_integrity",
            "runtime_contracts",
            "host_portability",
            "alpine",
        },
    )

    assert plan.host_portability
    assert plan.alpine
    assert not plan.performance
    assert not plan.physics3d
    assert not plan.modeling


def test_control_plane_breadth_is_explicit_not_constitutional_magic(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.CONSTITUTIONAL,
        [".github/workflows/ci.yml"],
        sections=("ci_control",),
        lanes={
            "governance",
            "architecture_integrity",
            "runtime_contracts",
            "experiment_mechanics",
            "canonical_full",
            "python_compat",
            "host_portability",
            "alpine",
            "protocol_mechanics",
            "physics3d",
            "modeling",
        },
    )

    assert plan.governance
    assert plan.canonical_full
    assert plan.architecture_integrity
    assert plan.runtime_contracts
    assert plan.experiment_mechanics
    assert plan.physics3d
    assert plan.modeling
    assert plan.python_compat
    assert plan.host_portability
    assert plan.alpine
    assert plan.protocol_mechanics
    assert not plan.observatory


def test_observed_launchers_select_the_observatory_lane() -> None:
    import tomllib

    matrix = tomllib.loads(
        (ROOT / "docs" / "governance" / "validation-matrix.toml").read_text(encoding="utf-8")
    )
    launchers = sorted((ROOT / "lab" / "src" / "lab" / "cli").glob("observed_*.py"))

    assert launchers
    for launcher in launchers:
        path = launcher.relative_to(ROOT).as_posix()
        assert any(ci_plan._matches(path, pattern) for pattern in matrix["observatory"]["paths"]), (
            path
        )
    assert "observatory" in matrix["observatory"]["ci_lanes"]


def test_constitutional_markdown_only_change_skips_behavioral_lanes(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.CONSTITUTIONAL,
        [".agents/skills/architecture-decision/SKILL.md"],
        sections=("governance",),
        lanes={"governance"},
    )

    assert plan.governance
    assert plan.docs
    assert not plan.code_quality
    assert not plan.software_core
    assert not plan.architecture_integrity
    assert not plan.canonical_full
    assert not plan.python_compat


def test_scientific_markdown_only_change_skips_behavioral_lanes(monkeypatch) -> None:
    plan = _plan(
        monkeypatch,
        ChangeClass.SCIENTIFIC,
        ["docs/design/core/example.md"],
        sections=("docs", "scientific_design"),
        lanes={"docs"},
    )

    assert plan.docs
    assert not plan.software_core
    assert not plan.architecture_integrity
    assert not plan.runtime_contracts
    assert not plan.experiment_mechanics
    assert not plan.physics3d
    assert not plan.modeling
    assert not plan.python_compat
    assert not plan.protocol_mechanics


def test_adversarial_review_rejects_uncovered_path(monkeypatch) -> None:
    monkeypatch.setattr(ci_plan, "_load_matrix_at", lambda _base: {"schema_version": 4})
    plan = ci_plan.CIPlan(
        classification="ORDINARY",
        code_quality=True,
        docs=False,
        governance=False,
        software_core=True,
        world=False,
        observatory=False,
        architecture_integrity=False,
        runtime_contracts=False,
        experiment_mechanics=False,
        canonical_full=False,
        physics3d=False,
        modeling=False,
        python_compat=False,
        host_portability=False,
        alpine=False,
        protocol_mechanics=False,
        performance=False,
        budget_seconds=120,
        changed_paths=("unknown/new_surface.py",),
        matrix_sections=(),
        selected_lanes=("software_core",),
        reasons=(),
    )

    findings = ci_plan._audit_plan("base", plan)
    assert any("uncovered changed paths" in finding for finding in findings)
