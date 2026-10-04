# Private episodes never carry a competence identity on the canonical runtime (2026-10-04)

Found while preparing the confirmatory W1 protocol the owner requested. It
makes that protocol's question structurally untestable, so the protocol was
**not** preregistered or run. Source for the numbers:
`lab/research/studies/cognition/cognitive-cycle/2026-10-04-run-receipts.json`.

## Observation

In the seed-42 organism developed 1536 ticks on `main` (run
`cc-w1-dev-s42-r2`):

- 601 of 601 motor-caused private episodes have a distinct action token,
  all of the form `action.command.<id>`;
- all 35 generative hypotheses target `gc.prospective.primitive.<id>`;
- the 6 hypotheses sourced from `private-slm` are still `predicted`, with no
  support and no conflict reference, after 1536 ticks; the same six are
  unchanged 512 ticks later and after re-embodiment;
- every factual source recorded by generative consolidation is a `causal.`
  reference from the competence-effect route (27 of 27);
- of the active model's 602 validated predictions, 571 are contradicted.

## Cause (static trace)

`ActionDomain.act` returns
`ActionStepResult(action_id=self.last_motor_command.command_id, …)`
(`symbiont/core/domains/action.py`). A command id is unique per command.

`PrivateModelOrganismRuntime._capture_private_frame` takes its first branch
whenever `result.action_result` is present and sets
`action_token = f"action.{action_id}"`
(`symbiont/modeling/private_runtime.py`). The branch that substitutes the
competence's opaque identity — whose comment says it gives "counterfactual
inference the same token that was produced during training — one
representation for learning and imagining" — is an `elif` that runs only
when there is no `action_result`. On the canonical runtime a motor command
always produces one, so that branch is unreachable.

`symbiont/tests/unit/modeling/test_private_experience_pipeline.py::test_private_runtime_uses_opaque_primitive_identity_as_action_token`
builds a `RuntimeTickResult` without `action_result`, so it exercises the
unreachable branch and passes.

## Consequences

1. **Private-model hypotheses cannot be reconciled.** The private runtime
   notes the factual outcome under `gc.prospective.command.<id>`; no
   hypothesis has that target. Imagined outcomes attributed to the private
   model are never confronted with what happened.
2. **Finding F2 of Cognitive Cycle v1 is latent, not active.** The
   "one event counted as up to 17 factual sources" path requires a
   private-model hypothesis to be reconciled. It did not happen once in this
   organism. The second half of `shared_fact_identity` (one event, one
   source) therefore has no effect on the canonical runtime.
3. **The training corpus has no repeated action.** Each action token occurs
   once, so a private model cannot learn an action-conditioned transition,
   and a counterfactual query names a competence token that never appeared
   in training. This is a candidate structural explanation for Private Model
   Learnability v1 (no candidate beat the frequency baseline). It is a
   hypothesis from a static trace and one organism, not a tested claim.

## What this is not

Not a fix and not a decision. Changing which identity a private episode
carries changes what every private model learns and what prospective
deliberation can use; it is an organism behaviour change that needs its own
design and review. The observation comes from one organism and one seed;
the cause is read from the code and is independent of the seed.

## Disposition of the requested confirmatory protocol

The owner asked for a confirmatory test of "does the flag reduce the
generative factual-source count" on a horizon where reconciliations occur.
No such horizon exists on the canonical runtime: the path is unreachable
(consequence 1). A protocol on that question would be NOT_TESTABLE by
construction, so none was frozen and no run was launched. The question
becomes testable only after the action-identity issue above is decided.

## Addendum — corrected (2026-10-04, owner instruction "modify the organism")

Origin: commit `217489e66` (2026-09-25, "report committed physical execution
from ActionDomain") made the action domain return the command id for every
motor command, which silently took the private frame out of the
competence-identity branch introduced the same day by `bd80bc995`.

Change (`symbiont/modeling/private_runtime.py`): a tick that actuated is
identified by what was done — the competence's opaque identity when a named
competence drove it, the composite motor token otherwise — and never by its
command id. A non-motor action result keeps its own id. Two tests build a
production-shaped result (with `action_result`) for both cases.

Mechanics checks, not evidence (scratch runs with the corrected code):

| Check | Motor episodes | Distinct action tokens | Private-model hypotheses reconciled |
|---|---|---|---|
| developed organism continued 128 ticks from tick 1536 | 111 | 1 (`action.motor.composite`; no competence was executed in the window) | 0 |
| fresh organism, 480 ticks, no model trained | 387 | 3 (two `action.primitive.*`, composite) | 0 (none exists) |
| fresh organism, 480 ticks, models trained | 375 | 2 (one `action.primitive.*`, composite) | 5 of 13 |

In the third check the five reconciliations added 64 `evidence.` references
to generative consolidation beside 10 `causal.` ones: **finding F2 is now
active**, as the design described, with `shared_fact_identity` off.

Consequences of the correction that are not yet measured:

- every private model trained from now on sees a different corpus; models
  and results from before this change are not comparable with later ones;
- Private Model Learnability v1 was run on per-command tokens. Whether the
  correction changes its negative result is an open empirical question;
- the confirmatory W1 question (does the flag reduce the factual-source
  count) is now testable.

The second and third checks came from one invocation: the scratch script had
no `__main__` guard and a spawned worker re-executed it. Both are fresh
organisms; neither is a governed run.

