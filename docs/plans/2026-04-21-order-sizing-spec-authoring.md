- Date: `2026-04-21`
- Task: `Author the first product spec draft for explicit percentage-based order sizing`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Write a future-facing product spec under `docs/product-specs/` for the
    first explicit percentage-based order-sizing slice, covering the public
    UX, semantic basis, resolution rules, and deliberate deferrals.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, the current shipped backtest and research
    behavior, the architecture and dependency boundaries, the canonical
    backtest execution semantics, and the Tier A safety policy for trading
    domain work.
- In-repo scope:
  - Add one new product spec draft under `docs/product-specs/`.
  - Update the product-spec routing index so the spec is discoverable.
  - Update this active plan with evaluator findings and verification evidence.
- Out-of-repo scope:
  - No Python implementation changes.
  - No network-dependent product research beyond already completed local work
    and previously reviewed official documentation.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `thread user`
    - Human approver: `thread user`
    - Verification marker:
      explicit thread request to author a first product spec draft for
      percentage-based order sizing
    - Granted scope:
      docs-only product-spec authoring for the next `trading` sizing slice,
      including routing-index updates and local code/doc review
    - Expiration:
      end of this `2026-04-21` docs-authoring slice
    - Audit reference:
      this active plan and the resulting product-spec draft
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains one coherent product spec draft for explicit
    order-sizing percentages.
  - The spec clearly distinguishes current quantity-only behavior from the
    proposed next slice.
  - The product-spec routing index points to the new spec.
  - `uv run poe repo-check` passes after the doc changes.
- Out of scope:
  - Any implementation plan for code changes
  - Any Python behavior changes
  - Portfolio-target or rebalance semantics
  - Margin or buying-power modeling

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the new spec is specific enough to guide later
    implementation and review, yet narrow enough to avoid silently expanding
    into portfolio-target sizing or full execution design.
- Acceptance artifact location:
  - `docs/product-specs/order-sizing.md`
- How the generator and evaluator agreed on done before execution:
  - Done means the new spec answers:
    1. what public UX is being proposed
    2. what `qty_percent` means for buys and sells
    3. when percent sizing resolves into concrete quantity
    4. what remains explicitly deferred
- Checks the evaluator will use:
  - Compare the spec against the current code truth and current governing docs.
  - Check that the new routing-index row is discoverable and correctly marked.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The spec rewrites current implemented behavior instead of describing a
    future slice.
  - The spec overloads `quantity` instead of keeping it distinct from
    percentage sizing.
  - The spec quietly introduces portfolio-target semantics.
  - Routing-index discoverability or repo checks fail.

## Generator Work Log

- Planned slice order:
  1. Review current product-spec and design-doc style.
  2. Write the new order-sizing product spec draft.
  3. Add a routing-index row in `docs/product-specs/index.md`.
  4. Run `uv run poe repo-check`.
  5. Record evaluator findings and verification evidence here.
- Notes:
  - This is a docs-only slice.
  - The spec should preserve the current architectural rule that runtime
    `Order` remains quantity-based.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
- Added `docs/product-specs/order-sizing.md` as a future-facing product spec
  draft for the first explicit `qty_percent` sizing slice.
- The draft keeps the current architectural seam intact:
  strategy-facing intent may carry percent sizing, but runtime `Order` remains
  quantity-based.
- The spec fixes one explicit meaning for `qty_percent` in the current slice:
  - buy-side percent resolves against available cash
  - sell-side percent resolves against current position quantity
- The draft explicitly defers portfolio-target semantics, buying-power
  semantics, and strategy-level default sizing declarations.
- Added a `Future-only` routing row in `docs/product-specs/index.md` so the
  spec is discoverable without being mistaken for current implemented
  authority.
- Verification evidence:
- `uv run poe repo-check`
  -> `repository checks passed`
- Final disposition:
- `complete`
