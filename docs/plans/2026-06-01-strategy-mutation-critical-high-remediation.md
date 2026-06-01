# Active Plan

- Date: 2026-06-01
- Task: Remediate critical/high `strategy` mutation survivors
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Add focused tests for the critical/high `strategy` mutation survivors
  identified in `docs/plans/2026-06-01-strategy-mutation-survivor-triage.md`,
  keep mutation-gate scope honest, and make the default aggregate mutation gate
  pass at the configured 80% threshold without hiding important strategy
  contracts behind broad mutation exclusions.
- Governing docs: `AGENTS.md`, `README.md`, `ARCHITECTURE.md`,
  `docs/design-docs/package-topology-and-naming.md`, `docs/RELIABILITY.md`,
  `docs/plans/2026-06-01-strategy-mutation-survivor-triage.md`
- Why these are governing: They define the workflow contract, strategy bounded
  context, current mutation-gate policy, and the reviewed critical/high
  remediation priorities.
- In-repo scope:
  - `src/quantleet/strategy/config.py` and
    `src/quantleet/strategy/strategy.py` only for narrowing the mutmut
    `__init_subclass__` collection workaround while keeping declaration logic
    under mutation
  - `tests/unit/strategy/**`
  - `tests/structure/repo/test_poe_task_contracts.py` for the repository
    contract expectation that mirrors the mutation target list
  - `.coverage-baseline.json` if the default `coverage-baseline` check raises
    the baseline while verifying this slice
  - this plan
  - `docs/RELIABILITY.md` only if the strategy gate passes and the gate
    expansion is ready to describe as current policy
- Out-of-repo scope: dependency changes, mutmut package patches, threshold
  changes, and behavior changes unrelated to the `__init_subclass__` mutation
  collection workaround.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B strategy test
  remediation.
- Verification commands:
  - targeted `uv run pytest tests/unit/strategy -q`
  - `uv run poe mutation-gates`
  - `uv run poe check` if mutation gates pass and time allows
- Success criteria:
  - Critical order-intent tests cover default market orders, explicit symbol
    propagation, explicit symbol mismatch rejection, and stop trigger
    above/below/equal behavior, or any remaining mutants in those groups are
    explicitly classified as equivalent/tooling-limited with evidence.
  - High series tests cover visibility, indexing, append, advance, and
    preloaded bar advancement behavior.
  - High config tests cover unsupported union-shape rejection.
  - `uv run poe mutation-gates` passes with `no_tests=0` and score at or above
    `80%`.
- Out of scope:
  - Killing every `strategy` mutant.
  - Adding broad property-based tests or new dependencies.
  - Lowering the mutation threshold.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The mutation gate must pass
  because behavior-focused tests improve meaningful coverage and any mutation
  exclusions are minimal, documented, and limited to mutmut collection
  mechanics. The evaluator must not claim all critical/high mutants are killed
  unless fresh `mutmut results` evidence proves it.
- Acceptance artifact location:
  `docs/plans/2026-06-01-strategy-mutation-critical-high-remediation.md`
- How the generator and evaluator agreed on done before execution: This plan
  narrows the write surface to tests and documentation and ties completion to
  the existing mutation hard gate.
- Checks the evaluator will use:
  - `uv run pytest tests/unit/strategy -q`
  - `uv run poe mutation-gates`
  - `git diff --check`
- Auto-fail conditions:
  - Mutation threshold is lowered.
  - `strategy` is removed from the mutation target.
  - `StrategyConfig.__init_subclass__` or `Strategy.__init_subclass__` keeps
    broad `# pragma: no mutate` exclusions without documented mutmut
    collection evidence and direct declaration-contract tests.
  - Tests assert private sentinel representation only to kill equivalent
    mutants.
  - `no_tests` remains nonzero.

## Generator Work Log

- Planned slice order:
  1. Add behavior-focused unit tests for series visibility/advance.
  2. Add behavior-focused unit tests for order-intent and stop-trigger
     contracts.
  3. Add config union-shape rejection tests.
  4. Run targeted tests, then mutation gate.
- Notes:
  - Initial implementation added broad `# pragma: no mutate` comments to
    `StrategyConfig.__init_subclass__` and `Strategy.__init_subclass__` to
    avoid mutmut collection failures. Read-only review found that too broad
    because it hid core declaration/config resolution logic from mutation.
  - `docs/RELIABILITY.md` was updated after the strategy-inclusive mutation
    gate passed so the documented gate scope matches the configured gate.
  - `tests/structure/repo/test_poe_task_contracts.py` was updated after
    `uv run poe check` showed the old `trading`/`backtest`-only expectation no
    longer matched the configured mutation target list.
  - `.coverage-baseline.json` changed during the successful default check
    because the baseline checker raised the stored coverage from `92.535183%`
    to `92.575974%`.
- Blockers or scope changes:
  - Read-only review found two blockers:
    1. The plan overclaimed that critical/high mutants were killed when fresh
       survivor evidence still needed to be checked at mutant level.
    2. The plan did not include the production-source mutation workaround in
       its approved scope.
  - Scope was updated to allow a narrow `__init_subclass__` refactor
    experiment. The broad pragma workaround was rejected; the final helper
    extraction passed after concurrent mutmut processes sharing `mutants/` were
    eliminated.

## Evaluator Review

- Findings:
  - Superseded by the follow-up review loop below. The earlier "No blocking
    findings" disposition was too strong because it did not account for broad
    `__init_subclass__` pragmas or remaining critical survivor evidence.
  - The mutation threshold remained `80%`.
  - `strategy` remained in the mutation target.
  - The added tests focus on externally observable strategy behavior:
    order-intent contracts, stop trigger inference, series visibility/indexing,
    append/advance semantics, and unsupported config union rejection.
  - `no_tests` dropped from the previously reported `5` to `0`.
- Verification evidence:
  - `uv run pytest tests/unit/strategy -q`: `53 passed in 0.07s`.
  - `uv run ruff check tests/unit/strategy`: passed.
  - `git diff --check`: passed before the full mutation run.
  - `uv run pytest
    tests/structure/repo/test_poe_task_contracts.py::test_mutmut_configuration_targets_aggregate_contract_tests
    -q`: `1 passed in 0.02s`.
  - `rm -rf mutants && time uv run poe mutation-gates`: passed with
    `total=3357 killed=2713 survived=644 no_tests=0 suspicious=0 timeout=0
    segfault=0 score=80.82% threshold=80%`; wall time `7:55.70`.
  - First `uv run poe check`: failed in `coverage-gates` because
    `test_mutmut_configuration_targets_aggregate_contract_tests` still
    expected the old `trading`/`backtest` mutation scope.
  - Final `uv run poe check`: passed end-to-end after updating the repository
    contract test; key observed evidence included `847 passed, 4 skipped`,
    total coverage `93%`, diff coverage `100%`, mutation score `80.82%`, Twine
    checks passing for both built artifacts, repository checks passing, and all
    notebooks validating.
- Final disposition: reopened for narrow pragma remediation and fresh
  critical/high survivor review.

## Follow-Up Review Loop

### Read-Only Review Synthesis

- Review scope: current `# pragma: no mutate` changes in
  `src/quantleet/strategy/config.py` and `src/quantleet/strategy/strategy.py`,
  current survivor evidence, and plan consistency.
- Finding 1: broad pragmas on
  `StrategyConfig.__init_subclass__` lines 43-99 and
  `Strategy.__init_subclass__` lines 54-75 were too broad before the
  follow-up remediation.
  - Behavioral claim: core config field collection, annotation validation,
    inherited config resolution, generic config resolution, explicit config
    resolution, and conflict rejection are hidden from mutation.
  - Why it matters: these are strategy authoring contracts, not incidental
    collection mechanics.
  - Experiment: moving the logic to top-level helper functions made targeted
    unit tests, Ruff, and a fresh single-owner mutation gate pass. Earlier
    missing `mutants` working directory/meta-file errors were caused by
    concurrent mutmut processes sharing the same generated working tree, not by
    the helper extraction itself.
  - Final remediation: keep only the mutmut-sensitive `__init_subclass__`
    wrapper calls excluded, and keep the config/strategy declaration behavior
    in mutation-eligible helper functions.
  - Confidence: high.
- Finding 2: the previous accepted disposition overclaimed critical/high
  remediation.
  - Behavioral claim: aggregate score passing does not prove all critical/high
    mutants are killed.
  - Why it matters: the user goal is financially meaningful mutant management,
    not a raw score-only pass.
  - Minimal remediation: rerun fresh mutation evidence after narrowing the
    pragma workaround, inspect remaining critical/high survivors, and document
    whether each remaining group is killed, equivalent, tooling-limited, or a
    follow-up.
  - Confidence: high.

### Follow-Up Handoff Contract

- Scope: one writer may edit only the active plan,
  `src/quantleet/strategy/config.py`, `src/quantleet/strategy/strategy.py`, and
  focused strategy tests needed to resolve remaining verified critical/high
  mutants.
- Owner: Codex.
- Acceptance criteria:
  - Broad `__init_subclass__` pragmas are removed.
  - Any remaining pragma is limited to wrapper mechanics or classified
    tool-equivalent default-argument mutations.
  - Declaration behavior remains covered by direct unit tests and is housed in
    mutation-eligible helper functions.
  - Fresh targeted tests pass.
  - Fresh `uv run poe mutation-gates` passes at `80%` with `no_tests=0`.
  - The final evaluator records remaining critical/high mutants, if any,
    without overclaiming.
- Evidence required:
  - `git diff --check`
  - targeted unit tests
  - representative `mutmut show` or `mutmut run` evidence for the previously
    disputed critical groups
  - fresh aggregate mutation gate output
- Next-step note: after implementation, run another read-only review synthesis
  before final reporting.

### Follow-Up Closure Evidence

- `StrategyConfig.__init_subclass__` and `Strategy.__init_subclass__` now call
  top-level helper functions; the helper bodies no longer carry
  `# pragma: no mutate`.
- Fresh targeted representative mutmut run killed
  `quantleet.strategy.strategy.xǁStrategyǁbuy__mutmut_1`.
- Fresh single-owner `uv run poe mutation-gates` passed with
  `total=3458 killed=2807 survived=651 no_tests=0 suspicious=0 timeout=0
  segfault=0 score=81.17% threshold=80%`.
