# Embodiment Physical Body Pose Semantic Contract v1

**Status:** Accepted with refinements by Embodiment semantic owner (2026-10-07).  
**Scope:** Backend-neutral semantic contract for `embodiment.body_pose`.  
**Not in scope:** Wire schema, envelope, transport, API, event taxonomy, implementation or publication mechanism.

Embodiment accepted the semantic meaning and conformance boundary below, subject to the refinements recorded here. This acceptance does not approve a record schema, concrete serialization fields, publication cadence, API, events, snapshots, transport, implementation or cutover. The source-level Physics3D conformance assessment found conformance not demonstrated; Body Pose is not record-ready. See [Observation Architecture v1 — Target Design §9.1.1](observation-architecture-target-design-v1.md#912-physics3d-body-pose-conformance-assessment--2026-10-07).

## 1. Semantic claim

Body Pose expresses:

> The physical position and orientation of an identified physical Body or identified physical Body part, sampled at an identified instant in the Embodiment physical state, relative to an explicitly identified physical reference frame.

The claim is Embodiment-authoritative. The apparatus/backend supplies the sample but does not define its public semantics.

## 2. Subject

A Body Pose observation concerns exactly one of:

```text
Physical Body
Physical Body Part
```

A Body-part pose is always scoped to a specific Body. A part identifier has no meaning independently of the Body/morphology contract under which it is defined.

Body identity, part identity and compatible physical-contract revision are independent identity/context dimensions. Do not concatenate them into a synthetic identifier. A part identifier is interpreted within its Body instance and applicable physical contract.

Array position, backend object index, MuJoCo body index or serialization order must never constitute semantic part identity.

## 3. Position

`position` means the location of the origin of the subject's declared physical frame relative to the origin of the declared reference frame.

Canonical dimensional quantity:

```text
length
```

Canonical observation unit:

```text
metre (m)
```

Backends using another internal unit must convert before claiming conformance. A raw backend coordinate whose scale is not known to correspond to metres is not conformant Body Pose.

## 4. Reference frame

Every Body Pose claim must have an explicit reference frame. The contract does not assume a universal Environment/world coordinate system.

The backend-neutral concept is an **Embodiment Physical Reference Frame**; it need not be named a “world frame.” For the normal external Body Pose representation in v1, use the active Embodiment physical reference frame representing the apparatus/world space in which the Body is instantiated. A concrete implementation may use another explicitly defined physical frame if its semantics and transformations are defined. It may be associated with an Environment frame, but equality must not be inferred:

```text
EmbodimentPhysicalWorldFrame
        ≠ automatically
EnvironmentWorldFrame
```

An explicit transformation or identity assertion is required before claims expressed in the two frames are joined. The physical contract must define the origin and positive X/Y directions for each reference-frame kind used.

## 5. Axes and handedness

A conforming physical-frame definition must explicitly define handedness, positive X, positive Y, positive Z and up direction.

Canonical v1 observation convention:

```text
right-handed Cartesian coordinates
+Z = up
```

This constrains canonical observation semantics, not backend internals. A backend may convert from another unit, handedness or axis convention. The concrete frame contract must define +X and +Y; neither UI orientation nor simulator defaults establish them.

## 6. Orientation

Orientation means the rotation from the subject's local physical frame into the declared reference frame.

Canonical representation:

```text
unit quaternion
component order: (x, y, z, w)
```

Here `w` is the scalar component. A conforming value must satisfy a normalization tolerance defined by the physical semantic contract. Quaternion sign equivalence applies:

```text
q ≡ -q
```

because both represent the same physical orientation. Consumers must not interpret a sign flip alone as physical rotation. Euler angles are not the canonical Body Pose orientation representation. A backend may internally use another representation or component order provided it converts explicitly.

Invalid, unavailable and non-finite quaternion behavior must be defined before a record is ready.

## 7. Body-local frame

Each Body or Body part exposed through Body Pose must have a declared local physical frame. For each subject, its frame definition belongs to the versioned physical Body contract.

The definition must make it impossible for one backend to mean `pelvis origin` while another silently means `center of mass` under the same semantic part identity. Center of mass is not Body Pose unless explicitly defined as a separate quantity.

## 8. Body and Body-part pose

The family may contain two subject granularities:

```text
Body pose
Part pose
```

They share quantity semantics, units, reference-frame rules, orientation convention and sampling semantics. They differ in the identified physical subject and its local-frame definition. This does not require them to be emitted in one record or one sample.

## 9. Sampling semantics

Body Pose is a **point state sample**: physical pose state evaluated at a specific Embodiment sampling instant.

It is not an interval average, command, intended pose, predicted pose, interpolated presentation pose unless explicitly classified as such, or trajectory. Every conforming sample must be bound to an Embodiment-domain sampling reference sufficient to establish when the physical state was valid.

## 10. Domain time

The semantic contract distinguishes:

```text
Embodiment physical sample time
Organism cycle
transport sequence
presentation frame
```

They are not interchangeable. The contract does not require every backend to possess a simulation step, simulation time or physics substep. These are valid implementation references for simulated Embodiments, not universal requirements. For Physics3D, simulation step/time may satisfy the contract once their relationship to the sampled pose is demonstrated. Association with an organism cycle may additionally be provided when evidenced, but does not replace the physical sample reference.

```text
organism_tick ≠ physical sample clock
```

unless an explicit relation states otherwise.

## 11. Acquisition mode

A conforming implementation must identify whether a Body Pose value is sampled physical state or derived/interpolated physical state if that distinction is material to interpretation. The v1 canonical candidate is sampled physical state. Presentation interpolation must not silently become the source Body Pose claim.

## 12. Identity

A conforming Body Pose claim requires:

### Body identity

A stable identifier for the lifetime of the physical Body. Re-embodiment creates a new Body identity. Same-Body restore preserves Body identity.

### Part identity

A stable identifier within the applicable physical Body contract and Body instance. Compatibility across contract revisions must be declared explicitly; absent such a declaration, same-name parts are not presumed semantically compatible.

### Embodiment episode

The Embodiment episode may be supplied as contextual identity where necessary to associate the Body with the current Symbiont coupling. It does not replace Body identity.

No Lab alias or runtime fallback may silently replace an unresolved Body identity.

Body identity, part identity and physical-contract revision remain independent dimensions. Concrete identifier kinds, issuer/asserter and explicit links remain subject to the target identity model.

## 13. Contract revision

Body Pose must reference a versioned **physical semantic contract**. That revision establishes compatibility for at least quantity meaning, units, coordinate-system conventions, orientation convention, local Body/part frames, part identities and sampling semantics.

A checkpoint/state schema version does not satisfy this requirement. An incompatible change to any semantic element above requires a new physical semantic-contract revision.

## 14. Availability

The semantic model must distinguish, where relevant:

```text
available
unsupported
not_applicable
not_observed
temporarily_unavailable
stale
```

These are conceptual states, not proposed wire enum names. Missing data must not ambiguously represent all of them. For example: a part absent from a Body contract is `not_applicable`; a backend unable to provide an otherwise valid part is `unsupported`; a missing current sample is `temporarily_unavailable`; and a prior sample beyond its freshness limit is `stale`.

Exact representation and freshness criteria remain record-design work.

## 15. Completeness

A Body Pose claim must not silently combine values from different physical sampling instants. If a composed Body view contains base and multiple part poses acquired at different times, it must preserve those sampling references or state explicitly that it is asynchronous/partial. A common container does not establish atomicity.

## 16. Epistemic nature

For a simulator-backed Embodiment, the classification is:

```text
semantic authority = Embodiment
    epistemic nature   = simulated apparatus physical-state sample
measurement source = concrete backend/apparatus
```

The observation describes the state represented by that Embodiment implementation. It must not be presented as independently measured external-world ground truth.

## 17. Explicit exclusions

Body Pose does not include:

- Body Schema;
- Self Model;
- Environment entity pose;
- intended/commanded pose;
- predicted pose;
- joint kinematics;
- linear/angular velocity;
- center of mass;
- mass;
- contacts;
- force;
- torque;
- actuator effort;
- mechanical work;
- resource position.

Each requires its own admitted semantic family or explicit composition.

## 18. Conformance rule

A backend is conformant with Physical Body Pose v1 only when it can demonstrate for every published Body Pose quantity:

1. compatible subject identity;
2. compatible Body/part local-frame definition;
3. position converted to metres;
4. explicit compatible reference frame;
5. right-handed Cartesian convention with +Z up;
6. orientation represented or losslessly converted to canonical `xyzw` unit-quaternion semantics, within the defined normalization tolerance;
7. explicit physical sampling reference;
8. distinction between sampled and presentation/interpolated state;
9. semantic-contract revision association;
10. explicit availability behavior.

Undefined or non-conforming quantities must not be published as `embodiment.body_pose`.

## 19. Decision boundary

This accepted contract establishes semantic readiness inputs for Body Pose and permits a Physics3D conformance assessment. It does not approve a record schema, field layout, publication cadence, event, snapshot, endpoint, transport or implementation.

### Still requiring explicit disposition or later specification

- concrete Embodiment physical-frame identity, origin and +X/+Y interpretation;
- local-frame definitions for Body and parts;
- quaternion normalization tolerance and invalid/non-finite behavior;
- canonical Body/part identifier kinds, issuer/asserter and explicit revision compatibility;
- selected physical sampling path and typed clock;
- availability representation and any freshness policy.

These are contract/conformance and record-readiness details, not a reversal of the accepted semantic-owner disposition.
