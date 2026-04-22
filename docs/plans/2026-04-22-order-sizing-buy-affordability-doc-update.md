- Date: `2026-04-22`
- Task: `Align buy-side qty_percent semantics with budget-first affordability clamp`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Update the order-sizing spec and implementation plan so buy-side
    `qty_percent` is documented as a requested position-budget percentage with
    fee-aware affordability clamping, rather than as a percent applied after a
    pre-subtracted fee reserve.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the current shipped research/backtest behavior, the architecture
    seam that keeps runtime orders quantity-only, and the future-only sizing
    spec and implementation plan that must stay internally consistent.
- In-repo scope:
  - Modify `docs/product-specs/order-sizing.md`.
  - Modify `docs/plans/2026-04-22-order-sizing-implementation-plan.md`.
  - Record evaluator findings and verification evidence in this active plan.
- Out-of-repo scope:
  - No Python implementation changes.
  - No new external research beyond already established best-practice context.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `thread user`
    - Human approver: `thread user`
    - Verification marker:
      explicit thread request to update the documents to the budget-first,
      fee-aware clamp interpretation
    - Granted scope:
      docs-only semantic update for the future `qty_percent` sizing slice
    - Expiration:
      end of this `2026-04-22` docs slice
    - Audit reference:
      this active plan and the updated spec/implementation-plan documents
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The spec says buy-side `qty_percent` is applied to reserved-adjusted quote
    cash as the requested position budget, not to a fee-pre-reduced budget.
  - The spec says fees are checked after budget calculation and only clamp size
    when needed for affordability.
  - The implementation plan mirrors that same semantic and names the tests that
    should freeze it.
  - No document reintroduces raw percent fields into runtime `Order`.
- Out of scope:
  - Any code changes
  - Any shipped-status routing changes
  - Any new target-percent or leverage semantics

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only when the buy-side semantic described in chat can be read
    directly from the updated documents without relying on unstated intent.
- Acceptance artifact location:
  - `docs/product-specs/order-sizing.md`
  - `docs/plans/2026-04-22-order-sizing-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - Done means both documents answer:
    1. what percent is applied to on the buy side
    2. when fees enter the calculation
    3. whether exact requested budget is preserved when affordable
    4. how over-allocation is prevented without a `100%` special case
- Checks the evaluator will use:
  - Diff the updated docs against the prior fee-pre-subtraction wording.
  - Check consistency between the product spec and implementation plan.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The spec and plan disagree on buy-side arithmetic order.
  - The wording implies `100%` receives a special-case hardcoded rule.
  - The update weakens the quantity-only runtime-order boundary.

## Generator Work Log

- Planned slice order:
  1. Update the product spec wording for buy-side semantics.
  2. Update the implementation plan wording and test expectations.
  3. Run repo/document verification.
  4. Record evaluator findings here.
- Notes:
  - This is a docs-only semantic hardening slice.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
- Updated `docs/product-specs/order-sizing.md` so buy-side `qty_percent`
  now reads as a requested position-budget percentage of reserved-adjusted
  quote cash, with fee-aware affordability checked after the requested budget
  is computed.
- The spec now says requested budget should be preserved exactly when
  affordable and clamped only when fees or execution costs would otherwise
  over-allocate capital.
- The spec now states explicitly that this is a general affordability clamp,
  not a special-case rule for `qty_percent=100`.
- Updated
  `docs/plans/2026-04-22-order-sizing-implementation-plan.md` to mirror the
  same arithmetic order and to freeze it in unit/integration tests, including:
  exact-budget preservation for affordable `buy(qty_percent=50)` and clamp
  behavior for `buy(qty_percent=100)` when fees would cause overspend.
- Verification evidence:
- `uv run poe repo-check`
  -> `repository checks passed`
- Final disposition:
- `complete`
