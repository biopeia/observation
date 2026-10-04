# Crawler Passive Characterization v1 — run record (2026-10-04)

This is the descriptive record for the authorized execution of the frozen
protocol [`Crawler Passive Characterization v1`](../../../../docs/design/embodiment/crawler-passive-characterization-v1.md).
It records this run only; it does not amend or reinterpret the frozen protocol.

## Execution provenance

| Field | Value |
|---|---|
| Run ID | `crawler-passive-characterization-20261004` |
| Experiment ID | `crawler-passive-characterization-v1` |
| Scope | `mechanical` |
| Pinned source commit | `61397bd652aeac26759fb07db04417655a2ddaef` |
| Agentctl state | `complete`, return code 0 |
| Seed | None in the protocol; launcher bookkeeping value `0`, with no stochastic input |
| Effective runner config SHA-256 | `85247916aa735c4a69ef8d74aeba2d3e2c6ee0337d64ac400b2f783591480d18` |
| UV lock SHA-256 | Recorded in the archived raw report |

The first resource preflight attempt did not start the study (4.73 GiB available
against 5.00 GiB requested). The same frozen protocol was then run with a
3 GiB declared memory allocation. No study settings, thresholds, or inputs
changed between attempts.

## Effective scene and body

The two fresh constructions each compiled to 14 bodies, 13 joints, 10 geoms,
19 position coordinates and 18 velocity coordinates. Effective scene settings
were timestep `1/240 s`, gravity `(0, 0, -9.81) m/s²`, 100 solver iterations,
and tolerance `1e-8`. The compiled body mass was `17.6 kg`; the corresponding
weight used for the descriptive ratio was `172.656 N`.

### Declared-to-compiled mapping observations

The archived descriptor and compiled model differ in several inspectable
ways; these were recorded, not repaired:

- The descriptor declares twelve joints; all twelve appear in the compiled
  model with a `body.` name prefix. The compiled model also has `body.root`.
- The descriptor lists four foot segments (combined declared mass `0.5 kg`
  for the front pair and `0.56 kg` for the rear pair; `1.06 kg` total), but there are
  no corresponding foot bodies/geoms in the compiled model. Instead, the
  compiled model includes four `0.05 kg` yaw-carrier bodies absent from the
  declared segment table. The declared segment masses sum to `18.46 kg`; the
  compiled non-world body masses sum to `17.6 kg`.
- The compiled model contains nine crawler geoms, all emitted as `unnamed-1`
  through `unnamed-9`, so the trace has effective dimensions/materials but no
  semantic geom names to directly pair to descriptor segments.

These are declaration/runtime mapping discrepancies visible in this one
execution, not a diagnosis of why the mapping occurs or a physical defect
claim. The full declared and compiled values are in the raw report.

## Observations

| Observable | Construction 1 | Construction 2 |
|---|---:|---:|
| Settling | converged, 451 steps, 48 stable samples | converged, 451 steps, 48 stable samples |
| Residual base linear speed | 0.0002026 m/s | 0.0002026 m/s |
| Residual base angular speed | 0.0002985 rad/s | 0.0002985 rad/s |
| Post-settle window | 480 steps | 480 steps |
| Base displacement over window | 0.000003140 m | 0.000003140 m |
| COM height, start → end | 0.471466047 → 0.471465749 m | 0.471466047 → 0.471465749 m |
| Mean ground reaction | 172.656058 N | 172.656058 N |
| Mean reaction / body weight | 1.000000338 | 1.000000338 |
| Mean / maximum penetration | 0.000389000 / 0.000389090 m | 0.000389000 / 0.000389090 m |
| Ground contacts, mean / maximum | 8 / 8 | 8 / 8 |
| Finite values | yes | yes |
| Protocol disposition | reportable | reportable |

Each replicate contains 932 trace records (initial state, settling, and the
post-settle window). The captured per-step traces are exactly equal between
these two fresh constructions. This is repeat agreement for this single pinned
configuration and run, not a general determinism or physical-validity claim.

## Evidence files and integrity

- Full report and time series, gzip-compressed:
  [`2026-10-04-crawler-passive-characterization-trace.json.gz`](2026-10-04-crawler-passive-characterization-trace.json.gz)
  — SHA-256 `00d5955ed9d892ea76690df1d336be22d2b240fb3fd25e4c0d4c6dced55c1eee`
- Uncompressed report SHA-256: `e48268ac2260915b0432128659f1d5cb91f32009428556d51b90b7a5be3de235`
- Agentctl execution receipt (including verified child command/config fingerprint):
  [`2026-10-04-crawler-passive-characterization-agentctl-execution.json`](2026-10-04-crawler-passive-characterization-agentctl-execution.json)
- Agentctl artifact manifest:
  [`2026-10-04-crawler-passive-characterization-artifact-manifest.json`](2026-10-04-crawler-passive-characterization-artifact-manifest.json)

## Limits

This is a passive simulation characterization of `crawler-v1` under the
recorded MuJoCo configuration. It has no physical reference measurements and
does not establish physical calibration, contact realism, locomotion,
organism competence, or any property beyond these two constructions. No
parameters were changed or tuned. Further physical calibration or broader
scientific claims require a separate scope and evidence contract.
