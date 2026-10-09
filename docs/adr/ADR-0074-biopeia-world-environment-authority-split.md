# ADR-0074 — Biopeia World and Environment Authority Split

## Status

- **Status:** Accepted
- **Owner acceptance:** 2026-10-09, Architecture Owner
- **Scope:** Biopeia Architecture v1 TARGET authority boundaries and migration direction. This is a derived decision; it does not reopen Pass 15 or alter AD-0021…AD-0036 except for the explicitly superseded historical rule identified below. It also clarifies Constitution §1 item 7 for Biopeia TARGET while preserving its historical Symbiont CURRENT boundary.
- **Supersedes:** Constitution §1 item 3 and ADR-0060 only to the extent stated in this ADR. ADR-0060 remains valid evidence of the historical Symbiont CURRENT architecture.

## Context

Biopeia migration clarified that causal coordination and environmental state
ownership are separate responsibilities. The historical Symbiont architecture
assigned external laws, opportunities, and dynamics to `symbiont_world` and
used a hex topology. That remains a description of the historical CURRENT
system, but is not the Biopeia TARGET authority model.

This decision records an explicit owner resolution of that conflict. It does
not assert that the existing implementation has already been moved, replaced,
or brought into conformance.

## Decision

### 1. World owns shared causality

Biopeia TARGET `World` is the primary causal runtime and composition authority.
It owns:

- World identity and causal time/ticks;
- active-presence and causal-participant/owner registries;
- cross-owner interaction coordination and causal ordering;
- lifecycle choreography and causal transaction boundaries;
- commit and recovery coordination.

World executes and commits shared causal evolution. It does not deep-own the
state of its participants.

### 2. Environment owns external environmental truth

Biopeia TARGET `Environment` owns external environmental state and its
semantics, including spatial environment, terrain/geometry, resources,
environmental fields, hazards, medium properties, environmental laws and
dynamics, ground truth, and Environment genesis.

`World` and `Environment` are distinct authorities:

```text
causal coordination != environmental state ownership
```

Environment does not acquire World identity, causal tick, participant roster,
commit, or recovery authority. World does not acquire Environment state or law
ownership.

### 3. Other causal authorities and numerical substrate

- **Embodiment** owns morphology, body identity/episode, and authoritative
  somatic state.
- **Organism** owns its longitudinal private state and cognition.
- A physical solver is a numerical execution capability, not a semantic
  authority or owner. Environment and Embodiment project their state, validate
  and adopt applicable candidate results, and World commits the resulting
  causal cut.
- MuJoCo is already authorized by ADR-0066 as the initial Physics3D engine
  behind an adapter/projection boundary. This ADR does not make it a universal
  physical engine mandate.

Neither World nor Environment may own Organism cognition or Embodiment somatic
truth. The Organism does not receive experimental ground truth, and external
semantic labels are not injected into cognition.

This decision does not relax the existing import restrictions in Constitution
§1 items 4–6. Cross-authority coordination must preserve those boundaries; the
specific composition/dependency mechanism is not frozen here.

### 4. Historical rule and ADR-0060 disposition

The historical rule that `symbiont_world` owns external laws, opportunities,
and dynamics is **superseded for Biopeia TARGET only**. It remains valid when
describing the historical Symbiont CURRENT architecture.

ADR-0060 is **partially superseded**. Its CURRENT inventory and evidence about
`symbiont_world`, the hex topology, the World adapter, Physics3D, historical
environment families, and their consumers are retained. Its TARGET claims
that the hex kernel is the unique constitutional World implementation, that
external laws/topology/dynamics belong to World, or that no canonical
World/Environment authority split exists no longer govern Biopeia TARGET.
Non-conflicting boundaries remain in force, including separation from
Organism cognition and the prohibition on silently adding environment
semantics to Organism.

### 5. Hex and physical 3D direction

The hex world is not the canonical spatial topology for Biopeia TARGET's
embodied physical path. Its existing implementation is historical evidence,
not a migration input. Legacy code must not be moved, wrapped, or retained in a
TARGET repository merely to preserve historical behavior or backward
compatibility. A discrete or hex experiment remains permissible only when its
scientific purpose is independently justified; that does not authorize
migrating the legacy implementation or preserving its API. Any independently
needed TARGET capability must be justified and implemented on its own terms.
Each source component must be disposed by meaning (`MOVE`, `SPLIT`, `REWRITE`,
`DROP`, or provisional `DEFER`); no mechanical `HexCoord` to `Vec3` or topology
conversion is implied.

The owner-approved canonical embodied direction is toward a continuous physical
3D Environment. This is an architectural direction, not a claim that every
Environment or experiment must use a continuous spatial representation;
discrete and non-spatial fixtures remain valid where the experiment requires
them.

### 6. Environment genesis and procedural generation

Procedural generation is an owner-approved Environment capability, not the
only genesis strategy. Explicit/static environments and scientific fixtures
remain valid. When procedural generation is used, it must be reproducible from
sufficient explicit inputs and must not treat host wall-clock randomness as
implicit causal authority. This ADR does not freeze a generator algorithm,
configuration schema, spatial partitioning, coordinate representation,
chunk/region model, or finite/unbounded extent.

Environmental properties are objective causal conditions, not preassigned
cognitive affordances or goals. Do not inject labels such as `food`, `danger`,
`shelter`, `goal`, or `reward` into Organism cognition.

### 7. Composition and planes

The target causal plane consists of World coordinating Organism, Embodiment,
Environment, and applicable Modality/physical capabilities while each domain
retains ownership of its own state. Observation remains a passive projection.
Lab is the scientific apparatus and may configure, start, or explicitly
intervene in a World, but is not required for ordinary causal runtime.

## Consequences

- Target authority is assigned by semantic responsibility, not historical
  repository name or source location.
- Legacy, junk, or disposable code is not migrated, adapted, or wrapped merely
  to retain historical behavior or backward compatibility. No old API
  compatibility is implied. Any reused capability requires independent
  semantic justification for Biopeia TARGET; source disposition and historical
  evidence remain explicit.
- Migration documentation must distinguish CURRENT implementation from TARGET
  authority and must not imply that this ADR alone completes code migration.
- Concrete spatial indices, generator details, and a universal coordinate
  representation remain open until implementation evidence requires them.

## Alternatives considered

- **Keep World as owner of environmental laws and state.** Rejected for
  Biopeia TARGET because it conflates causal coordination with environmental
  truth ownership.
- **Make Environment subordinate to World as a projection.** Rejected because
  Environment is an independent semantic owner of environmental truth.
- **Mechanically convert the hex topology to 3D.** Rejected because historical
  location and representation do not establish target meaning or reusable
  semantics.
- **Require procedural generation for every Environment.** Rejected because
  explicit/static environments and scientific fixtures are valid genesis
  strategies.

## References

- [ADR-0060 — Responsibility and Naming of World and Environment Families](ADR-0060-world-responsibility-and-naming.md) (partially superseded)
- [ADR-0066 — MuJoCo as the Single Physics3D Engine and Engine-independent Visual Sampling](ADR-0066-mujoco-physics-engine-and-engine-independent-vision.md)
- [ADR-0073 — Biopeia Migration Causal and Physical Contracts](ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
- [World Responsibility Map v1](../design/world/world-responsibility-map-v1.md) (CURRENT inventory and TARGET disposition)
