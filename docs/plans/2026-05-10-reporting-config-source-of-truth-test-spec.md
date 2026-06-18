# Reporting Config Source Of Truth Test Spec Plan

- Date: 2026-05-10
- Task: Reporting Config Source Of Truth test spec
- Status: `completed`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Add a product-test spec that turns the Stage 3 reporting config
  source-of-truth product contract into observable test scenarios.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the planner/generator/evaluator workflow and
    repo-local verification contract.
  - `reporting-config-source-of-truth.md` is the source product contract for
    Stage 3.
  - The strategy configuration and parameter exploration specs define the
    upstream and downstream config snapshot vocabulary that reporting must
    align with.
  - `README.md`, `backtest-mvp.md`, and `research-ergonomics.md` define the
    beta user-facing report and research surfaces.
  - `ARCHITECTURE.md` and package-topology docs define ownership boundaries:
    `strategy` owns config semantics, `backtest` owns historical reporting,
    and `research` composes those surfaces for studies.
  - `RELIABILITY.md` and `SECURITY.md` define verification, safety tiers, and
    financial-safety boundaries.
- In-repo scope:
  - Create
    `docs/product-specs/reporting-config-source-of-truth-test-scenarios.md`.
  - Update `docs/product-specs/index.md` to route Stage 3 test work to the new
    test spec.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope:
  - Web search for testing-design guidance only. No external code or data is
    imported.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B product-test
  documentation for strategy, research, and backtest behavior; it does not
  touch Tier A `trading` or `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check -- docs/product-specs/reporting-config-source-of-truth-test-scenarios.md docs/product-specs/index.md docs/plans/2026-05-10-reporting-config-source-of-truth-test-spec.md`
- Success criteria:
  - The new test spec is derived from the Stage 3 product spec and does not add
    new product scope.
  - The spec covers normal flows, failure flows, edge cases, and migration
    regressions for `strategy_config`, `strategy_parameters`, and
    `Strategy.parameters()`.
  - The spec chooses test levels based on risk: unit tests for local contracts,
    integration tests for strategy/backtest/research boundaries, and structure
    or docs checks for managed-surface cleanup.
  - The spec states fixture, fake, mock, and assertion boundaries in a way that
    favors observable product behavior over private implementation details.
  - Open questions do not reopen Stage 3 decisions already resolved in the
    product spec.
  - The product spec index routes Stage 3 test work to the new test spec.
- Out of scope:
  - Code changes.
  - Test implementation.
  - Implementation-plan authoring.
  - WFA implementation.
  - Direct backtest class-plus-config API tests for the later API-alignment
    phase.
  - Changelog updates.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the new test spec against the planner contract, the Stage 3 product
    spec, and the existing product-test spec style.
  - Confirm the test spec validates external contracts rather than private
    implementation mechanics.
  - Confirm the test spec does not add arbitrary metadata APIs, WFA behavior,
    or direct-run class-plus-config API scope to Stage 3.
  - Confirm verification evidence is fresh from the final working tree.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - Generator must write only the test spec, routing index update, and this
    active plan.
  - Evaluator must reject any test requirement that keeps
    `strategy_parameters` as a compatibility alias or treats
    `Strategy.parameters()` as a valid report source.
- Checks the evaluator will use:
  - Review
    `docs/product-specs/reporting-config-source-of-truth-test-scenarios.md`.
  - Review `docs/product-specs/index.md`.
  - Run `uv run poe repo-check`.
  - Run the listed `git diff --check` command.
- Auto-fail conditions:
  - The spec tests implementation internals instead of observable contracts.
  - The spec adds a new metadata bag, WFA fold result shape, or direct
    class-plus-config backtest API to Stage 3.
  - The spec allows `strategy_parameters` to remain in current report
    contracts.
  - The spec allows `Strategy.parameters()` to affect report config.
  - Verification fails without a recorded blocker.

## Generator Work Log

- Planned slice order:
  1. Read the Stage 3 product spec and existing test-spec examples.
  2. Confirm external testing-design guidance with web search.
  3. Create this active plan.
  4. Create the Stage 3 product-test spec.
  5. Update the product spec routing index.
  6. Run verification.
  7. Record evaluator review.
- Notes:
  - External testing guidance checked: behavior-focused tests, layered test
    pyramid, and pytest fixture/integration guidance.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The new product-test spec derives from the Stage 3 product spec and keeps
    implementation, WFA, direct class-plus-config backtest API, arbitrary
    metadata, and changelog work out of scope.
  - The spec focuses tests on observable contracts: `report.run.strategy_config`
    as the plain config snapshot, absence of `strategy_parameters`, ignored
    `Strategy.parameters()` hooks, config-less `{}` behavior, and
    `ParameterStudy` row/report alignment.
  - The selected levels match the risk profile: unit tests for local field
    shape and negative contracts, integration tests for `strategy`/`backtest`/
    `research` composition, regression tests for old-surface removal, and
    structure/docs checks for managed current surfaces.
  - The fixture and fake policy prefers real Quantcraft objects at product
    boundaries and avoids private helper assertions.
  - The product spec routing index now points Stage 3 test work at the new
    product-test spec.
- Verification evidence:
  - `uv run poe repo-check`
    - Output: `repository checks passed`
  - `git diff --check -- docs/product-specs/reporting-config-source-of-truth-test-scenarios.md docs/product-specs/index.md docs/plans/2026-05-10-reporting-config-source-of-truth-test-spec.md`
    - Output: no whitespace errors
- Final disposition:
  - Accepted for this product-test-spec authoring slice.
