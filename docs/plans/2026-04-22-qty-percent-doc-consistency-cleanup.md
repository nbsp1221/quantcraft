# Active Plan

- Date: `2026-04-22`
- Task: `Clean up qty_percent documentation consistency before commit`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Reconcile shipped `qty_percent` docs, routing, and plan artifacts so the
    repository is internally consistent and commit-ready after the feature
    implementation.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, the current shipped backtest/research
    contracts, the shipped `qty_percent` product meaning, routing authority,
    and the repo-level reliability/documentation expectations that commit-ready
    docs must satisfy.
- In-repo scope:
  - Audit shipped product specs, repo-level docs, and qty-percent-related plan
    artifacts for stale wording, status mismatches, or missing shipped
    references.
  - Update only the docs and plan artifacts needed to make the repository
    internally consistent for commit readiness.
  - Record evaluator findings and fresh verification evidence in this active
    plan.
- Out-of-repo scope:
  - No Python implementation changes.
  - No external network or non-repo behavior changes.
- Tier A progression requested: `no`
- Approval record, if required:
  - not required; this slice is docs-only and does not change Tier A code
- Verification commands:
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_repository_entrypoint_docs.py -q`
  - `uv run poe repo-check`
  - `uv run poe verify-runtime`
- Success criteria:
  - Shipped `qty_percent` docs no longer contain stale future-only or pre-ship
    wording that conflicts with current implementation.
  - Qty-percent-related plan artifacts have status/final-disposition text that
    does not read as still-open work when the work is already complete.
  - Repo-level doc structure tests and repo checks pass from the current tree.
- Out of scope:
  - Any new feature work
  - Reopening `qty_percent` semantics
  - Adding new verification lanes or restructuring the test suite

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after a read-heavy audit plus fresh structure/repo
    verification show no remaining material qty-percent doc inconsistency that
    would make the pending commit misleading.
- Acceptance artifact location:
  - touched docs and plan files
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - Done means shipped qty-percent docs, routing, and related plan artifacts
    read coherently as current repository truth and pass the repo-local doc
    checks.
- Checks the evaluator will use:
  - line-by-line comparison between shipped specs and repo-level docs
  - read-only review fan-out synthesis
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_repository_entrypoint_docs.py -q`
  - `uv run poe repo-check`
  - `uv run poe verify-runtime`
- Auto-fail conditions:
  - a touched plan still reports `Status: active` while its own evaluator block
    closes it as complete
  - product-spec routing or shipped-status wording contradicts the current
    implementation
  - the slice is reported complete without fresh doc-check evidence

## Generator Work Log

- Planned slice order:
  1. Audit shipped product specs, repo docs, and qty-percent-related plan
     artifacts.
  2. Synthesize read-only review fan-out findings.
  3. Apply only the doc/plan edits needed for commit readiness.
  4. Run fresh structure/repo verification.
  5. Record evaluator findings and final disposition here.
- Notes:
  - Parent agent owns all writes.
  - Subagents stay read-only and must return evidence-backed findings only.
- Blockers or scope changes:
  - None yet.

## Evaluator Review

- Findings:
- No unresolved material qty-percent doc-consistency issues remain for commit
  readiness in the touched shipped-doc and plan set.
- Fixed one product-spec contradiction in
  `docs/product-specs/backtest-mvp.md`:
  the strategy surface already described pending order requests resolving into
  quantity-only `OrderIntent`, but the acceptance criteria still said strategy
  code emits `OrderIntent` directly.
- Tightened shipped-doc routing and authority readability:
  - `docs/product-specs/backtest-mvp.md` and
    `docs/product-specs/research-ergonomics.md` now list
    `docs/product-specs/order-sizing.md` in related documents.
  - `docs/product-specs/order-sizing.md` now reads as a shipped governing spec
    instead of partially future-tense proposal text in the flagged sections.
- Synced repo-entry docs with shipped behavior:
  - `README.md` now mentions shipped `qty_percent` support in the current
    implemented scope and notes the checked-in BTC-fixture `%` regressions.
  - `docs/RELIABILITY.md` now records the checked-in BTC-fixture `qty_percent`
    market/limit regressions as normal integration-lane examples.
- Hardened repo-level doc guards so these facts do not silently drift:
  - `tests/structure/repo/test_repository_entrypoint_docs.py` now locks the
    README and reliability references to shipped `qty_percent` coverage.
  - `tests/structure/repo/test_poe_task_contracts.py` fixture content now
    matches the shipped `docs/product-specs/index.md` row for
    `order-sizing.md`.
- Closed stale qty-percent plan artifacts that still reported `Status: active`
  despite completed evaluator blocks, and corrected the
  `verify-runtime`/`repo-check` evidence mix-up in
  `docs/plans/2026-04-22-qty-percent-canonical-regression-execution.md`.
- Verification evidence:
- `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_repository_entrypoint_docs.py tests/structure/repo/test_poe_task_contracts.py -q`
  -> `25 passed in 0.04s`
- `uv run poe repo-check`
  -> `repository checks passed`
- `uv run poe verify-runtime`
  -> `ruff check .` passed
  -> `mypy src` passed
  -> `pytest -q` => `360 passed, 3 skipped`
  -> coverage policy check passed at `92%`
  -> `uv build` passed
  -> `repository checks passed`
  -> notebook validation passed for 4 notebooks
  -> perf check passed:
     `test_rsi_backtest_steady_state_median_is_within_threshold` median about
     `120.8ms`
- Final disposition:
- `complete`
