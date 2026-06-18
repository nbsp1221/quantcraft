# Active Plan

- Date: 2026-06-01
- Task: Classify `strategy` mutation survivors by risk before remediation
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Run or reuse the current mutation evidence for the expanded
  `trading`/`backtest`/`strategy` aggregate gate, isolate the `strategy`
  survivor/no-tests signal, classify the observed `strategy` mutants into
  `critical`, `high`, `medium`, and `low`, and write a remediation-planning
  report without changing production or test behavior.
- Governing docs: `AGENTS.md`, `README.md`, `ARCHITECTURE.md`,
  `docs/design-docs/package-topology-and-naming.md`, `docs/RELIABILITY.md`,
  `docs/plans/2026-06-01-strategy-mutation-gate-reproduction.md`
- Why these are governing: They define the repo workflow, public beta strategy
  scope, strategy bounded-context ownership, mutation-gate expectations, and
  the current `strategy` gate reproduction state.
- In-repo scope: A new plan/report artifact under `docs/plans/`; read-only
  inspection of mutation artifacts, `src/quantcraft/strategy`, and existing
  tests.
- Out-of-repo scope: dependency changes, mutmut package patches, external
  service calls, and network research.
- Tier A progression requested: `no`
- Approval record, if required: not required; this slice is Tier B and
  documentation-only.
- Verification commands:
  - `uv run poe mutation-gates`
  - `uv run mutmut results`
  - representative `uv run mutmut show <strategy-mutant>`
- Success criteria:
  - The report records current mutation evidence for the expanded aggregate
    gate.
  - The report separates `strategy` mutants into `critical`, `high`,
    `medium`, and `low` with concrete mutant evidence and rationale.
  - The report identifies which `critical`/`high` groups should be remediated
    first to make the 80% aggregate gate pass.
  - A read-only reviewer fan-out checks the report for correctness, testing
    value, maintainability, and risk framing, and the synthesis is recorded.
- Out of scope:
  - Adding or changing tests.
  - Changing the mutation threshold.
  - Removing the intentional `strategy` gate failure.
  - Reclassifying all historical `trading`/`backtest` survivors.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The final artifact must be a
  planning-quality report, not an implementation patch, and must cite mutation
  evidence that can be independently checked from the current repository state.
- Acceptance artifact location:
  `docs/plans/2026-06-01-strategy-mutation-survivor-triage.md`
- How the generator and evaluator agreed on done before execution: The plan
  limits the write surface to this document and requires reviewer synthesis
  before final disposition.
- Checks the evaluator will use:
  - `uv run poe mutation-gates`
  - `uv run mutmut results`
  - representative `uv run mutmut show <strategy-mutant>`
  - read-only subagent review findings
- Auto-fail conditions:
  - Production or test behavior is changed in this slice.
  - The report treats equivalent/low-value mutants as critical/high without a
    domain-risk rationale.
  - The report omits the `no_tests` signal.
  - The reviewer fan-out returns only summary approval without evidence.

## Generator Work Log

- Planned slice order:
  1. Collect fresh mutation-gate evidence.
  2. Extract `strategy` survivor/no-tests mutant names.
  3. Inspect representative and high-risk mutants with `mutmut show`.
  4. Classify mutants by domain risk and remediation value.
  5. Send the draft report to read-only reviewers and synthesize findings.
- Notes:
  - This slice intentionally does not remediate the mutants.
- Blockers or scope changes:
  - None currently.

## Strategy Mutation Survivor Report

### Fresh Evidence

- Command: `rm -rf mutants && time uv run poe mutation-gates`
- Result: failed as intended at the mutation score gate.
- Aggregate stats:
  - `total=3357`
  - `killed=2681`
  - `survived=671`
  - `no_tests=5`
  - `suspicious=0`
  - `timeout=0`
  - `segfault=0`
  - `score=79.86%`
  - `threshold=80%`
- Runtime: `7:45.05` wall time.
- Strategy-only evidence:
  - `128` survived mutants
  - `5` no-tests mutants
  - `133` total non-killed strategy mutants in the current result set

The aggregate gate is close to the threshold, but this is not just a numeric
failure. The `strategy` slice exposes untested contracts in the strategy
authoring surface, order-intent construction, stop-trigger inference, config
schema validation, and time-series visibility model.

### Classification Method

Classification is based on domain risk, not on raw mutant count alone:

- `critical`: a surviving mutant can change generated order intent, trigger
  direction, symbol routing, or default order type in a way that can change
  trades.
- `high`: a surviving mutant can change strategy inputs, lifecycle state,
  config admissibility, or runtime guardrails that materially affect future
  orders or reported behavior.
- `medium`: a surviving mutant weakens validation, immutability, inheritance,
  or diagnostics but is less directly tied to trade emission in the current
  beta scope.
- `low`: mostly diagnostic-string mutations, likely equivalent mutations, or
  cosmetic/default-state details where testing the exact value would add low
  reliability value.

### Function Distribution

`uv run mutmut results | rg '^    quantcraft\.strategy'` produced these
strategy function groups:

| Function group | Non-killed mutants | Initial classification |
| --- | ---: | --- |
| `Strategy._infer_trigger_condition` | 13 | critical/low split |
| `Strategy._resolve_order_symbol` | 11 | critical/low split |
| `Strategy.__delattr__` | 11 | medium/low split |
| `Strategy._handle_bar` | 8 | high/low split |
| `StrategyConfig.__delattr__` | 8 | medium/low split |
| `_inherited_config_type` | 7 | medium |
| `PositionView.__init__` | 6 | medium |
| `_SeriesBuffer.set_visible_length` | 6 | high |
| `_SeriesBuffer.__init__` | 6 | high/low split |
| `_resolve_supported_annotation` | 6 | high/low split |
| `SeriesView.__init__` | 5 | high |
| `SeriesView.__getitem__` | 5 | high/low split |
| `_validate_config_value` | 5 | medium/low split |
| `_public_type_hints` | 5 | medium |
| `Strategy._reset_runtime_state` | 4 | high |
| `Strategy._assert_order_intake_allowed` | 4 | low |
| `_SeriesBuffer.append` | 4 | high |
| `Strategy.buy` | 3 | critical |
| `Strategy.sell` | 3 | critical |
| `_generic_config_type` | 3 | medium |
| `_SeriesBuffer.advance` | 3 no-tests | high |
| `SeriesView._advance` | 2 no-tests | high |
| `Strategy._submit_order_request` | 1 | critical |
| `Strategy._materialize_config` | 1 | low |
| `_validate_config_type` | 1 | low |
| `SeriesView._append` | 1 | high |
| `StrategyConfig.__init__` | 1 | low |

### Critical Mutants

These are the highest-value remediation targets because they affect order
intent semantics or stop trigger semantics.

1. `Strategy.buy` and `Strategy.sell` default order type mutations
   - Mutants:
     - `quantcraft.strategy.strategy.xǁStrategyǁbuy__mutmut_1`
     - `quantcraft.strategy.strategy.xǁStrategyǁbuy__mutmut_2`
     - `quantcraft.strategy.strategy.xǁStrategyǁsell__mutmut_1`
     - `quantcraft.strategy.strategy.xǁStrategyǁsell__mutmut_2`
   - Representative evidence: default `order_type="market"` changes to
     `"XXmarketXX"` or `"MARKET"`.
   - Why critical: strategy authors commonly call `buy(quantity=...)` and
     `sell(quantity=...)` without passing `order_type`; changing the default can
     turn a valid market order into an invalid or differently interpreted order.
   - Test implication: assert default `buy` and `sell` create market
     `PendingOrderRequest`s.

2. Explicit symbol propagation and mismatch rejection
   - Mutants:
     - `quantcraft.strategy.strategy.xǁStrategyǁbuy__mutmut_4`
     - `quantcraft.strategy.strategy.xǁStrategyǁsell__mutmut_4`
     - `quantcraft.strategy.strategy.xǁStrategyǁ_submit_order_request__mutmut_20`
     - `quantcraft.strategy.strategy.xǁStrategyǁ_resolve_order_symbol__mutmut_3`
     - `quantcraft.strategy.strategy.xǁStrategyǁ_resolve_order_symbol__mutmut_4`
     - `quantcraft.strategy.strategy.xǁStrategyǁ_resolve_order_symbol__mutmut_5`
   - Representative evidence:
     - `symbol=symbol` changes to `symbol=None`.
     - `symbol != active_bar_symbol` changes to `symbol == active_bar_symbol`.
     - `and` changes to `or` or `active_bar_symbol is None`.
   - Why critical: this can silently route orders to the active bar symbol while
     ignoring the explicit symbol, or accept an explicit symbol mismatch in the
     single-symbol beta workflow.
   - Test implication: assert explicit matching symbols are preserved and
     mismatching symbols are rejected for both `buy` and `sell`.

3. Stop trigger condition return contract
   - Mutants:
     - `quantcraft.strategy.strategy.xǁStrategyǁ_infer_trigger_condition__mutmut_21`
     - `quantcraft.strategy.strategy.xǁStrategyǁ_infer_trigger_condition__mutmut_22`
   - Representative evidence: return `"crosses_below"` changes to
     `"XXcrosses_belowXX"` or `"CROSSES_BELOW"`.
   - Why critical: stop-family orders depend on the inferred trigger condition.
     Returning a non-contract string can break activation or turn a valid stop
     intent into an invalid internal state.
   - Test implication: assert stop prices above and below the active close map
     exactly to `"crosses_above"` and `"crosses_below"`.

### High Mutants

These should be remediated in the same follow-up slice if the goal is to make
`strategy` a credible part of the default hard gate.

1. Series visibility and historical indexing
   - Mutants/groups:
     - `_SeriesBuffer.set_visible_length`: 6 survived
     - `_SeriesBuffer.__init__`: behavior-changing boundary variants such as
       `visible_length > len(values)` becoming `>=`
     - `_SeriesBuffer.append`: visible length increments by `2`
     - `_SeriesBuffer.advance`: 3 no-tests
     - `SeriesView.__init__`: `visible_length` ignored for tuple-backed views
     - `SeriesView.__getitem__`: historical index and boundary behavior
     - `SeriesView._append`: appends `None`
     - `SeriesView._advance`: 2 no-tests
   - Representative evidence:
     - `visible_length < 0 or visible_length > len(self.values)` changes to
       `and`, allowing invalid visibility.
     - `self.visible_length += 1` changes to `+= 2`.
     - `_advance(step=1)` changes to `_advance(step=2)`.
   - Why high: strategy signals consume `self.data.open/high/low/close/volume`
     through these views. A lookback/indexing bug can change entry/exit timing
     without touching the backtest engine.
   - Test implication: add focused tests for visible-length boundaries,
     append/advance increments, `latest`, historical `[0]`, `[1]`, out-of-range
     `nan`, and negative-index rejection.

2. Strategy lifecycle state cleanup, narrowed to observable leakage paths
   - Mutants/groups:
     - `Strategy._handle_bar__mutmut_11` through
       `Strategy._handle_bar__mutmut_14`
     - `Strategy._reset_runtime_state` mutants that change active-bar symbol or
       close cleanup
   - Representative evidence:
     - `_active_bar_close = None` changes to `""`.
   - Why high: stale active-bar symbol or close can affect future order symbol
     resolution or stop-trigger inference.
   - Important boundary: message-only closed-bar mutants and truthiness-preserved
     `_handling_bar = False` to `None` variants are low-value unless an
     externally observable behavior changes.
   - Test implication: assert state is restored after normal `on_bar` and after
     exception through public/runtime-observable behavior; avoid asserting exact
     private sentinel values solely to kill truthiness-equivalent mutants.

3. Config schema admissibility
   - Mutants/groups:
     - `_resolve_supported_annotation`: behavior-changing optional/union
       variants.
   - Representative evidence:
     - `len(non_none_args) != 1 or len(non_none_args) == len(args)` changes to
       `and`, admitting unsupported union shapes.
   - Why high: config schema controls strategy parameter search and runtime
     construction. Allowing unsupported union shapes can create parameters that
     downstream code does not validate consistently.
   - Test implication: add explicit rejection tests for `int | str`,
     `int | str | None`, and non-optional `Union` shapes.

### Medium Mutants

These are worth tracking, but should not block the first remediation slice
unless they are cheap to kill alongside high-priority tests.

1. Config and strategy immutability deletion paths
   - Mutants/groups:
     - `StrategyConfig.__delattr__`: 8 survived
     - `Strategy.__delattr__`: 11 survived
   - Rationale: deletion immutability matters, but most surviving variants are
     truthiness or diagnostic-message changes. Existing tests already prove the
     core rejection path for `config` and materialized config fields.
   - Suggested next action: add one or two targeted tests only for behavior
     changes that would permit deletion or over-reject unrelated attributes.

2. PositionView defaults
   - Mutants: `PositionView.__init__`: 6 survived.
   - Rationale: the initial position view should be flat with zero quantity and
     zero average price. This is user-visible but refreshed from
     `TradingState` in normal runtime paths.
   - Suggested next action: assert initial `PositionView` defaults through a
     strategy instance and after runtime refresh.

3. Generic and inherited config type helpers
   - Mutants/groups:
     - `_generic_config_type`: 3 survived
     - `_inherited_config_type`: 7 survived
     - `_validate_config_type`: 1 survived
   - Rationale: these affect subclass declaration diagnostics and inheritance
     compatibility. Important for authoring, but less directly tied to emitted
     orders than the critical groups.
   - Suggested next action: add tests for inherited config propagation,
     explicit fallback inheritance, and invalid inherited config diagnostics.

4. Public type-hint isolation
   - Mutants: `_public_type_hints`: 5 survived.
   - Rationale: this protects the public/private annotation boundary and
     forward-reference resolution, but the current high-priority evidence is
     weaker than the direct union-shape admission mutant.
   - Suggested next action: keep this medium unless a representative mutant is
     shown to admit unsupported public config fields or break supported public
     forward references.

### Low Mutants

These should not drive the first hard-gate remediation:

- Error-message-only mutations in:
  - `_infer_trigger_condition`
  - `_resolve_order_symbol`
  - `_assert_order_intake_allowed`
  - `_validate_config_value`
  - `StrategyConfig.__init__`
  - `Strategy._materialize_config`
  - `_validate_config_type`
- Likely equivalent or low-value mutations:
  - `Strategy._infer_trigger_condition__mutmut_18`, because the equality case
    is already guarded immediately before the mutated `>` comparison.
  - truthiness changes where both `False` and `None` preserve the current branch
    behavior and only exact private-state representation changes.

Low does not mean useless forever. It means these should be deliberately
deferred until the behavior-changing critical/high groups are killed.

### Remediation Priority

To pass the gate, the next implementation slice must solve two independent
conditions:

- `no_tests` must become `0`.
- aggregate score must reach at least `80%`.

Since the current score is `79.86%`, killing only a small number of survived
mutants is numerically enough, but the meaningful path is:

1. Add `SeriesView`/`_SeriesBuffer` advance and visibility tests first.
   - This removes the `5` no-tests mutants and kills several high-value series
     survivors.
2. Add order-intent tests for default order type and explicit symbol handling.
   - This targets the direct critical mutants.
3. Add stop trigger tests for above/below/equal active close and invalid
   stop-price shapes.
   - This targets the stop-condition critical group.
4. Add lifecycle cleanup tests after normal and exceptional `on_bar`.
   - This should target observable stale symbol/close or pending-order cleanup
     behavior, not exact private truthiness sentinels.
5. Add config union-shape rejection tests if the gate still has low margin.

This order is intentionally not “kill every mutant.” It targets the
financially meaningful mutants first and should provide enough score movement
to pass the current aggregate 80% hard gate with a stronger test-quality story.

### Follow-Up Documentation Note

`docs/RELIABILITY.md` still says `mutation-gates` runs the aggregate gate across
`trading` and `backtest`. If the `strategy` gate expansion is accepted for
committed operation, update that repo-level reliability text in the same
implementation slice that makes the gate pass.

## Reviewer Fan-Out

Three read-only reviewers checked the report through the
`subagent-orchestration` review fan-out pattern.

1. Correctness and mutation-evidence reviewer
   - Disposition: no blocking issue.
   - Evidence: confirmed `strategy` has `128 survived` and `5 no-tests`
     mutants; confirmed critical classification for default order type,
     explicit symbol propagation, mismatch rejection, and
     `"crosses_below"` trigger contract.
   - Required adjustment: narrow `_handle_bar` high classification to
     cleanup/state-leakage mutants; move closed-bar message-only mutants to low.
   - Action taken: incorporated above.

2. Testing-value reviewer
   - Disposition: conditional approval.
   - Evidence: confirmed the `SeriesView`/`_SeriesBuffer` first-priority slice
     is valuable because all `5` no-tests mutants are series advance mutants and
     visible-length/indexing bugs can shift strategy signal timing.
   - Required adjustment: avoid overfitting lifecycle tests to private
     `False` versus `None` truthiness, and keep `_public_type_hints` out of the
     high bucket unless supported by stronger behavior evidence.
   - Action taken: incorporated above.

3. Maintainability and risk-framing reviewer
   - Disposition: acceptable with follow-up.
   - Evidence: confirmed the direction is consistent with `strategy` as the
     shared strategy authoring/configuration context in `ARCHITECTURE.md`.
   - Required adjustment: record that `docs/RELIABILITY.md` must be updated when
     the `strategy` mutation gate expansion is made permanent.
   - Action taken: recorded as a follow-up documentation note.

## Evaluator Review

- Findings:
  - No blocking report defects remain after reviewer synthesis.
  - The critical/high set is now narrowed to behavior-changing mutants rather
    than raw survivor count.
  - The report remains documentation-only; no production or test behavior was
    changed in this slice.
- Verification evidence:
  - `rm -rf mutants && time uv run poe mutation-gates`: failed at the intended
    mutation score gate with `total=3357 killed=2681 survived=671 no_tests=5
    suspicious=0 timeout=0 segfault=0 score=79.86% threshold=80%`.
  - `uv run mutmut results | rg '^    quantcraft\.strategy'`: confirmed
    `128` strategy survived mutants and `5` strategy no-tests mutants.
  - Representative `uv run mutmut show` evidence was collected for order type,
    symbol propagation, stop trigger return value, series visibility/indexing,
    config union-shape validation, and lifecycle cleanup mutants.
  - Read-only reviewer fan-out returned one no-blocker review and two
    conditional/maintainability reviews; all required adjustments were
    incorporated.
- Final disposition: accepted as the planning report for a future
  critical/high strategy mutation remediation slice.
