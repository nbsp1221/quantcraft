# Beta Documentation Status Sync

- Date: 2026-05-02
- Task: Align first-beta documentation with the current implemented reporting,
  plotting, and reservation behavior.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: User
- Owner: Codex

## Planner Contract

- Goal:
  - Replace stale beta-gap and planned-status wording where the implementation
    has already shipped `result.report`, `result.plot()`, plotting tests, and
    order reservation behavior.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-plotting-test-scenarios.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - The README and product specs define the current user-facing beta target and
    implemented scope. The design and reliability docs define the architecture,
    safety tier, and verification expectations for this documentation-only
    Tier B slice.
- In-repo scope:
  - Update stale docs that still describe implemented beta reporting, plotting,
    plotting tests, or order reservation behavior as planned or missing.
  - Keep remaining beta gaps focused on constrained parameter exploration,
    richer examples, fresh install guidance, and release metadata/docs.
- Out-of-repo scope:
  - No code behavior changes.
  - No package publishing.
  - No network-backed checks.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required. This slice edits documentation for Tier B research/backtest
    positioning and does not modify `trading` or `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - README no longer lists shipped reporting or plotting as remaining beta
    blockers.
  - Product routing no longer marks the plotting spec or test scenarios as not
    implemented.
  - Research ergonomics docs distinguish shipped reporting/plotting from
    remaining beta-positioning gaps.
  - Order reservation docs no longer call the implemented policy planned.
  - Repository/document structure checks pass.
- Out of scope:
  - Adding parameter exploration.
  - Adding examples or installation docs.
  - Changing runtime code or tests beyond documentation verification.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the diff against the planner contract and confirm the edited docs
    describe current implementation without claiming full beta readiness.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - The planner contract above fixes the exact stale documentation classes to
    update and the verification commands to run.
- Checks the evaluator will use:
  - Manual diff review.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - Docs claim broad first-beta readiness.
  - Docs imply parameter exploration, richer examples, or fresh install
    guidance already exist when they do not.
  - Documentation checks fail.

## Generator Work Log

- Planned slice order:
  1. Update beta-gap wording in README and research ergonomics docs.
  2. Update plotting spec and plotting test scenario status language.
  3. Update product-spec routing status language.
  4. Update order-reservation planned-policy wording.
  5. Run documentation verification and record evaluator findings.
- Notes:
  - This is a documentation-status sync only.
  - Updated README implemented-scope bullets for `result.report` and
    `result.plot()`.
  - Reframed remaining beta gaps around constrained parameter exploration,
    richer examples, fresh install guidance, and release
    metadata/documentation cleanup.
  - Marked plotting product and test-scenario specs as implemented.
  - Replaced planned order-reservation wording with implemented wording.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The edited docs no longer describe shipped reporting,
    plotting, plotting tests, or order reservation behavior as missing or
    planned. The docs still avoid claiming broad first-beta readiness.
- Verification evidence:
  - A stale-status `rg` search for previous "not yet implemented",
    "planned", and reporting/plotting beta-gap phrases exited with code `1`,
    meaning no matches.
  - `uv run poe repo-check` passed with output `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    output `67 passed in 0.16s`.
- Final disposition:
  - Accepted for this documentation-status sync.
