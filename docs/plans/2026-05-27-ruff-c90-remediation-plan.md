# Ruff C90 Remediation Plan

- Date: 2026-05-27
- Task: Remediate the 9 remaining non-false-positive Ruff `C90` findings.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Remediate every remaining non-exempt `C901` finding after the one
  confirmed false positive was suppressed.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-05-26-ruff-c90-evaluation.md`
- Why these are governing: The change is a repository quality-gate migration
  with edits in runtime-sensitive backtest/research paths and Tier A `trading`
  modules.
- In-repo scope:
  - `pyproject.toml`
  - `src/quantleet/_repo_tools.py`
  - `src/quantleet/backtest/execution_model.py`
  - `src/quantleet/backtest/runtime.py`
  - `src/quantleet/integrations/venues/ccxt/market_data.py`
  - `src/quantleet/research/parameter_exploration.py`
  - `src/quantleet/strategy/config.py`
  - `src/quantleet/trading/domain/intents.py`
  - `src/quantleet/trading/domain/orders.py`
  - `src/quantleet/trading/order_requests.py`
  - `tests/unit/trading/test_contracts.py`
  - Active plan artifacts under `docs/plans/`
- Out-of-repo scope: none.
- Tier A progression requested: `yes`, for the future `trading` fixes only.
- Approval record, if required:
  - requestor: user
  - human approver: user
  - check marker: 2026-05-27 thread instruction to enter work phase and proceed
    autonomously inside the documented implementation scope
  - granted scope: behavior-preserving refactors needed to satisfy this C90
    remediation plan, including `src/quantleet/trading/**` validator extraction
  - expiration: end of this C90 remediation implementation slice
  - audit reference: this plan and the 2026-05-27 user instruction in the
    current agent thread
- Verification commands:
  - `uv run ruff check src tests scripts --select C90 --statistics`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run pytest tests/structure/repo tests/structure/architecture tests/unit/research tests/unit/data tests/unit/integrations tests/unit/backtest tests/smoke/local tests/unit/trading tests/unit/research/test_strategy_surface.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe check-runtime`
  - `uv run poe check`
- Success criteria:
  - Each remaining `C901` finding has a concrete diagnosis.
  - Each finding has a proposed behavior-preserving remediation path.
  - The decision basis includes both theory and practice web references.
  - Tier A and runtime-sensitive verification needs are explicit.
  - Implementation removes all non-exempt `C901` findings without raising the
    threshold.
  - Required verification and independent subagent review are complete.
- Out of scope:
  - Raising the C90 threshold.
  - Adding more `noqa` exceptions.
  - Changing public APIs or runtime semantics.
  - Raising `.coverage-baseline.json` as part of this C90 slice.

## Evidence Basis

### Harness Operating Basis

- The work follows the long-running harness principle of separating planning,
  generation, and evaluation. Anthropic's harness write-up describes the
  planner/generator/evaluator split, sprint-style done contracts, file-backed
  handoffs, and independent QA as useful controls for long-running autonomous
  coding work:
  https://www.anthropic.com/engineering/harness-design-long-running-apps
- Subagent write ownership is split across disjoint file groups:
  - Worker A: repository check helpers in `_repo_tools.py`.
  - Worker B: research/integration helpers.
  - Worker C: backtest runtime/execution helpers.
  - Worker D: Tier A trading validators.
- Parent orchestration owns synthesis, final verification, and review issue
  triage.

### Initial Local Evidence

- `uv run ruff check src tests scripts --select C90 --statistics` reports
  `9 C901 complex-structure` findings after suppressing the one confirmed false
  positive in `_validate_config_value`.
- `uv run ruff check .` fails on the same 9 `C901` findings.
- The active Ruff gate now includes `C90`.

### Theory References

- Ruff `C901` checks functions with high McCabe complexity:
  https://docs.astral.sh/ruff/rules/complex-structure/
- McCabe/cyclomatic complexity measures independent execution paths; Sonar's
  guide frames high scores as harder to test, maintain, and debug:
  https://www.sonarsource.com/resources/library/cyclomatic-complexity/
- Radon ranks `11-20` as moderate-risk/slightly complex blocks, which covers
  most of the remaining findings except the `60` outlier:
  https://radon.readthedocs.io/en/stable/api.html

### Practice References

- Sonar distinguishes cyclomatic complexity from cognitive complexity:
  cyclomatic complexity is strong for testability/path count, but human review
  is still needed before deciding whether a finding is a maintainability defect:
  https://www.sonarsource.com/blog/cognitive-complexity-because-testability-understandability/
- Refactoring.Guru treats long/branch-heavy methods as a practical code smell
  and recommends Extract Method when a method contains separable responsibilities:
  https://refactoring.guru/smells/long-method
- Refactoring.Guru's composing-methods guidance supports extracting well-named
  operations when local variable coupling does not make extraction unsafe:
  https://refactoring.guru/refactoring/techniques/composing-methods

## Remediation Queue

### 1. `collect_doc_issues` - `src/quantleet/_repo_tools.py:369` - `60 > 10`

- Classification: true positive, highest priority.
- Why it is complex: one function validates required docs, README sections,
  financial disclaimers, public docs, plans guidance, AGENTS guidance,
  `pyproject.toml` Poe configuration, routing indexes, and directory index
  membership.
- Real risk: new repo-check rules will keep being appended to the same function,
  increasing path count and making failures harder to isolate.
- Remediation:
  - Extract focused collectors:
    - `_collect_required_doc_issues(root)`
    - `_collect_readme_doc_issues(root)`
    - `_collect_public_doc_issues(root)`
    - `_collect_financial_disclaimer_doc_issues(root)`
    - `_collect_plans_doc_issues(root)`
    - `_collect_agents_doc_issues(root)`
    - `_collect_pyproject_poe_issues(root)`
    - `_collect_routing_index_issues(root)`
    - `_collect_legacy_index_membership_issues(root)`
  - Keep `collect_doc_issues(root)` as an orchestration function that extends
    issue lists in the same order to preserve exact output ordering.
  - Do not change issue text unless tests require an explicit update.
- Verification:
  - `uv run pytest tests/structure/repo -q`
  - `uv run python scripts/repo_check.py`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `collect_doc_issues` drops below 10; extracted helpers
  should each remain under 10.

### 2. `_run_backtest` - `src/quantleet/backtest/runtime.py:25` - `20 > 10`

- Classification: true positive, high risk.
- Why it is complex: the function initializes runtime state, iterates bars,
  activates orders, syncs reservations, handles tick events, triggers dormant
  orders, applies fills, records reports, marks equity, and builds summary
  output.
- Real risk: executable-order handling and newly-triggered-order handling
  duplicate the fill/rejection/apply/report/reservation path, which is exactly
  the type of path explosion cyclomatic complexity is designed to expose.
- Remediation:
  - Introduce a small internal runtime context dataclass only if it reduces
    parameter churn; otherwise use explicit helper parameters.
  - Extract `_process_tick_event(...)` to own active order scanning and return
    updated state, reservations, latest mark price, and bar-position facts.
  - Extract `_process_executable_order(...)` for match/reject/apply/record/
    reservation update. Reuse it for immediately executable orders and newly
    triggered orders.
  - Extract `_record_bar_close(...)` for `BarEvent`, strategy callback, equity
    curve, and exposure counters.
  - Extract `_build_backtest_result(...)` for summary/report/result assembly.
- Verification:
  - `uv run pytest tests/unit/backtest tests/smoke/local -q`
  - `uv run poe check-runtime`
  - `uv run poe mutation-trading` if trading behavior is touched indirectly.
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `_run_backtest` drops below 10 with no public result/report
  changes.

### 3. `_crossing_prices_for_segment` - `src/quantleet/backtest/execution_model.py:122` - `14 > 10`

- Classification: true positive.
- Why it is complex: a single loop handles executable limits, previously
  triggered stop-limits, dormant stop orders, stop-limit trigger and same-segment
  limit crossing, symbol filtering, open-state filtering, price range checks,
  and direction-aware sorting.
- Real risk: limit and stop-family candidate rules are coupled in one branchy
  method, so adding another order type or crossing rule will increase path count.
- Remediation:
  - Extract `_limit_crossing_candidate(order, start, low, high, triggered_ids)`.
  - Extract `_stop_crossing_candidates(order, start, end, low, high)`.
  - Keep direction sorting and duplicate removal in the original method.
  - Return a small tuple/result for stop-limit candidates that includes newly
    triggered unfilled stop-limit ids.
- Verification:
  - `uv run pytest tests/unit/backtest tests/unit/trading -q`
  - `uv run poe check-runtime`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: method drops below 10 while preserving existing conservative
  OHLCV execution semantics.

### 4. `_fetch_ohlcv_range` - `src/quantleet/integrations/venues/ccxt/market_data.py:120` - `14 > 10`

- Classification: true positive.
- Why it is complex: pagination, request limit calculation, page fetching,
  non-advancing provider defense, timestamp filtering, duplicate filtering,
  row conversion, limit depletion, and stop conditions all live in one loop.
- Real risk: pagination bugs are boundary-heavy; keeping cursor movement and row
  filtering together makes off-by-one and duplicate-row behavior harder to audit.
- Remediation:
  - Extract `_ohlcv_request_limit(remaining)`.
  - Extract `_time_bar_from_ohlcv_row(raw_row)`.
  - Extract `_append_page_rows(rows, page, cursor, end, remaining)` returning
    `(added, remaining, exhausted)`.
  - Extract `_next_ohlcv_cursor(page_last_timestamp, cursor)` for the
    non-advancing provider guard.
  - Preserve the direct `start is None` path.
- Verification:
  - `uv run pytest tests/unit/data tests/unit/integrations -q` if present.
  - `uv run pytest tests/smoke/local -q`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `_fetch_ohlcv_range` drops below 10 and pagination behavior
  remains byte-for-byte equivalent at the public `TimeBar` output level.

### 5. `grid_search` - `src/quantleet/research/parameter_exploration.py:243` - `12 > 10`

- Classification: true positive, moderate priority.
- Why it is complex: the method owns grid validation, objective validation,
  candidate preparation, constraint evaluation, backtest execution, construction
  error mapping, generic backtest error mapping, metric extraction, success row
  construction, and final result assembly.
- Real risk: new rejection stages or metrics behavior will add another try/except
  path to the same method.
- Remediation:
  - Extract `_prepare_grid_candidates(grid, config_type)`.
  - Extract `_evaluate_constraint(prepared, constraint, rows, fail_fast)`.
  - Extract `_run_grid_candidate(prepared, engine, bars, strategy, rows, fail_fast)`.
  - Extract `_extract_candidate_metrics(prepared, backtest, rows, fail_fast)`.
  - Keep `grid_search` as orchestration of validation and row accumulation.
- Verification:
  - `uv run pytest tests/unit/research -q`
  - `uv run poe check-runtime` because research runtime behavior is in scope.
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `grid_search` drops below 10 and rejection-stage semantics
  remain identical.

### 6. `collect_architecture_issues` - `src/quantleet/_repo_tools.py:746` - `12 > 10`

- Classification: true positive, low risk.
- Why it is complex: AST walking, import handling, import-from handling, domain
  dependency validation, and root-module validation are all inline.
- Real risk: architecture checks will grow as package boundaries grow; keeping
  AST node handling inline makes future rules harder to add safely.
- Remediation:
  - Extract `_collect_import_node_issues(path, module_parts, source_domain, node)`.
  - Extract `_collect_import_from_node_issues(path, module_parts, source_domain, node)`.
  - Extract `_collect_target_dependency_issues(path, module_parts, source_domain, target_parts)`.
  - Keep `collect_architecture_issues` as path iteration plus AST dispatch.
- Verification:
  - `uv run pytest tests/structure/architecture -q`
  - `uv run python scripts/repo_check.py`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `collect_architecture_issues` drops below 10.

### 7. `OrderIntent.__post_init__` - `src/quantleet/trading/domain/intents.py:25` - `12 > 10`

- Classification: true positive, Tier A.
- Why it is complex: quantity validation, limit-order shape, stop-family required
  fields, stop-market forbidden fields, stop-limit required fields, and
  non-stop forbidden trigger fields are all inline.
- Real risk: the same stop-family shape rules also appear in `Order` and
  partially in `PendingOrderRequest`, so future order-type changes can diverge.
- Remediation:
  - Introduce shared pure validators in the trading domain module, for example:
    - `_validate_positive_quantity(label, quantity)`
    - `_validate_stop_family_shape(...)`
    - `_validate_non_stop_shape(...)`
    - `_validate_limit_shape(...)`
  - Keep public dataclass fields and error messages unchanged.
  - Avoid moving validation outside construction unless tests prove behavior is
    identical.
- Verification:
  - Requires Tier A approval before implementation.
  - `uv run pytest tests/unit/trading/test_orders.py tests/unit/trading/test_contracts.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe check-runtime`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `OrderIntent.__post_init__` drops below 10 while preserving
  construction-time invariant enforcement.

### 8. `Order.__post_init__` - `src/quantleet/trading/domain/orders.py:32` - `15 > 10`

- Classification: true positive, Tier A.
- Why it is complex: it repeats order-shape validation from `OrderIntent` and
  adds filled-quantity and triggered-state invariants.
- Real risk: duplicated validation across `OrderIntent` and `Order` can drift,
  and C90 correctly highlights the path count of construction-time invariants.
- Remediation:
  - Reuse the same shared validators created for `OrderIntent`.
  - Extract `_validate_filled_quantity(quantity, filled_quantity)`.
  - Extract triggered-state validation into the non-stop/stop-family shape helper
    or a small dedicated helper if that keeps error messages clearer.
  - Keep `Order.from_intent` unchanged unless a test exposes duplication that
    should move there.
- Verification:
  - Requires Tier A approval before implementation.
  - `uv run pytest tests/unit/trading/test_orders.py tests/unit/trading/test_contracts.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe check-runtime`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `Order.__post_init__` drops below 10 and shares invariant
  enforcement with `OrderIntent`.

### 9. `PendingOrderRequest.__post_init__` - `src/quantleet/trading/order_requests.py:28` - `16 > 10`

- Classification: true positive, Tier A.
- Why it is complex: request sizing-mode validation, fixed quantity validation,
  percent sizing validation, limit order shape, stop-family shape, numeric price
  validation, and non-stop forbidden fields are all inline.
- Real risk: request-level validation partially overlaps domain-order validation
  but uses different field names (`stop_price` vs `trigger_price`) and sizing
  semantics, so a careless extraction can change public strategy ergonomics.
- Remediation:
  - Extract `_validate_request_sizing(quantity, qty_percent)`.
  - Extract `_validate_request_price_fields(order_type, stop_price, limit_price, trigger_condition)`.
  - Reuse generic `_is_finite_number` and, only where field names match the
    public error contract, shared order-shape helpers.
  - Keep `to_order_intent` unchanged and covered by existing tests.
- Verification:
  - Requires Tier A approval before implementation.
  - `uv run pytest tests/unit/trading/test_contracts.py tests/unit/trading/test_sizing.py tests/unit/research/test_strategy_surface.py -q`
  - `uv run poe mutation-trading`
  - `uv run poe check-runtime`
  - `uv run ruff check src tests scripts --select C90`
- Expected outcome: `PendingOrderRequest.__post_init__` drops below 10 without
  changing public strategy order intake behavior.

## Proposed Implementation Order

1. `_repo_tools.py` doc and architecture checks.
   - Lowest runtime risk.
   - Clears the `60 > 10` outlier first.
2. `grid_search` and `_fetch_ohlcv_range`.
   - Moderate risk; both can be tested with targeted non-Tier-A suites.
3. `_crossing_prices_for_segment` and `_run_backtest`.
   - Runtime-sensitive backtest behavior; requires `check-runtime`.
4. Trading validators.
   - Tier A; requires explicit approval record and mutation/runtime checks.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for future implementation:
  - No remaining non-exempt `C901` findings.
  - No raised C90 threshold.
  - No new `C901` `noqa` without a written false-positive rationale.
  - Existing public error messages remain unchanged unless explicitly approved.
  - Runtime-sensitive and Tier A verification commands are run for their slices.
- Acceptance artifact location:
  - This plan plus per-slice updates in the relevant active plan.
- Checks the evaluator will use:
  - `uv run ruff check src tests scripts --select C90 --statistics`
  - `uv run ruff check .`
  - `uv run poe check`
  - Slice-specific targeted tests listed above.
  - `uv run poe check-runtime` for backtest/research runtime-sensitive slices.
  - `uv run poe mutation-trading` for Tier A trading slices.
- Auto-fail conditions:
  - Threshold raised to hide findings.
  - Remaining true positives suppressed with `noqa`.
  - Tier A trading implementation without an approval record.
  - Behavior-changing refactor without targeted regression evidence.

## Generator Work Log

- Planned and executed slice order:
  - Worker A split repository document and architecture checks in
    `_repo_tools.py`.
  - Worker B split CCXT OHLCV pagination helpers and research grid-search
    candidate/error handling.
  - Worker C split backtest runtime accounting/executable-order processing and
    execution-model crossing candidate selection.
  - Worker D split Tier A trading order/request validators and kept public
    dataclass construction contracts intact.
  - Parent orchestration added the `C90` gate, kept the single confirmed
    `_validate_config_value` false-positive exception, added review-requested
    trading boundary/message contract tests, and handled final verification.
- Notes:
  - `_validate_config_value` remains the only confirmed false positive.
  - The 9 listed findings were treated as true positives and refactored instead
    of suppressed.
  - `.coverage-baseline.json` was raised automatically by `poe check` and
    `poe check-runtime`; the automatic raise was reverted because baseline
    maintenance is outside this slice.
- Blockers or scope changes:
  - None remaining. Tier A approval is recorded above.

## Evaluator Review

- Findings:
  - Reviewer 1 found a blocker in `_crossing_prices_for_segment`: the extracted
    working-limit branch could fall through into stop-order handling when no
    limit crossing existed in the segment. Fixed by always continuing after
    working-limit processing.
  - Reviewer 1 and Reviewer 2 found an important issue in `_fetch_ohlcv_range`:
    row conversion occurred before cursor/end/duplicate skip filters. Fixed by
    applying skip filters on the raw timestamp before constructing `TimeBar`.
  - Reviewer 2 found a blocker in `.coverage-baseline.json`: runtime/default
    checks auto-raised the baseline. Fixed by restoring the previous baseline
    values after verification.
  - Reviewer 2 and Reviewer 3 found stale plan text. Fixed by updating this
    document from planning-only to implementation/evaluation status.
  - Reviewer 3 found important mutation-derived gaps for fractional
    `qty_percent`, subunit prices, invalid positive-price values, and public
    `PendingOrderRequest` error messages. Fixed in
    `tests/unit/trading/test_contracts.py`.
- Verification evidence:
  - `uv run ruff check src tests scripts --select C90 --statistics`: exit 0,
    no non-exempt findings.
  - `uv run ruff check .`: exit 0.
  - `uv run mypy src`: exit 0, no issues in 61 source files.
  - `uv run pytest tests/structure/repo tests/structure/architecture tests/unit/research tests/unit/data tests/unit/integrations tests/unit/backtest tests/smoke/local tests/unit/trading tests/unit/research/test_strategy_surface.py -q`:
    exit 0, 594 passed, 1 warning.
  - `uv run pytest tests/unit/trading/test_contracts.py -q`: exit 0, 40 passed.
  - `uv run poe mutation-trading`: exit 0, 764 mutants, 670 killed, 94 survived.
    The review-targeted `order_requests` survivor group was removed; remaining
    survivors are outside the C90 remediation scope or are message-only domain
    helper survivors.
  - `uv run poe check-runtime`: exit 0, including 812 passed, 4 skipped,
    diff coverage 96%, build/twine/repo/notebook/perf checks passed.
  - `uv run poe check`: exit 0, including 812 passed, 4 skipped, diff coverage
    96%, build/twine/repo/notebook checks passed.
- Final disposition:
  - Complete. `C90` is part of the Ruff gate, the default threshold remains 10,
    the only `C901` suppression is the documented `_validate_config_value` false
    positive, and all non-exempt findings have been remediated.
