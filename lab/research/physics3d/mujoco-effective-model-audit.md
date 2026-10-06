# MuJoCo Effective-Model Audit

**Audit revision:** `d9b70171ea4041aaf844cc20d2cfbbf0ec34ab41`  
**Engine:** MuJoCo 3.14.0  
**Evidence:** [`mujoco-effective-model-audit.json`](mujoco-effective-model-audit.json)

## Scope and result

The read-only effective-model audit enumerated all six canonical morphologies
against all five canonical environments (30 freshly constructed scenarios).
The suite hash is
`714aefbc922720751b964d4f134fd3ac6c8f74f8899fdadc197228cd922ae829`.
Repeating the command produced the same hash.

| Relation | Count |
| --- | ---: |
| Mismatch | 0 |
| Missing | 845 |
| Implicit | 330 |
| Provisional | 15 |
| Warnings | 1,190 |

Zero mismatches means this audit found no contradiction for the declarations
it currently compares. It does not show that the apparatus is calibrated or
that any effective value is physically appropriate. The other counts are
unresolved or intentionally provisional contract surfaces, not 1,190 distinct
failures.

## First descriptive pilot crosswalk

The existing owner-approved and frozen [Crawler Passive Characterization
v1](../../../docs/design/embodiment/crawler-passive-characterization-v1.md)
already selects canonical `crawler-v1` on standard flat ground at timestep
`1/240` s and gravity `(0, 0, -9.81)`, with two fresh constructions and
descriptive observations only. The matching audit scenario has report hash
`a99d976185f017d812e200eaa2d9f5334c797e7388ab6c1ad71c5131686163dc` and
reports zero mismatches, 21 missing, 9 implicit, and zero provisional findings.
The pilot protocol is already frozen and authorized under its limited scope;
this crosswalk does not extend that authorization or turn it into a calibration.

In this matching scenario, the missing fields comprise unrepresented material
restitution/damping declarations and declared joint velocity limits not enforced
by current MuJoCo dynamics. The implicit fields are solver/contact settings
coming from MuJoCo defaults. They must remain visible in the report; this audit
does not choose new mappings or parameter values.

## Limits and next review decisions

This report does not step the physics, tune parameters, establish acceptance
thresholds, or authorize calibration. Before freezing the broader approved
apparatus-calibration design, the owner/reviewer still needs to:

1. Disposition material restitution/damping, joint velocity limits, friction
   combination, solver/contact defaults, and provisional vision constants as
   intentional contract, instrumentation gap, separately reviewed change, or
   out of scope for a named stage.
2. Select body/environment coverage and ordering beyond the already frozen
   crawler passive pilot; specify which cases are passive, contact-driven, or
   vision-only.
3. Define observables and, for every numerical criterion, its value, unit,
   method, and justification before use. Descriptive-only observations should
   remain threshold-free.
4. Pin repeat/seed policy, artifact completeness rules, discrepancy
   disposition authority, and the separate review and explicit authorization
   required before any calibration run.

No PyBullet/A7 setting is transferred. No calibration or scientific run was
performed for this report.
