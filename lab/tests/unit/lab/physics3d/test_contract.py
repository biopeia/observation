import inspect
import re

import pytest

from embodiment.physics3d.humanoid import (
    JOINT_AXES,
    JOINT_LIMITS,
    JOINT_SPECS,
    MOTOR_DOF,
    PHYSICAL_RECEPTOR_COUNT,
    TOTAL_RECEPTOR_COUNT,
    HumanoidPhysics,
    build_anthropomorphic_urdf,
    effector_contract_ids,
    interoceptive_receptor_contract_ids,
    mechanical_joint_limits,
    receptor_contract_ids,
)
from embodiment.physics3d.mechanics import (
    BODY_MATERIAL,
    GROUND_MATERIAL,
    MECHANICAL_LIMIT_GUARD,
)
from lab.integration.physics3d.apparatus import (
    OpaqueBodyInteroception,
    physics3d_cognition,
    physics3d_sensory_system,
)
from symbiont.cognition.limits import KernelLimits
from symbiont.core.embodiment.physiology import LivingBodyState


def test_physics3d_contract_uses_only_opaque_port_ids():
    receptors = receptor_contract_ids()
    effectors = effector_contract_ids()

    assert len(receptors) == TOTAL_RECEPTOR_COUNT == 107
    assert len(effectors) == MOTOR_DOF * 2 == 62
    assert receptors == tuple(f"rec.{i}" for i in range(TOTAL_RECEPTOR_COUNT))
    assert effectors == tuple(f"eff.{i}" for i in range(MOTOR_DOF * 2))
    assert interoceptive_receptor_contract_ids() == tuple(
        f"rec.{i}" for i in range(PHYSICAL_RECEPTOR_COUNT, TOTAL_RECEPTOR_COUNT)
    )


def test_v6_body_is_generated_as_hard_limited_urdf():
    import xml.etree.ElementTree as ET

    root = ET.fromstring(build_anthropomorphic_urdf())
    joints = root.findall("joint")

    assert root.attrib["name"] == "symbiont_anthropomorphic_v6"
    assert len(joints) == MOTOR_DOF
    assert [joint.attrib["name"] for joint in joints] == [spec.name for spec in JOINT_SPECS]

    for joint, spec in zip(joints, JOINT_SPECS):
        limit = joint.find("limit")
        dynamics = joint.find("dynamics")
        assert limit is not None
        assert dynamics is not None
        mechanical_lower, mechanical_upper = mechanical_joint_limits(spec)
        assert float(limit.attrib["lower"]) == pytest.approx(mechanical_lower)
        assert float(limit.attrib["upper"]) == pytest.approx(mechanical_upper)
        assert mechanical_lower > spec.lower
        assert mechanical_upper < spec.upper
        assert mechanical_lower - spec.lower <= MECHANICAL_LIMIT_GUARD + 1e-12
        assert spec.upper - mechanical_upper <= MECHANICAL_LIMIT_GUARD + 1e-12
        assert float(limit.attrib["effort"]) == pytest.approx(spec.max_motor_torque)
        assert float(limit.attrib["velocity"]) == pytest.approx(spec.max_velocity)
        # Humanoid passive damping is body-owned and applied explicitly
        # under TORQUE_CONTROL; URDF damping remains zero to avoid duplication.
        assert float(dynamics.attrib["damping"]) == pytest.approx(0.0)


def test_v6_long_limbs_use_axially_symmetric_collision_geometry():
    import xml.etree.ElementTree as ET

    root = ET.fromstring(build_anthropomorphic_urdf())
    links = {link.attrib["name"]: link for link in root.findall("link")}

    for name in (
        "left_upper_arm",
        "left_forearm",
        "right_upper_arm",
        "right_forearm",
        "left_thigh",
        "left_shin",
        "right_thigh",
        "right_shin",
    ):
        collision = links[name].find("collision/geometry/cylinder")
        assert collision is not None
        assert float(collision.attrib["radius"]) > 0.0
        assert float(collision.attrib["length"]) > 0.0

    assert links["torso"].find("collision/geometry/box") is not None
    assert links["pelvis"].find("collision/geometry/box") is not None


def test_mechanical_guard_band_never_expands_anatomical_range():
    for spec in JOINT_SPECS:
        lower, upper = mechanical_joint_limits(spec)
        assert spec.lower < lower < upper < spec.upper


def _humanoid() -> HumanoidPhysics:
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    return HumanoidPhysics(PhysicsScene(timestep=1.0 / 240.0))


def test_effector_contract_rejects_non_positive_motor_count():
    with pytest.raises(ValueError):
        effector_contract_ids(0)


def test_physics3d_optional_dependency_is_lazy():
    import embodiment.physics3d.scene as scene
    import lab.physics3d.runtime as runtime

    # The engine is imported where a scene is built, never at module import.
    for module in (scene, runtime):
        assert not re.search(r"^(import|from) mujoco", inspect.getsource(module), re.M)
    assert "MuJoCo is optional" in inspect.getsource(runtime)


def test_physics3d_cognition_accepts_experiment_local_limits():
    experimental = KernelLimits(max_nodes=256)
    _, _, returned = physics3d_cognition(kernel_limits=experimental)

    assert returned is experimental
    assert returned.max_nodes == 256
    assert KernelLimits().max_nodes == 768


def test_anatomical_labels_do_not_live_in_core_symbiont_surface():
    import symbiont.core.orchestration.clean_embodiment_seed as symbiont

    source = inspect.getsource(symbiont).lower()
    for anatomical_term in ("knee", "elbow", "shoulder", "hip", "thigh", "shin"):
        assert anatomical_term not in source


def test_physics3d_uses_canonical_body_independent_genome():
    genome, _graph, limits = physics3d_cognition()

    assert genome.genome_id == "genome_symbiont_base_v2"
    assert not hasattr(genome, "motor")
    assert genome.development.soft_node_budget == 192
    assert genome.development.soft_edge_budget == 1536
    assert genome.development.sense_node_budget == 128
    assert limits.max_nodes == 768
    assert limits.max_edges == 6144
    assert limits.max_nodes >= genome.development.soft_node_budget
    assert limits.max_edges >= genome.development.soft_edge_budget


def test_physics3d_runtime_does_not_call_parallel_symbiont_step():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime)
    assert "PrivateModelOrganismRuntime" in source
    assert "CleanEmbodimentSeed(" not in source
    assert ".symbiont.step(" not in source


def test_physics3d_grants_body_sized_bounded_sensory_checkpoint_budget():
    sensory = physics3d_sensory_system()

    assert sensory.plasticity_enabled is True
    assert sensory.limits.max_active_sensors == 256
    assert sensory.limits.max_sensor_checkpoint_bytes == 1024 * 1024


def test_physics3d_opts_into_autonomous_validated_predictor_promotion():
    import lab.physics3d.runtime as runtime
    from symbiont.core.organism_profile import CANONICAL

    # Promotion comes from the canonical profile, not from a launcher override.
    assert CANONICAL.auto_promote_predictors is True
    assert "auto_promote_predictors" not in inspect.getsource(runtime)


def test_humanoid_excludes_collision_between_structural_neighbours():
    from embodiment.physics3d.humanoid import ANTHROPOMORPHIC_SPEC

    humanoid = _humanoid()
    model = humanoid.scene.model
    body = {
        name: humanoid._body_id_by_link[index]
        for name, index in humanoid._link_index_by_name.items()
    }
    excluded = {
        frozenset((int(signature) >> 16, int(signature) & 0xFFFF))
        for signature in model.exclude_signature
    }

    assert ANTHROPOMORPHIC_SPEC.structural_neighbour_names
    assert excluded == {
        frozenset((body[left], body[right]))
        for left, right in ANTHROPOMORPHIC_SPEC.structural_neighbour_names
    }


def test_new_physics3d_subjects_do_not_reuse_one_fixed_organism_identity():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime)
    assert 'organism_id="symbiont:3d-subject"' not in source
    assert "secrets.token_hex(8)" in source


def test_unified_viewer_mode_keeps_native_engine_window_disabled():
    import lab.physics3d.cli as cli

    source = inspect.getsource(cli.run)
    assert "gui=(not headless and not show_monitor)" in source
    assert "UnifiedViewerProcess" in source


def test_runtime_has_no_engine_renderer():
    import lab.physics3d.runtime as runtime

    # ADR-0066: nothing renders through the engine; vision casts its own rays
    # and presentation draws exported poses.
    assert not hasattr(runtime.Physics3DEmbodimentRuntime, "render_camera_frame")
    assert "Renderer" not in inspect.getsource(runtime)


def test_unified_viewer_rendering_is_not_in_canonical_runtime_loop():
    import lab.physics3d.cli as cli

    source = inspect.getsource(cli.run)
    assert "render_camera_frame(" not in source
    assert "physical_state=runtime.passive_physical_state()" in source


def test_every_motor_joint_has_one_bounded_mechanical_limit():
    assert set(JOINT_LIMITS) == set(range(MOTOR_DOF))
    for limit in JOINT_LIMITS.values():
        assert limit.lower < limit.upper


def test_humanoid_restore_rejects_malformed_engine_state_without_touching_the_body():
    humanoid = _humanoid()
    state = humanoid.export_physical_state()

    with pytest.raises(ValueError, match="body state has no engine state"):
        humanoid.restore_physical_state({**state, "engine_state": None})
    with pytest.raises(ValueError, match="qpos must contain"):
        humanoid.restore_physical_state(
            {**state, "engine_state": {**state["engine_state"], "qpos": object()}}
        )
    with pytest.raises(ValueError, match="qvel must contain numeric values"):
        humanoid.restore_physical_state(
            {
                **state,
                "engine_state": {
                    **state["engine_state"],
                    "qvel": [None] * len(state["engine_state"]["qvel"]),
                },
            }
        )
    assert humanoid.export_physical_state() == state


def test_body_and_ground_have_nonzero_friction_without_semantic_specialization():
    assert BODY_MATERIAL.lateral_friction > 0.0
    assert GROUND_MATERIAL.lateral_friction > 0.0
    assert BODY_MATERIAL.spinning_friction >= 0.0
    assert GROUND_MATERIAL.spinning_friction >= 0.0
    assert BODY_MATERIAL.restitution < 0.1
    assert GROUND_MATERIAL.restitution < 0.1


def test_runtime_module_source_compiles():
    import pathlib

    import lab.physics3d.runtime as runtime

    source = pathlib.Path(runtime.__file__).read_text(encoding="utf-8")
    compile(source, runtime.__file__, "exec")


def test_runtime_reapplies_motor_command_each_physics_substep():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.step)
    assert "self.apparatus.prepare_physics_substep()" in source
    assert source.index("prepare_physics_substep()") < source.index("self.scene.step()")


def test_physics3d_locomotion_constitution_uses_explicit_metabolism():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.__init__)
    assert "explicit_metabolism=True" in source
    assert "replenishment={kind: 0.0 for kind in metabolic_capacity}" in source
    from symbiont.core.organism_profile import CANONICAL

    assert CANONICAL.interoception_mode == "absent"
    assert "interoception_mode" not in source


def test_l3_receptors_remain_opaque_ordinals():
    receptors = receptor_contract_ids()
    assert receptors == tuple(f"rec.{i}" for i in range(TOTAL_RECEPTOR_COUNT))
    for forbidden in (
        "resource",
        "energy",
        "hunger",
        "integrity",
        "temperature",
        "fatigue",
        "stress",
        "damage",
        "repair",
        "pressure",
    ):
        assert all(forbidden not in receptor for receptor in receptors)


def test_l3_interoceptive_channels_are_independent():
    surface = OpaqueBodyInteroception()
    baseline = LivingBodyState(
        energy_reserve=1.0,
        max_energy=2.0,
        structural_integrity=0.8,
        temperature=0.4,
        fatigue=0.2,
    )
    values = surface.sample(baseline)

    mutations = (
        ("energy_reserve", 0.4),
        ("structural_integrity", 0.3),
        ("temperature", 0.9),
        ("fatigue", 0.7),
    )
    for expected_slot, (field_name, value) in enumerate(mutations):
        changed = LivingBodyState(
            energy_reserve=baseline.energy_reserve,
            max_energy=baseline.max_energy,
            structural_integrity=baseline.structural_integrity,
            temperature=baseline.temperature,
            fatigue=baseline.fatigue,
        )
        setattr(changed, field_name, value)
        sample = surface.sample(changed)
        changed_ids = {
            receptor_id
            for receptor_id in surface.receptor_ids
            if sample[receptor_id] != values[receptor_id]
        }
        assert changed_ids == {surface.receptor_ids[expected_slot]}


def test_l3_interoception_mapping_is_label_invariant_under_permutation():
    state = LivingBodyState(
        energy_reserve=0.6,
        max_energy=2.0,
        structural_integrity=0.7,
        temperature=0.3,
        fatigue=0.9,
    )
    canonical = OpaqueBodyInteroception(source_ordinals_by_slot=(0, 1, 2, 3))
    permuted = OpaqueBodyInteroception(source_ordinals_by_slot=(2, 0, 3, 1))

    canonical_values = tuple(canonical.sample(state).values())
    permuted_values = tuple(permuted.sample(state).values())

    assert permuted_values == (
        canonical_values[2],
        canonical_values[0],
        canonical_values[3],
        canonical_values[1],
    )
    assert state == LivingBodyState(
        energy_reserve=0.6,
        max_energy=2.0,
        structural_integrity=0.7,
        temperature=0.3,
        fatigue=0.9,
    )


def test_l3_local_contact_loads_are_independent_physical_channels():
    body = _humanoid()
    _base, left, right = body._contact_links[:3]
    peak = dict.fromkeys(body._contact_links, 0.0) | {left: 24.0, right: 72.0}
    body._contact_loads = lambda: ({left, right}, peak, 2)

    values = body.sample_receptors()

    # 62 proprioception + 10 global kinematics + 15 contact-presence + 1 field.
    assert values["rec.88"] == pytest.approx(0.0)
    assert values["rec.89"] > 0.0
    assert values["rec.90"] > values["rec.89"]


def test_l3_checkpoint_preserves_only_opaque_ordinal_mapping():
    surface = OpaqueBodyInteroception(source_ordinals_by_slot=(3, 1, 0, 2))
    checkpoint = surface.checkpoint()

    assert checkpoint == {
        "schema_version": 1,
        "source_ordinals_by_slot": [3, 1, 0, 2],
    }
    serialized = repr(checkpoint).lower()
    for forbidden in (
        "reserve",
        "integrity",
        "temperature",
        "fatigue",
        "hunger",
        "damage",
        "repair",
        "stress",
    ):
        assert forbidden not in serialized

    restored = OpaqueBodyInteroception.from_checkpoint(checkpoint)
    assert restored.source_ordinals_by_slot == (3, 1, 0, 2)


def test_resource_ground_truth_is_evaluator_only():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.step)
    assert "resource_distance" in source
    assert "set_opaque_environment_state" in source
    assert "resource_distance=" not in inspect.getsource(
        runtime.Physics3DEmbodimentRuntime.checkpoint
    )


def test_physics3d_applies_all_concurrent_actuations_in_one_tick():
    from types import SimpleNamespace

    from lab.physics3d.runtime import Physics3DEmbodimentRuntime
    from symbiont.actuation.types import Actuation

    applied = {}

    class Apparatus:
        def apply_effectors(self, physical):
            applied.update(physical)

    runtime = Physics3DEmbodimentRuntime.__new__(Physics3DEmbodimentRuntime)
    runtime.apparatus = Apparatus()
    runtime._actuator_to_effector = {
        "a": "motor.0",
        "b": "motor.3",
        "c": "motor.7",
    }
    runtime.organism = SimpleNamespace(
        last_actuations=(
            Actuation("a", 0.9, 0.8),
            Actuation("b", 0.7, 0.6),
            Actuation("c", 0.5, 0.4),
        )
    )

    active = runtime._apply_runtime_actuation()

    assert active == 3
    assert applied == {
        "motor.0": 0.8,
        "motor.3": 0.6,
        "motor.7": 0.4,
    }


def test_physics3d_external_physical_actuation_override_is_bounded_and_complete():
    from types import SimpleNamespace

    import pytest

    from lab.physics3d.runtime import Physics3DEmbodimentRuntime

    applied = {}

    class Apparatus:
        effector_ids = ("eff.0", "eff.1", "eff.2")

        def apply_effectors(self, physical):
            applied.update(physical)

    runtime = Physics3DEmbodimentRuntime.__new__(Physics3DEmbodimentRuntime)
    runtime.apparatus = Apparatus()
    runtime._actuator_to_effector = {}
    runtime.organism = SimpleNamespace(last_actuations=())

    active = runtime._apply_runtime_actuation({"eff.1": 0.65})

    assert active == 1
    assert applied == {"eff.0": 0.0, "eff.1": 0.65, "eff.2": 0.0}
    with pytest.raises(ValueError, match="unknown physical effector"):
        runtime._apply_runtime_actuation({"motor.unknown": 0.2})
    with pytest.raises(ValueError, match="finite in \\[0, 1\\]"):
        runtime._apply_runtime_actuation({"eff.0": float("nan")})


def test_physics3d_resume_projects_solver_penetration_but_direct_restore_stays_strict():
    import inspect

    import lab.physics3d.runtime as runtime
    from embodiment.physics3d.humanoid import HumanoidPhysics

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.__init__)
    assert "strict_anatomical_limits=False" in source

    signature = inspect.signature(HumanoidPhysics.restore_physical_state)
    assert signature.parameters["strict_anatomical_limits"].default is True


def test_physics3d_newborns_use_mode_free_sensorimotor_constitution():
    import lab.integration.physics3d.apparatus as apparatus
    import lab.physics3d.runtime as runtime

    runtime_source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.__init__)
    exclusion_source = inspect.getsource(apparatus.actuator_exclusion_groups)

    assert "motor_exploration_mode" not in runtime_source
    assert '"genome_symbiont_physics3d_v9"' not in runtime_source
    assert "missing canonical genome identity" in runtime_source
    assert "exclusive_actuator_groups=canonical_exclusive_groups" in runtime_source
    assert "physics3d_actuator_surface(" in runtime_source
    assert 'physical_contract=f"count:{len(self.apparatus.effector_ids)}"' in runtime_source
    assert 'f"{contract.body_kind}' not in runtime_source

    # The physical directional-pair mapping belongs to the apparatus adapter,
    # not to the runtime constructor or the genome.
    assert "binding.positive_port" in exclusion_source
    assert "binding.negative_port" in exclusion_source


def test_humanoid_anatomical_axes_match_reference_planes():
    by_name = {spec.name: spec.axis for spec in JOINT_SPECS}

    # Z: axial/yaw rotations.
    for name in (
        "trunk_yaw",
        "left_hip_yaw",
        "right_hip_yaw",
        "left_shoulder_yaw",
        "right_shoulder_yaw",
    ):
        assert by_name[name] == (0.0, 0.0, 1.0)

    # X: sagittal flexion/extension.
    for name in (
        "trunk_pitch",
        "neck_pitch",
        "left_elbow_pitch",
        "right_elbow_pitch",
        "left_hip_pitch",
        "right_hip_pitch",
        "left_knee_pitch",
        "right_knee_pitch",
        "left_ankle_pitch",
        "right_ankle_pitch",
    ):
        assert by_name[name] == (1.0, 0.0, 0.0)

    # Y: frontal-plane roll / ab-adduction.
    for name in (
        "trunk_roll",
        "left_hip_roll",
        "right_hip_roll",
        "left_ankle_roll",
        "right_ankle_roll",
    ):
        assert by_name[name] == (0.0, 1.0, 0.0)


def test_left_and_right_knees_are_mirrored_hinges_not_lateral_rotators():
    by_name = {spec.name: spec for spec in JOINT_SPECS}
    left = by_name["left_knee_pitch"]
    right = by_name["right_knee_pitch"]

    assert left.axis == right.axis == (1.0, 0.0, 0.0)
    assert left.lower == pytest.approx(right.lower)
    assert left.upper == pytest.approx(right.upper)
    assert left.lower == pytest.approx(0.0)


def test_v5_hard_limited_body_exposes_multiple_rotational_axes():
    assert set(JOINT_AXES) == set(JOINT_LIMITS)
    axes = set(JOINT_AXES.values())

    assert (1.0, 0.0, 0.0) in axes
    assert (0.0, 1.0, 0.0) in axes
    assert (0.0, 0.0, 1.0) in axes
    assert JOINT_AXES[0] == (0.0, 0.0, 1.0)
    assert JOINT_AXES[1] == (0.0, 1.0, 0.0)


def test_physics3d_l4_uses_one_physical_energy_pool_for_all_metabolism() -> None:
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.__init__)
    assert "physical_energy_capacity = sum(metabolic_capacity.values())" in source
    assert "living_body_state=living_body_state" in source
    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime.__init__)
    assert "genome_symbiont_physics3d_v9" not in source


def _body_state_with_joint_position(
    humanoid: HumanoidPhysics, joint_ordinal: int, position: float
) -> dict:
    state = humanoid.export_physical_state()
    # Engine coordinates: seven for the free base, then one per joint.
    state["engine_state"]["qpos"][7 + joint_ordinal] = float(position)
    return state


def test_canonical_body_restore_still_rejects_large_anatomical_excursion():
    humanoid = _humanoid()
    shoulder = next(
        index for index, spec in enumerate(JOINT_SPECS) if spec.name == "right_shoulder_pitch"
    )
    payload = _body_state_with_joint_position(
        humanoid, shoulder, JOINT_SPECS[shoulder].upper + 0.25
    )

    with pytest.raises(
        ValueError,
        match="joint state outside hard anatomical limit: right_shoulder_pitch",
    ):
        humanoid.restore_physical_state(payload)


def test_visual_body_restore_projects_large_solver_excursion_without_mutating_source():
    humanoid = _humanoid()
    shoulder = next(
        index for index, spec in enumerate(JOINT_SPECS) if spec.name == "right_shoulder_pitch"
    )
    raw_position = JOINT_SPECS[shoulder].upper + 0.25
    payload = _body_state_with_joint_position(humanoid, shoulder, raw_position)

    humanoid.restore_physical_state(payload, strict_anatomical_limits=False)

    _lower, mechanical_upper = mechanical_joint_limits(JOINT_SPECS[shoulder])
    assert humanoid.joint_states()[shoulder][0] == pytest.approx(mechanical_upper)
    assert payload["engine_state"]["qpos"][7 + shoulder] == pytest.approx(raw_position)


def test_monitor_draws_recorded_poses_without_restoring_a_body():
    import lab.app.physics3d.monitor.viewer as monitor

    source = inspect.getsource(monitor._viewer_main)
    # Display reads the recorded poses and never restores them into a body,
    # so a recorded solver excursion cannot be refused or altered.
    assert "restore_physical_state" not in source
    assert 'physical_state.get("links", ())' in source


def test_passive_postural_tone_is_body_owned_and_bounded():
    from embodiment.physics3d.humanoid import (
        PASSIVE_TONE_TORQUE_CAP_FRACTION,
        _neutral_rest_position,
        _passive_postural_tone,
    )

    for spec in JOINT_SPECS:
        rest = _neutral_rest_position(spec)
        assert spec.lower <= rest <= spec.upper
        at_rest = _passive_postural_tone(
            spec,
            position=rest,
            velocity=0.0,
        )
        assert at_rest == pytest.approx(0.0)

        displaced = _passive_postural_tone(
            spec,
            position=rest + 0.1,
            velocity=0.0,
        )
        assert displaced <= 0.0
        assert abs(displaced) <= (spec.max_motor_torque * PASSIVE_TONE_TORQUE_CAP_FRACTION + 1e-12)


def test_passive_tone_is_elastic_and_damping_is_separate() -> None:
    from embodiment.physics3d.humanoid import _neutral_rest_position, _passive_postural_tone

    ordinal, spec = next(
        item for item in enumerate(JOINT_SPECS) if item[1].name == "left_forearm_roll"
    )
    rest = _neutral_rest_position(spec)

    assert _passive_postural_tone(spec, position=rest, velocity=5.0) == pytest.approx(0.0)
    # Viscous damping is the engine's, per joint, not part of the tone torque.
    humanoid = _humanoid()
    damping = float(humanoid.scene.model.dof_damping[humanoid._joint_dof[ordinal]])
    assert spec.passive_damping > 0.0
    assert damping == pytest.approx(spec.passive_damping)


def test_actuator_work_decomposition_keeps_absolute_effort_distinct_from_net():
    from embodiment.physics3d.mechanics import (
        ActuatorWork,
    )

    work = ActuatorWork(
        positive_j=4.0,
        negative_j=1.5,
        absolute_j=5.5,
        net_j=2.5,
    )
    assert work.absolute_j == work.positive_j + work.negative_j
    assert work.net_j == work.positive_j - work.negative_j


def test_runtime_physics_trace_initializes_joint_payload_before_append():
    import lab.physics3d.runtime as runtime

    source = inspect.getsource(runtime.Physics3DEmbodimentRuntime._physics_trace_sample)
    assert "joints: list[dict[str, object]] = []" in source
    assert source.index("joints: list") < source.index("joints.append")


def test_runtime_settling_fails_closed_instead_of_treating_timeout_as_success():
    from types import SimpleNamespace

    from lab.physics3d.runtime import Physics3DEmbodimentRuntime

    class NeverSettles:
        observer_joint_specs = (SimpleNamespace(name="joint"),)
        position = 0.0

        def apply_effectors(self, _values):
            return None

        def prepare_physics_substep(self):
            self.position += 1.0

        def joint_states(self):
            return [(self.position, 0.25)]

        def base_velocity(self):
            return [1.0, 0.0, 0.0], [0.0, 0.5, 0.0]

        def contact_details(self):
            return []

        def joint_torques(self):
            return [0.0]

    runtime = Physics3DEmbodimentRuntime.__new__(Physics3DEmbodimentRuntime)
    runtime.scene = SimpleNamespace(
        model=SimpleNamespace(opt=SimpleNamespace(timestep=1.0 / 240.0)), step=lambda: None
    )
    runtime.apparatus = NeverSettles()

    with pytest.raises(RuntimeError, match="failed passive settling"):
        runtime._settle_new_body(
            max_steps=3,
            stable_samples=2,
            linear_threshold=0.01,
            angular_threshold=0.01,
            joint_threshold=0.01,
        )

    assert runtime._settling_result.converged is False
    assert runtime._settling_result.steps == 3


def test_engine_rejects_pre_v9_motor_evidence_without_explicit_reembodiment():
    from lab.physics3d.engine import _require_current_motor_evidence

    legacy = {
        "actuation": {
            "sensorimotor": {
                "schema_version": 8,
            },
        },
    }
    with pytest.raises(RuntimeError, match="requires schema 11"):
        _require_current_motor_evidence(
            legacy,
            fresh_body=False,
            new_symbiont=False,
        )

    # Explicit re-embodiment is the honest path: the old learned motor state
    # is not restored as current-body evidence.
    _require_current_motor_evidence(
        legacy,
        fresh_body=True,
        new_symbiont=False,
    )

    for schema in (11,):
        current = {
            "actuation": {
                "sensorimotor": {
                    "schema_version": schema,
                },
            },
        }
        _require_current_motor_evidence(
            current,
            fresh_body=False,
            new_symbiont=False,
        )


def test_engine_reads_motor_evidence_schema_from_the_action_domain():
    """Regression: since ActionDomain owns motor state, the schema lives under
    actuation.action_domain.competence_development; the guard rejected every
    checkpoint written after that move."""
    from lab.physics3d.engine import _require_current_motor_evidence
    from lab.studies.learning.agency_acquisition_body import CausalBody, build_subject

    body = CausalBody(actuator_count=3, seed=1)
    runtime = build_subject(body, organism_id="physics3d-guard")
    for _ in range(3):
        runtime.tick()
        body.advance(runtime.last_actuations)
    _require_current_motor_evidence(runtime.checkpoint(), fresh_body=False, new_symbiont=False)

    for schema in (11,):
        _require_current_motor_evidence(
            {
                "actuation": {
                    "action_domain": {"competence_development": {"schema_version": schema}}
                }
            },
            fresh_body=False,
            new_symbiont=False,
        )
    with pytest.raises(RuntimeError, match="requires schema 11"):
        _require_current_motor_evidence(
            {"actuation": {"action_domain": {"competence_development": {"schema_version": 8}}}},
            fresh_body=False,
            new_symbiont=False,
        )
    _require_current_motor_evidence(
        {"actuation": {"enabled": False}}, fresh_body=False, new_symbiont=False
    )


def test_action_domain_applies_exclusion_before_execution_and_credit():
    from symbiont.core.domains.action import ActionDomain

    source = inspect.getsource(ActionDomain.act)
    constrain_at = source.index("constrain_intents")
    issue_at = source.index("self.issue_command")
    execute_at = source.index("self.execute_command")
    credit_at = source.index("services.schedule_homeostatic_action_credit")

    assert constrain_at < issue_at < execute_at < credit_at


def test_apparatus_projects_directional_pairs_to_opaque_actuator_groups():
    from types import SimpleNamespace

    from lab.integration.physics3d.apparatus import actuator_exclusion_groups

    constitution = SimpleNamespace(
        actuator_ids=("a0", "a1", "a2", "a3"),
    )
    apparatus = SimpleNamespace(
        effector_ids=("e0", "e1", "e2", "e3"),
        motor_bindings=(
            SimpleNamespace(positive_port="e2", negative_port="e0"),
            SimpleNamespace(positive_port="e3", negative_port="e1"),
        ),
    )

    assert actuator_exclusion_groups(constitution, apparatus) == (
        ("a2", "a0"),
        ("a3", "a1"),
    )


def test_apparatus_motor_unit_contract_requires_complete_disjoint_coverage():
    from types import SimpleNamespace

    from lab.integration.physics3d.apparatus import actuator_exclusion_groups

    constitution = SimpleNamespace(
        actuator_ids=("a0", "a1", "a2", "a3"),
    )
    incomplete = SimpleNamespace(
        effector_ids=("e0", "e1", "e2", "e3"),
        motor_bindings=(SimpleNamespace(positive_port="e0", negative_port="e1"),),
    )
    with pytest.raises(ValueError, match="complete actuator constitution"):
        actuator_exclusion_groups(constitution, incomplete)

    overlapping = SimpleNamespace(
        effector_ids=("e0", "e1", "e2", "e3"),
        motor_bindings=(
            SimpleNamespace(positive_port="e0", negative_port="e1"),
            SimpleNamespace(positive_port="e1", negative_port="e2"),
        ),
    )
    with pytest.raises(ValueError, match="disjoint directional pairs"):
        actuator_exclusion_groups(constitution, overlapping)


def test_actuator_work_metabolic_conversion_is_proportional_without_cap():
    from lab.physics3d.runtime import metabolic_cost_from_actuator_work

    assert metabolic_cost_from_actuator_work(100.0, 0.1) == pytest.approx(10.0)
    assert metabolic_cost_from_actuator_work(1000.0, 0.001) == pytest.approx(1.0)

    for work, rate in (
        (-1.0, 0.1),
        (1.0, -0.1),
        (float("inf"), 0.1),
        (1.0, float("nan")),
    ):
        with pytest.raises(ValueError):
            metabolic_cost_from_actuator_work(work, rate)


def test_articulated_body_reports_signed_and_absolute_actuator_work():
    from embodiment.physics3d.articulated import ArticulatedPhysics

    body = ArticulatedPhysics.__new__(ArticulatedPhysics)
    body.joint_states = lambda: [(0.0, 2.0), (0.0, -3.0)]
    body._applied_torque_by_joint = {0: 4.0, 1: 5.0}

    work = body.actuator_work_step(0.5)

    assert work.positive_j == pytest.approx(4.0)
    assert work.negative_j == pytest.approx(7.5)
    assert work.absolute_j == pytest.approx(11.5)
    assert work.net_j == pytest.approx(-3.5)
    assert body.mechanical_work_step(0.5) == pytest.approx(11.5)
