# Embodiment Render Link Pose Carriage v1

Observation carries the Embodiment-owned `embodiment.render_link_pose_candidate/v1`
payload in the carrier family `embodiment.render_link_pose@v1`. The carrier
preserves the candidate payload, its candidate digest, and the exact World
committed-cut and Embodiment checkpoint-reference metadata supplied by World.
The family and contract identifiers version this Observation carrier; they do
not redefine the payload's meaning or transfer its semantic authority.

The adapter is structural and passive. It does not import World or Embodiment,
verify the World receipt, join geometry to poses, infer missing values, or
reconstruct state. World performs the transient current-cut association before
publication. The carried association is not a durable record or independent
cryptographic proof of physical state. Consumers must not treat matching tick
numbers alone as proof of coherence.

The local read bridge validates the closed candidate, source identities,
checkpoint membership metadata, canonical candidate digest, pose units and
quaternion bounds. The candidate is limited by its owner-defined bound; the
Observation carrier is limited to 384 KiB and remains subject to the existing
1,000,000-byte response cap. This addition creates no endpoint, history,
cross-owner semantic join, or remote-access capability.
