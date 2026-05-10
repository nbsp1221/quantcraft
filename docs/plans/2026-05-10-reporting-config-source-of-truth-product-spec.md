# Reporting Config Source Of Truth Product Spec Plan

- Date: 2026-05-10
- Task: Reporting Config Source Of Truth product spec
- Status: `completed`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Add a product spec that defines Stage 3 reporting config provenance:
  report metadata must use `StrategyConfig` snapshots as the single source of
  truth and remove the old `Strategy.parameters()` / `strategy_parameters`
  reporting contract.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/strategy-configuration-contract.md`
  - `docs/product-specs/strategy-configuration-contract-test-scenarios.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - `AGENTS.md` defines the planner/generator/evaluator workflow and
    repo-local verification contract.
  - `README.md` defines the first-beta public scope and documents `result.report`
    and `ParameterStudy` as beta surfaces.
  - `ARCHITECTURE.md` and package-topology docs define `strategy` as the shared
    strategy/config owner and `backtest` as historical runtime/reporting owner.
  - `strategy-configuration-contract.md` defines the canonical
    `StrategyConfig` contract and names Stage 3 reporting source-of-truth work.
  - `strategy-configuration-contract-test-scenarios.md` records downstream
    Stage 3 test hooks.
  - `wfa-prerequisite-roadmap.md` orders this work before WFA resumes.
  - `parameter-exploration.md` and `research-ergonomics.md` define the current
    study and research surfaces that must not silently disagree with reports.
  - `backtest-mvp.md` governs the current result/report baseline.
  - `RELIABILITY.md` and `SECURITY.md` define verification and safety-tier
    expectations.
- In-repo scope:
  - Create `docs/product-specs/reporting-config-source-of-truth.md`.
  - Update `docs/product-specs/index.md` to route Stage 3 reporting work to the
    new product spec.
  - Record evaluator review and verification evidence in this plan.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This is Tier B product
  documentation for `strategy`, `research`, and `backtest` behavior; it does
  not touch Tier A `trading` or `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check -- docs/product-specs/reporting-config-source-of-truth.md docs/product-specs/index.md docs/plans/2026-05-10-reporting-config-source-of-truth-product-spec.md`
- Success criteria:
  - The new product spec captures the user-confirmed Stage 3 decisions:
    `Strategy.parameters()` is removed, report-facing `strategy_parameters` is
    replaced by `strategy_config`, aliases are not retained, managed current
    docs/examples/tests/notebooks must migrate, and historical/audit documents
    are the only exception.
  - The spec stays product-level: it defines what and why, not low-level
    implementation mechanics.
  - The spec explicitly keeps new metadata APIs, WFA implementation, and
    `BacktestEngine.run(strategy=StrategyClass, config=...)` out of Stage 3.
  - Open questions are limited to unresolved future product choices and do not
    reopen decisions already made for Stage 3.
  - The product spec index routes reporting config source-of-truth work to the
    new spec.
- Out of scope:
  - Code changes.
  - Test-spec authoring.
  - Implementation-plan authoring for Stage 3.
  - Changelog updates.
  - WFA implementation or WFA resume spec.
  - Direct backtest class+config API implementation.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the new product spec against the planner contract, governing docs,
    and user-confirmed decisions from the Stage 3 alignment discussion.
  - Confirm the document distinguishes current managed docs/examples/tests from
    historical/audit records.
  - Confirm the document does not smuggle in a new metadata API, WFA behavior,
    or direct-run class+config API implementation.
  - Confirm verification evidence is fresh from the final working tree.
- Acceptance artifact location:
  - This plan's `## Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - Generator must write only the product spec, routing index update, and this
    active plan.
  - Evaluator must reject compatibility aliases for `strategy_parameters` or
    `Strategy.parameters()` in the Stage 3 contract.
- Checks the evaluator will use:
  - Review `docs/product-specs/reporting-config-source-of-truth.md`.
  - Review `docs/product-specs/index.md`.
  - Run `uv run poe repo-check`.
  - Run the listed `git diff --check` command.
- Auto-fail conditions:
  - The spec keeps `Strategy.parameters()` as a canonical or compatibility
    reporting source.
  - The spec keeps `strategy_parameters` as a report-facing alias.
  - The spec adds arbitrary custom report metadata as part of Stage 3.
  - The spec requires WFA implementation in Stage 3.
  - The spec requires `BacktestEngine.run(strategy=StrategyClass, config=...)`
    in Stage 3.
  - Verification fails without a recorded blocker.

## Generator Work Log

- Planned slice order:
  1. Read governing docs and current Stage 3 hooks.
  2. Create this active plan.
  3. Create the Stage 3 product spec.
  4. Update the product spec routing index.
  5. Run verification.
  6. Record evaluator review.
- Notes:
  - The product spec is based on the prior Stage 3 alignment discussion and the
    existing `StrategyConfig` / `ParameterStudy` migration contracts.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The new product spec records Stage 3 as a reporting provenance cleanup, not
    as an implementation plan.
  - The spec preserves the user-confirmed decisions: no
    `Strategy.parameters()` canonical surface, no report-facing
    `strategy_parameters` alias, `strategy_config` as a plain
    `StrategyConfig` snapshot, managed current docs/examples/tests/notebooks
    migrated, and historical/audit records exempt only when they are not
    current product authority.
  - The spec keeps custom metadata APIs, WFA behavior, and direct
    `BacktestEngine.run(strategy=StrategyClass, config=...)` API work outside
    Stage 3.
  - Follow-on decisions from the external finance-library comparison and
    alignment pass are resolved in the product spec, leaving no open product
    questions that block the Stage 3 test spec.
  - The product spec routing index now points reporting config source-of-truth
    work at the new governing product spec.
- Verification evidence:
  - `uv run poe repo-check`
    - Output: `repository checks passed`
  - `git diff --check -- docs/product-specs/reporting-config-source-of-truth.md docs/product-specs/index.md docs/plans/2026-05-10-reporting-config-source-of-truth-product-spec.md`
    - Output: no whitespace errors
- Final disposition:
  - Accepted for this product-spec authoring slice.
