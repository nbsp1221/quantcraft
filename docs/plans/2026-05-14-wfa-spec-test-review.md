# WFA Product And Test Spec Review

- Date: 2026-05-14
- Task: Review Stage 4 WFA product and test specs before technical
  implementation planning
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Orchestrate independent third-party reviews of the Stage 4 WFA product
  spec and test scenario spec, apply obvious clarification fixes, and identify
  questions that require human product judgment before technical implementation
  planning.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/walk-forward-analysis-resume.md`
  - `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - `docs/references/testing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: the WFA product and test specs are the review
  subject; repo workflow and architecture docs define planning, ownership,
  safety tier, and verification expectations.
- In-repo scope:
  - review and, if needed, clarify
    `docs/product-specs/walk-forward-analysis-resume.md`
  - review and, if needed, clarify
    `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - update this active plan with review synthesis and verification evidence
- Out-of-repo scope: none
- Tier A progression requested: `no`
- Approval record, if required: not required; this is Tier B research/backtest
  documentation review.
- Verification commands:
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/wfa-prerequisite-roadmap.md docs/product-specs/walk-forward-analysis.md`
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume.md`
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - `git diff --check --no-index /dev/null docs/plans/2026-05-14-wfa-spec-test-review.md`
- Success criteria:
  - at least three independent reviewer perspectives are collected
  - findings are synthesized and deduplicated
  - obvious non-product-scope clarification fixes are applied
  - product-scope or trade-off decisions are left as human questions
  - specs are clear enough for technical implementation planning or remaining
    blockers are explicitly named
- Out of scope:
  - writing the technical implementation plan
  - production code or test code changes
  - changing product scope without human confirmation
  - committing changes

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: verify that review synthesis
  reflects subagent evidence, direct edits remain clarifying only, and
  whitespace verification is fresh.
- Acceptance artifact location:
  `docs/plans/2026-05-14-wfa-spec-test-review.md`
- How the generator and evaluator agreed on done before execution: this plan
  defines reviewer count, allowed edits, human-question boundaries, and
  verification before any document changes.
- Checks the evaluator will use:
  - inspect subagent findings and synthesis
  - inspect final diff for scope expansion
  - run diff whitespace checks
- Auto-fail conditions:
  - fewer than three independent review perspectives are collected
  - direct edits introduce unsupported WFA behavior such as source-backed input,
    stitched OOS account output, callable objectives, or threshold-based
    diagnostics
  - human product/trade-off decisions are silently resolved
  - verification is not run from the current repository state

## Generator Work Log

- Planned slice order:
  1. Read orchestration and document-review skill guidance. Completed.
  2. Create active review plan. Completed.
  3. Dispatch independent read-only reviewer agents. Completed.
  4. Synthesize findings and classify auto-fix versus human question.
     Completed.
  5. Apply obvious clarification edits only. Completed.
  6. Verify and record evaluator review. Completed.
- Notes:
  - Reviewers receive only the two target spec paths plus a short review lens
    to avoid overloading them with previous discussion.
- Blockers or scope changes:
  - None.

## Subagent Review Synthesis

- Reviewers used:
  - Product and requirements consistency reviewer: checked whether WFA's
    what/why, user intent, goals, non-goals, and contracts are coherent.
  - Test quality reviewer: checked whether tests target observable contracts,
    use appropriate levels, and avoid implementation coupling.
  - Edge case and failure scenario reviewer: checked missing boundaries,
    invalid inputs, failure flows, and failure-semantics contradictions.
  - Implementation risk reviewer: checked ambiguity, scope/resource risk,
    architecture risk, and implementation-plan blockers.
- Major findings:
  - Constraint callback examples conflicted with the existing `ParameterStudy`
    mapping-based constraint contract. Resolved by documenting mapping syntax.
  - Candidate-row failures and fold-level failures were overloaded in product
    text. Resolved by distinguishing retained train `GridSearchResult` row
    states from public fold failure status.
  - "No eligible row" used ambiguous "unselected or failed" language.
    Resolved by fixing the public fold status to `failed` with selection-stage
    reason.
  - Inherited `ParameterStudy.max_candidates` timing was inconsistent.
    Resolved as strict preflight before any fold starts when raw counts are
    knowable.
  - Invalid engine input and empty parameter value lists were missing from test
    boundaries. Added explicit coverage.
  - Record export wording conflicted with existing nested
    `candidate_parameters`/`strategy_config` conventions. Resolved by keeping
    top-level metadata/metric keys flat while nesting config snapshots.
  - Zero successful OOS folds needed explicit summary expectations. Added
    count/failure-rate-only expectation with no fabricated numeric aggregates.
  - Fresh strategy tests risked over-asserting constructor counts. Clarified
    that the durable contract is no state/config leakage.
- Human-decision findings carried forward:
  - Closed on 2026-05-14 by user decision: fold-level selected config snapshots
    are sufficient first-slice parameter-stability evidence; no separate
    stability summary is required for Stage 4.
  - Closed on 2026-05-14 by user decision: keep full train `GridSearchResult`
    and selected test `BacktestResult` retention paired with unlimited default
    WFA total-run cap; large runs remain user responsibility unless explicit
    caps are supplied.
  - Exact public module/type exports, public field names, timestamp record
    representation, diagnostic code strings, and no-trade diagnostic severity
    before concrete tests are written.

## Evaluator Review

- Findings:
  - No blocker findings after clarification edits.
  - Direct edits were limited to clarifying existing product/test intent and
    aligning WFA with existing `ParameterStudy`/record conventions.
  - Product-scope and resource trade-off decisions remain explicit open
    questions instead of being silently resolved.
- Verification evidence:
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/wfa-prerequisite-roadmap.md docs/product-specs/walk-forward-analysis.md`
    completed with exit 0 and no output.
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    new file differs from `/dev/null`.
  - `git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    new file differs from `/dev/null`.
  - `git diff --check --no-index /dev/null docs/plans/2026-05-14-wfa-spec-test-review.md`
    completed with no output; exit 1 is expected for `--no-index` because the
    new file differs from `/dev/null`.
- Final disposition: complete
