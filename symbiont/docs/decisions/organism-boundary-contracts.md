# Organism Boundary Contracts

Status: Accepted for implementation in the `symbiont` package.

This record resolves four open contracts from the focused Symbiont audit. It
states policy and ownership; it is not evidence that every implementation
path already conforms. The API change in this same workstream is recorded
separately below.

## D-1 — Process telemetry and interoception

Process telemetry is apparatus evidence, not organism experience. It MUST NOT
become an organism-facing reading, a learned capability, a percept, a memory,
or a checkpointed cognitive fact. Provider identity, host capability metadata,
and discovery topology MUST likewise remain outside organism learning. The
organism may receive only bounded values for its explicitly admitted intrinsic
interoceptive channels; those values must be computed from organism state, not
used to smuggle host measurements across the boundary.

This decision does not prohibit the external composer from using host
capability metadata to decide which providers to attach. It prohibits that
metadata from becoming subject-accessible evidence. Existing `process_telemetry`
paths and capability discovery require behavioral tests against this contract;
the decision alone does not establish conformance.

## D-2 — `Individual` and the reduced seed

`Individual` is the embodiment-study aggregate composed from
`CleanEmbodimentSeed`, `Body`, an `EmbodimentEpisode`, and its history. It is
not an alias for `OrganismRuntime`, nor does the word “Individual” assert the
canonical re-embodiment contract.

`CleanEmbodimentSeed` remains a reduced study subject with
`REDUCED_SEED_TRANSPLANT` continuity. `OrganismRuntime` remains the full runtime
with `CANONICAL_REEMBODIMENT` continuity. Both may exist; callers and
documentation MUST name the selected contract and MUST NOT describe the seed
as interchangeable with the full runtime. In particular, “canonical” refers
to the declared longitudinal contract, not to a universal claim that one
runtime is scientifically superior.

## D-3 — Social evidence ownership

The operational interaction ledgers (`RelationLedger` and
`ResourceEvidenceLedger`) remain distinct from the modeled social/cultural
claims owner (`SocialEvidenceLedger` with `CulturalPolicy`). Their inputs and
decisions are different, so they MUST NOT be merged into a universal social
trust ledger.

`EvidenceTrust` and `SourceEvidenceState` were dormant prototypes, not live
authorities; their unused implementations have been deleted. New runtime
behavior MUST NOT recreate or depend on them without an explicit owner,
evidence lifecycle, decision consumer, and persistence contract. If source
reputation is later required, define those contracts before implementation.

## D-4 — Capsule transport and claims

Knowledge capsules remain signed transport envelopes. Signature verification
establishes payload integrity relative to the included public key; it does not
establish truth, source reliability, consent to believe, or claim validity.
Capsule payloads MUST NOT be automatically ingested as social/cultural claims.
There is no capsule-to-claim adapter until a policy defines payload schema,
provenance preservation, evidence assessment, and the `SocialEvidenceLedger`
entry path.

## Public API consequence — Embodiment boundary (C-1)

`symbiont.api` exposes organism lifecycle, persistence, identity, and lineage
contracts. It does not expose body-transition operations or embodiment
descriptors. Internal organism-owned transition code may remain under
`symbiont.core.embodiment`; its internal location does not make it part of the
public organism facade.

Current external implementations that need such operations must import the
explicit internal transition contract until an owner outside `symbiont`
chooses a new public composition API. This change does not migrate or modify
those external consumers.

## D-5 — Resident budding is clonal Genome v2 inheritance

Resident budding uses an explicit Genome v2 `InheritancePackage`. It carries
the unchanged parent's `Genome`, one structured parent identifier, the next
generation, and only the germline marks admitted by the parent's explicit
`EpigeneticProtocol`. The child receives a new organism identifier and a
newly loaded birth cognitive graph. This is clonal inheritance: it does not
recombine genomes or mutate alleles. `create_child` remains a composition
seam, but the runtime supplies the package rather than leaving inheritance
semantics implicit.

The parent identifier is persisted organism lineage, not proof of a biological
pedigree. The package and lineage are mechanical contracts; they do not claim
that budding is biologically complete or scientifically useful.

## D-6 — Epigenetic state channels

Genome v2 `EpigeneticMark`/`GermlineState` is the only epigenetic channel
allowed to alter gene expression or enter resident inheritance packages.
Acquired-mark capture and transmission require an explicit enabled
`EpigeneticProtocol`; the default protocol transmits no marks. A captured mark
must persist for the configured capture window and is generation-decayed when
transmitted. `EpigeneticPrior` is not part of the current epigenetic contract:
it MUST NOT influence expression, enter inheritance packages, or be described
as inherited epigenetic state. No conversion to Genome v2 marks is permitted.

This integration defines a testable mechanism from expression deviation to
captured mark to offspring birth expression. It does not establish that the
mechanism improves adaptation, represents an empirically validated biological
process, or causes a beneficial transgenerational outcome.

The runtime and public API MUST NOT retain an `EpigeneticPrior` channel as a
compatibility path. Checkpoint schema 14 and current Genome v2 contracts are
the sole supported format; no implicit conversion or fallback is permitted.

## Follow-up implementation matrix

| Item | Disposition | Required work / boundary |
|---|---|---|
| C-1 public Embodiment exports | Implemented | Removed from `symbiont.api`; external consumers are not migrated here. |
| C-2 dormant social trust prototypes | Implemented | Deleted unused prototype modules and removed aggregate exports. |
| C-3 resident budding | Implemented | Explicit `InheritancePackage` carries unchanged Genome v2 plus parent/generation; no recombination or mutation. |
| C-4 organism parent lineage | Implemented | Structured `parent_ids` persist and restore; they do not assert biological pedigree. |
| C-5 epigenetic expression and inheritance | Implemented mechanically | Genome v2 germline is the sole expression/transmission channel; protocol is opt-in. No scientific utility claim follows. |

The explicit germline, parentage, and protocol fields require outer checkpoint
schema 14. Restore remains exact-schema-only and rejects schema 13 and earlier;
there is no automatic migration. No change to `OrganismRuntime` decomposition
(F-10) is included.
