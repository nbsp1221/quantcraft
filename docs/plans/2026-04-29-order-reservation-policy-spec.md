# Order Reservation Policy Spec Plan

- Date: `2026-04-29`
- Task: `Document conservative order reservation policy`
- Status: `active`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Create a what/why product spec for the MVP order reservation policy:
    percent sizing resolves to fixed quantity before runtime `Order` creation,
    and accepted orders reserve required cash or position even when they are
    dormant stop-family orders.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, Tier A approval expectations, current
    strategy sizing behavior, stop-family order direction, package ownership,
    and the rule that runtime `Order` remains quantity-based.
- In-repo scope:
  - Add a product spec under `docs/product-specs/`.
  - Register the spec in `docs/product-specs/index.md`.
  - Update adjacent product specs only where needed to state the routing and
    authority relationship between current shipped behavior and the planned
    reservation-policy slice.
  - Keep the document focused on goal, why, success conditions, policy, and
    non-goals rather than implementation steps.
- Out-of-repo scope:
  - Read-only prior-art inspection of user-provided financial library clones
    under `/tmp` for order sizing and stop-order semantics.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: `Naki (thread user)`
  - Human approver: `Naki (thread user)`
  - Verification marker:
    explicit thread request on `2026-04-29` to create the what/why spec
    document for conservative order reservation policy.
  - Granted scope:
    in-repository documentation only, limited to product spec routing and the
    new order reservation policy spec; read-only inspection of `/tmp`
    financial-library clones for comparison evidence.
  - Expiration:
    end of this documentation slice; no code implementation, commit, PR,
    out-of-repo change is approved by this record.
  - Audit reference:
    this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The new spec states the goal, motivation, product policy, success
    conditions, and explicit non-goals.
  - The spec keeps `qty_percent` out of runtime `Order` and defines fixed
    quantity resolution before order creation.
  - The spec states the conservative MVP default: accepted orders reserve
    required cash or position even when dormant.
  - The spec separates MVP policy from later venue-specific `check_on_trigger`
    behavior.
  - The spec records the prior-art conclusion that mature engines keep stop
    orders quantity-based and resolve percent or target sizing before order
    submission or simulation execution.
  - Product spec routing remains valid.
- Out of scope:
  - Source code changes.
  - Tests for the future implementation.
  - Changing shipped `stop_limit` status.
  - Implementing `qty_percent + stop_limit` or `qty_percent + stop_market`.

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Accept only if the document answers what and why clearly, does not smuggle
    implementation changes, and passes the repo-local doc/architecture checks.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The generator may add one product spec and update the routing index only.
- Checks the evaluator will use:
  - Review the diff against the planner contract.
  - Confirm the new spec aligns with `order-sizing.md` and the
    quantity-based runtime `Order` direction.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The spec says `qty_percent` belongs on runtime `Order`.
  - The spec treats venue-specific `check_on_trigger` as the MVP default.
  - The spec silently changes live-trading scope.
  - The doc route is missing or invalid.

## Generator Work Log

- Planned slice order:
  - Create active plan.
  - Add product spec.
  - Register product spec in routing index.
  - Run repo-check.
- Notes:
  - The policy is documentation-only in this slice.
  - Subagent review fan-out ran on `2026-04-29` with product/coherence,
    architecture, implementation/testability, and venue-semantics lenses.
  - Accepted review findings clarified that this planned spec does not
    retroactively change current shipped behavior, that reservation ownership
    belongs to runtime/account control rather than runtime `Order`.
  - Follow-up human review corrected the stop-market scope: stop orders are
    trigger-conditioned versions of their child order type, so the planned
    policy includes `qty_percent + stop_market`; buy-side stop-market sizing
    anchors on `stop_price` plus modeled slippage.
  - Read-only prior-art inspection of local `/tmp` clones found the same broad
    boundary in `backtesting.py`, `backtrader`, `nautilus_trader`, `LEAN`,
    `lumibot`, `vectorbt`, and `freqtrade`: strategy or portfolio sizing may be
    percent/target/stake based, but order objects and broker submissions use
    concrete quantity or venue notional fields plus order-type prices.
- Blockers or scope changes:
  - Scope widened from only the new product spec plus routing index to include
    narrow relationship notes in `docs/product-specs/order-sizing.md` and
    `docs/product-specs/stop-limit.md`.

## Evaluator Review

- Findings:
  - No remaining findings for this documentation slice after subagent review
    synthesis and accepted edits.
- Verification evidence:
  - `uv run poe repo-check`: `repository checks passed`.
  - After follow-up stop-market scope correction, `uv run poe repo-check`:
    `repository checks passed`.
  - After adding the prior-art baseline from local `/tmp` source inspection,
    `uv run poe repo-check`: `repository checks passed`.
- Final disposition:
  - Accepted for the planned product-spec documentation slice.
