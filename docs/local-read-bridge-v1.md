# Local Observation Read Bridge v1

**Status:** Implementation candidate for local development only
**Owner:** Observation
**Source base:** `e37f82dc0282074874ef68911eda69c3661bf9a8`
**Purpose:** Expose the bounded current subset already held by one in-process
`ObservationPlane` to the local Frontend development server.

This bridge does not create semantic claims, establish a World commit, make
cross-domain joins, or provide durable history. It is not a production,
multi-user, remote-access, or scientific-evidence interface.

## Route and method

```text
GET /v1/current
```

No query parameters are defined. Only `GET` is accepted. Request bodies and
other methods are rejected. The route is bound to one existing
`ObservationPlane`; it does not instantiate a plane or World runtime.

The bridge is intended to be called by a same-origin local development-server
proxy. The browser must not call the bridge as a cross-origin endpoint. The
proxy is expected to forward the browser's approved local origin to the bridge;
the bridge does not return CORS permission headers.

## M1 family allowlist

The route passes through only these exact semantic family identities:

| Qualified family | Authority | Contract ID | Revision | Epistemic kind |
| --- | --- | --- | --- | --- |
| `embodiment.body_pose` | Embodiment | `embodiment.body_pose` | `v1` | `authoritative_state` |
| `environment.finite_scalar_field` | Environment | `biopeia.environment.finite-scalar-field` | `1` | `domain_derived` |

A matching display name with a different authority, contract ID, revision, or
epistemic kind is not admitted. Unsupported families are excluded; the bridge
does not count or disclose them.

The family-specific value and envelope are validated against the current
Observation projection adapters. For BodyPose, this includes position units,
orientation representation, typed body/episode/morphology identity, World
causal-tick context, and Embodiment state lineage. For the scalar field, this
includes the dimensionless `[0, 1]` field value, unit, reference frame and
sample point, typed Environment/resource identity, source/target World tick
context, owner-checkpoint lineage, and projection transformation reference.
Invalid approved-family content fails closed; the bridge does not repair,
coerce, or infer missing fields.

All admitted source observation fields are serialized without substituting
Observation delivery metadata for source authority, identity, time, revision,
units, frame, or provenance. Each returned message adds only its
`delivery_sequence`, which is local to that plane instance.

## Response semantics

The success envelope has schema `biopeia.observation.current.v1` and contains:

- `availability`: `available` or `current_view_empty` for the approved subset.
- `absence_semantics`: always `not_evidence_of_source_absence`.
- `scope`: `bounded_in_memory_current_subset`.
- `freshness`: `not_established_by_snapshot`.
- `coherence`: `per_message_only_no_cross_owner_snapshot_guarantee`.
- `messages`: approved current messages, each with its local delivery sequence
  and an unchanged semantic observation envelope.

`current_view_empty` is not a source census. It may mean that the bounded
current subset contains no retained approved messages; it does not prove that
an owner state, body, resource, publication, or World is absent. Likewise, a
200 response does not assert that its messages are fresh or form one coherent
cross-owner cut. Consumers may not join or synchronize claims using arrival
order, browser time, geometry, names, or delivery sequence.

This snapshot route does not expose replay, expiry, stream rebase, partial
publication detection, currentness guarantees, or arbitrary historical
queries. Those properties cannot be inferred from a bounded current snapshot.
Delivery sequence gaps are possible because the underlying plane sequence is
global and other families may be excluded.

## Failure behavior and limits

| Condition | Response |
| --- | --- |
| Host differs from the configured local address | `400 invalid_host` |
| Missing or unexpected Origin | `403 origin_denied` |
| Request body or unsupported method | `400` or `405` |
| Unknown route | `404 not_found` |
| Encoded response exceeds byte limit | `413 current_view_exceeds_response_limit` |
| Plane read or approved-family serialization is invalid | `503 current_view_unavailable` |

Responses set `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`.
The default response limit is one million bytes. The default bind is
`127.0.0.1:4174`, and the configured browser origin must be one exact HTTP
origin on a literal loopback IP address.

Loopback, Host, and Origin checks limit accidental exposure and cross-site
requests in the intended local workflow. They are not authentication and do
not defend against a malicious process running as the same local user. No
credentials, tokens, wildcard CORS, remote bind, persistence, history, stream,
write route, World command, or Lab operation is supported.

## Verification boundary

Unit and local HTTP tests can establish filtering, schema rejection, response
limits, request validation, and non-mutation of the Observation plane. They do
not establish a live World-to-browser composition, durable delivery, security
against local malware, scientific validity, or production readiness. A real
TARGET World transition and same-origin Frontend consumer remain separate
integration acceptance requirements.
