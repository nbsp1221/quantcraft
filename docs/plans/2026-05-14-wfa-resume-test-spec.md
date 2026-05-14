# WFA Resume Test Spec Authoring

- Date: 2026-05-14
- Task: Write the Stage 4 WFA resume test scenario specification
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Turn the Stage 4 WFA resume product contract into a test scenario
  specification that defines behavior-focused unit, integration, structure,
  smoke, and regression coverage without expanding product scope.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/walk-forward-analysis-resume.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/direct-backtest-class-config-api-test-scenarios.md`
  - `docs/references/testing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: the product spec is the source of truth for what
  WFA Stage 4 must prove; existing test scenario docs and testing reference
  define local style and placement; architecture and reliability docs define
  capability ownership, safety tier, and verification expectations.
- In-repo scope:
  - add `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - update `docs/product-specs/index.md`
  - update the active plan with evaluator findings and verification evidence
- Out-of-repo scope: web search for testing best-practice references only.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B research/backtest
  test planning documentation and does not modify `trading` or `execution`.
- Verification commands:
  - `git diff --check -- docs/product-specs/index.md docs/plans/2026-05-14-wfa-resume-test-spec.md`
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
- Success criteria:
  - test spec restates the product intent and external contracts
  - test scope does not add product features outside the WFA resume spec
  - normal flows, failure flows, edge cases, fixtures, fake policy, priorities,
    and success conditions are explicit
  - open questions are separated from confirmed behavior
  - product-spec index routes WFA test work to the new document
- Out of scope:
  - implementation planning
  - production code or test code changes
  - changing WFA product requirements
  - committing changes

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: verify that the new test spec
  is aligned with the WFA resume product spec, follows existing test scenario
  document conventions, and records fresh whitespace verification.
- Acceptance artifact location:
  `docs/plans/2026-05-14-wfa-resume-test-spec.md`
- How the generator and evaluator agreed on done before execution: this plan
  defines document scope, verification commands, and explicit non-goals before
  product-spec edits.
- Checks the evaluator will use:
  - compare new test requirements against
    `docs/product-specs/walk-forward-analysis-resume.md`
  - inspect product-spec index routing
  - run diff whitespace checks
- Auto-fail conditions:
  - the test spec requires unsupported WFA features such as multi-symbol,
    source-backed input, stitched OOS equity, pandas-only output, callable
    objectives, or threshold-based diagnostics
  - the test spec authorizes Tier A trading/execution changes
  - verification is not run from the current repository state

## Generator Work Log

- Planned slice order:
  1. Review product spec and existing test scenario patterns. Completed.
  2. Consult external testing best-practice references. Completed.
  3. Add WFA resume test scenario document. Completed.
  4. Update product-spec routing index. Completed.
  5. Run verification and record evaluator findings. Completed.
- Notes:
  - External references consulted: Google Testing Blog behavior-focused tests
    and Martin Fowler's practical test pyramid.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocker findings.
  - The new test spec stays within the Stage 4 WFA resume product contract:
    single-symbol materialized `BarSeries`, rolling bar-count windows,
    objective tuples, class-plus-config strategy construction, independent OOS
    summaries, factual diagnostics, and portable records.
  - The spec explicitly marks out-of-scope items as non-test targets instead
    of requiring unsupported product behavior.
  - Product-spec routing now points WFA test work to the new test scenario
    document.
- Verification evidence:
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/wfa-prerequisite-roadmap.md`
    completed with exit 0 and no output.
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    new file differs from `/dev/null`.
  - `git diff --check --no-index /dev/null docs/plans/2026-05-14-wfa-resume-test-spec.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    new file differs from `/dev/null`.
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    WFA resume product spec is currently untracked relative to Git.
- Final disposition: complete
