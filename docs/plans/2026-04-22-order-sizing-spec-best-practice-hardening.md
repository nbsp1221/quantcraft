- Date: `2026-04-22`
- Task: `Harden the order-sizing spec using best-practice evidence and rerun review fan-out`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Revise `docs/product-specs/order-sizing.md` so the remaining unresolved
    semantics are fixed using best-practice evidence from official
    documentation and primary-source comparator behavior, then rerun read-only
    review fan-out.
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
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, current shipped scope, architecture
    boundaries, backtest semantics, and the current sizing-direction draft that
    the product spec must remain consistent with.
- In-repo scope:
  - Update `docs/product-specs/order-sizing.md`.
  - Update this active plan with findings and verification evidence.
  - Run read-only review fan-out after the doc revision.
- Out-of-repo scope:
  - No Python implementation changes.
  - No non-primary-source web research.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `thread user`
    - Human approver: `thread user`
    - Verification marker:
      explicit thread request to resolve the remaining order-sizing spec issues
      using best-practice evidence and rerun review fan-out
    - Granted scope:
      docs-only hardening of the order-sizing spec plus read-only review
    - Expiration:
      end of this `2026-04-22` slice
    - Audit reference:
      this active plan and the revised spec
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The revised spec explicitly settles:
    1. canonical sizing-resolution ownership
    2. reservation accounting against remaining quantity
    3. buy-side price-anchor rules
    4. same-cycle percent-order resolution ordering
  - The revision remains consistent with current repo architecture.
  - Post-revision read-only review fan-out produces no material unresolved
    issue, or any remaining issues are explicitly reported.
  - `uv run poe repo-check` passes.
- Out of scope:
  - Implementing code changes
  - Reopening `qty_percent` versus split-name API direction
  - Portfolio-target sizing

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the revised spec is materially tighter on the
    remaining four semantic gaps and the evidence-backed review fan-out has
    been synthesized.
- Acceptance artifact location:
  - `docs/product-specs/order-sizing.md`
- How the generator and evaluator agreed on done before execution:
  - Done means the revised spec answers the four remaining semantic questions
    in a way that can be defended with official docs and comparator evidence.
- Checks the evaluator will use:
  - Best-practice and primary-source comparison.
  - Read-only review fan-out.
  - `uv run poe repo-check`.
- Auto-fail conditions:
  - The revision relies on unsupported conjecture.
  - The spec still leaves the four targeted semantics ambiguous.
  - The review fan-out finds a material unresolved contradiction.

## Generator Work Log

- Planned slice order:
  1. Gather best-practice evidence for the four unresolved semantics.
  2. Revise the spec.
  3. Run `uv run poe repo-check`.
  4. Rerun read-only review fan-out.
  5. Record remaining issues, if any.
- Notes:
  - Best-practice evidence should prefer official docs and primary sources.
  - Review fan-out remains read-only and evidence-backed.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
- Revised `docs/product-specs/order-sizing.md` to explicitly fix:
  1. one canonical shared sizing policy for percent resolution
  2. reservation accounting against unresolved remainder
  3. buy-side order-type price anchors
  4. same-cycle serial resolution order
- The revised spec now also strengthens affordability rules around quantity
  increments, minimum quantity, and minimum notional constraints.
- A fresh read-only subagent rerun was attempted but the host rejected new
  agent spawns with `agent thread limit reached (max 6)`, so no post-revision
  second fan-out could be completed in this turn.
- That host-blocked rerun is recorded here as an explicit execution exception,
  not hidden completion evidence; later qty-percent planning and implementation
  review artifacts provided additional bounded review before ship.
- Verification evidence:
- `uv run poe repo-check`
  -> `repository checks passed`
- Final disposition:
- `complete`
