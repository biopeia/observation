# Embodiment BodyPose Observation Mapping v1

Observation maps Embodiment's approved BodyPose v1 owner projection into one
passive `SemanticObservation` claim. The mapping preserves Embodiment as the
primary authority and identifies the body, embodiment episode, and morphology
revision as separate typed subject identities.

The claim carries position in metres and orientation as the declared unit
quaternion, with both the reference and body frames explicit. The family does
not declare Embodiment domain time; World causal tick is retained only as
correlation context. Source-state digest and, when present, physical-step,
Environment, and solver revisions are lineage/configuration references.

The adapter validates the projection's shape and internal correlation. It
cannot authenticate that an arbitrary directly constructed value originated at
the Embodiment owner boundary, nor does the source-state digest establish
durability. Most importantly, mapping a projection does not prove that its
World cut committed. The World publication boundary must independently verify
the committed cut and reject stale, mismatched, or uncommitted projections
before publishing them.

This mapping defines no wire format, transport, storage, global snapshot, or
causal replay guarantee. The tests cover mapping and local validation only;
they do not complete the end-to-end publication acceptance criterion.
