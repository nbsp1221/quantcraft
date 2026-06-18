# Active Plan

- Date: 2026-06-01
- Task: Resolve strategy mutation remediation review blockers
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Close the read-only review blockers from the previous strategy
  mutation remediation slice by separating true order-intent survivors from
  mutmut trampoline-equivalent default-argument mutants, adding focused tests
  for the true behavior gap, documenting any intentional mutation exclusions,
  and re-running mutation/review evidence.
- Governing docs: `AGENTS.md`, `README.md`, `ARCHITECTURE.md`,
  `docs/design-docs/package-topology-and-naming.md`, `docs/RELIABILITY.md`,
  `docs/plans/2026-06-01-strategy-mutation-critical-high-remediation.md`,
  `docs/plans/2026-06-01-strategy-mutation-survivor-triage.md`
- Why these are governing: They define the repo workflow, strategy bounded
  context, current mutation gate policy, and the prior remediation claim that
  must be corrected with fresh evidence.
- In-repo scope:
  - `src/quantcraft/strategy/config.py` and
    `src/quantcraft/strategy/strategy.py` for moving declaration logic out of
    mutmut-sensitive `__init_subclass__` wrappers and for narrowly scoped
    mutmut exclusion comments on trampoline-equivalent default-argument
    mutants.
  - `tests/unit/strategy/test_strategy_surface.py` for observable order-intent
    tests.
  - `tests/structure/repo/test_poe_task_contracts.py` if a repository contract
    test is needed to document intentional mutation exclusions.
  - `pyproject.toml` if the mutation gate command itself must be hardened to
    avoid stale `mutants/` state.
  - `docs/plans/2026-06-01-strategy-mutation-critical-high-remediation.md`
    and this plan for corrected evidence and reviewer synthesis.
- Out-of-repo scope: dependency changes, mutmut package patches, threshold
  changes, and production behavior changes.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B strategy gate
  remediation and documentation.
- Verification commands:
  - `uv run pytest tests/unit/strategy tests/structure/repo/test_poe_task_contracts.py -q`
  - targeted `uv run mutmut run --max-children 4 <critical/high mutants>`
  - `uv run poe mutation-gates`
  - `uv run poe check` if the focused gates pass and time allows
- Success criteria:
  - The true `buy` explicit-symbol behavior gap is killed by a behavior test.
  - Helper-level explicit-symbol and stop-trigger critical mutants remain
    killed.
  - Default `buy`/`sell` order-type argument mutants are not represented as
    killed if mutmut can only exercise them through trampoline-equivalent inner
    defaults; they are either documented as tool-equivalent or excluded with a
    compensating source/signature contract.
  - The prior plan no longer claims that every critical/high mutant was killed
    solely by behavior tests.
  - Review findings are synthesized with concrete evidence.
- Out of scope:
  - Killing every strategy mutant.
  - New dependencies or property-based tests.
  - Lowering the mutation threshold or removing `strategy` from the mutation
    target.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The final state must not
  overclaim critical/high remediation. Any intentional mutation exclusion must
  have a concrete mutmut limitation, a narrow code marker, and a compensating
  non-mutation contract test or documented rationale.
- Acceptance artifact location:
  `docs/plans/2026-06-01-strategy-mutation-review-blocker-remediation.md`
- How the generator and evaluator agreed on done before execution: This plan
  records the read-only reviewer blockers before edits and requires another
  read-only review synthesis before final disposition.
- Checks the evaluator will use:
  - `uv run mutmut show <mutant>`
  - `uv run mutmut run --max-children 4 <critical/high mutants>`
  - `uv run pytest tests/unit/strategy tests/structure/repo/test_poe_task_contracts.py -q`
  - `uv run poe mutation-gates`
- Auto-fail conditions:
  - Mutation threshold is lowered.
  - `strategy` is removed from the mutation target.
  - A true order-intent behavior gap is dismissed as equivalent without
    targeted mutmut evidence.
  - Documentation says critical/high mutants are all killed when targeted
    mutmut evidence contradicts that.

## Generator Work Log

- Planned slice order:
  1. Record read-only exploration evidence for the prior blocker mutants.
  2. Add a focused explicit-buy-symbol mismatch test.
  3. Mark default `buy`/`sell` order-type defaults as mutmut
     trampoline-equivalent only if targeted evidence confirms normal tests
     cannot exercise those mutated defaults.
  4. Correct the prior remediation plan's scope and final disposition.
  5. Run targeted tests, targeted mutation, aggregate mutation, and review
     synthesis.
- Notes:
  - Initial targeted mutmut evidence showed `_submit_order_request`,
    `_resolve_order_symbol`, `_infer_trigger_condition`, and `sell(symbol=None)`
    mutants killed, while `buy(symbol=None)` and `buy`/`sell` default-argument
    mutants survived.
  - Inspecting `mutants/src/quantcraft/strategy/strategy.py` showed mutmut's
    trampoline wrapper keeps the outer `buy`/`sell` default `order_type` value
    as `"market"` and passes it as a keyword into the selected inner mutant;
    therefore inner default-argument mutations are not observable through
    ordinary calls.
  - A non-fresh targeted mutmut run reused stale generated code/`__pycache__`
    and produced misleading survivor evidence. Attempts to put cleanup directly
    into the Poe task made the current mutmut/`also_copy` setup fail during
    generation or execution, so this slice keeps the direct mutmut command and
    records fresh evidence explicitly instead of changing the command surface.
  - Read-only review correctly rejected the broad `__init_subclass__` pragma
    workaround. The final implementation keeps only the wrapper calls excluded
    and moves config/strategy declaration logic into top-level helper
    functions that remain mutation-eligible.
  - The apparent `mutants/` stability issue was reproduced as concurrent
    mutmut processes sharing the same generated working tree. After closing
    review agents and killing orphan mutmut processes, a single-owner
    `mutation-gates` run completed successfully.
- Blockers or scope changes:
  - The prior remediation plan incorrectly omitted `src/quantcraft/strategy/config.py`
    from the follow-up scope; this plan now includes it explicitly.

## Evaluator Review

- Findings:
  - No remaining blocking finding after the second review loop.
  - The previous broad pragma blocker is closed: `StrategyConfig.__init_subclass__`
    and `Strategy.__init_subclass__` now contain only wrapper mechanics, while
    `_initialize_strategy_config_subclass()` and `_initialize_strategy_subclass()`
    contain the declaration/config-resolution logic without `# pragma: no mutate`.
  - The `buy`/`sell` default `order_type="market"` exclusions remain narrow and
    are backed by behavior tests plus a public signature test. They are
    documented as mutmut trampoline-equivalent default-argument cases rather
    than claimed as killed behavior mutants.
  - The earlier operational-stability finding was valid for concurrent local
    mutmut runs. The accepted operating constraint for this repo is that
    `mutation-gates` owns `mutants/` exclusively; subagent reviews must not run
    mutmut against the same working tree. This is now recorded in
    `docs/RELIABILITY.md`.
  - Final read-only review found no remaining code/test/plan blocker for broad
    pragmas, narrow `buy`/`sell` default exclusions, scope, or overclaiming.
    A separate gate-integrity review asked for the `mutants/` ownership warning
    to move from this plan into durable reliability docs; that documentation
    update was applied.
- Verification evidence:
  - `uv run pytest tests/unit/strategy tests/structure/repo/test_poe_task_contracts.py -q`:
    `70 passed in 0.17s`.
  - `uv run ruff check src/quantcraft/strategy tests/unit/strategy tests/structure/repo/test_poe_task_contracts.py`:
    passed.
  - `git diff --check`: passed before the full mutation gate.
  - `uv run mutmut run --max-children 1
    'quantcraft.strategy.strategy.xǁStrategyǁbuy__mutmut_1'`: killed the
    representative default-buy mutant.
  - Fresh single-owner `uv run poe mutation-gates`: passed with
    `total=3458 killed=2807 survived=651 no_tests=0 suspicious=0 timeout=0
    segfault=0 score=81.17% threshold=80%`.
  - After the reliability-doc update:
    `uv run pytest tests/unit/strategy tests/structure/repo/test_poe_task_contracts.py -q`:
    `70 passed in 0.20s`; Ruff passed; `git diff --check` passed.
- Final disposition: accepted for this slice; remaining survived mutants are
  below the aggregate 80% hard gate and are not claimed as all remediated.
