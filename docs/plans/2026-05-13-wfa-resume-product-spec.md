# Active Plan

- Date: 2026-05-13
- Task: Stage 4 WFA Resume product spec authoring
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: create and refine a Stage 4 product spec that resumes walk-forward
  analysis planning from the completed strategy config, reporting, and direct
  backtest prerequisites.
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/direct-backtest-class-config-api.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/reporting-config-source-of-truth.md`
  - `docs/design-docs/package-topology-and-naming.md`
- Why these are governing: they define the first-beta scope, capability
  topology, WFA pause reason, prerequisite roadmap, and the canonical strategy
  construction and reporting contracts that Stage 4 must compose.
- In-repo scope:
  - add a WFA resume product spec under `docs/product-specs/`
  - update product-spec routing and roadmap links
  - record planner and evaluator evidence in this plan
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; this is research/product-spec
  documentation and does not change `trading` or `execution`.
- Verification commands:
  - `git diff --check -- docs/product-specs docs/plans/2026-05-13-wfa-resume-product-spec.md`
- Success criteria:
  - the new product spec focuses on what/why, not implementation how
  - it reflects the user's confirmed Stage 4 decisions
  - unresolved product decisions remain in a human-review section until they
    are closed
  - once the remaining questions are closed, the product spec records no open
    Stage 4 resume product questions
  - existing WFA routing points readers to the Stage 4 resume spec
- Out of scope:
  - WFA implementation
  - WFA test-scenarios spec
  - technical implementation plan
  - objective alias registry design
  - continuous OOS account semantics

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: compare the doc changes against
  the governing WFA roadmap and confirmed grill-me decisions, then run the
  doc-focused whitespace verification.
- Acceptance artifact location:
  `docs/plans/2026-05-13-wfa-resume-product-spec.md`
- How the generator and evaluator agreed on done before execution: the plan
  defines the target files, success criteria, and excluded implementation work.
- Checks the evaluator will use:
  - content review for required product-spec sections
  - routing/link review across product-spec index and roadmap
  - `git diff --check`
- Auto-fail conditions:
  - authorizes implementation directly
  - reopens completed Stage 3.5 strategy construction decisions
  - treats `oos_summary` as a continuous account report
  - hides unresolved decisions instead of listing open questions

## Generator Work Log

- Planned slice order:
  1. Add Stage 4 WFA resume product spec.
  2. Link it from product-spec routing and roadmap documents.
  3. Review and verify the documentation diff.
  4. Expand the open-question decision tree so future grill-me work can close
     remaining Stage 4 ambiguity.
  5. Research external WFA/optimization practices and close non-human
     decisions with evidence.
- Notes:
  - The user confirmed the first set of Stage 4 decisions through grill-me:
    strict preflight input failures, fold-level execution failures recorded and
    continued, train grid-search result preservation, independent-fold
    `oos_summary`, tuple-only objective contract, bar-count windows, and
    rolling-only mode.
  - The user requested a question-listing pass, not another round of questions
    to the human.
  - The follow-up objective requested web and open-source research, then
    evidence-backed closure of all questions that do not require human product
    review.
  - The user then closed the two remaining human-review questions:
    - WFA total-run cap defaults to no cap, with planned-run visibility and an
      optional explicit cap.
    - first-slice diagnostics stay fact-based and do not include numeric
      threshold-based quality judgments.
  - External docs consulted:
    - PyBroker strategy reference
    - Backtesting.py API reference
    - Backtesting.py parameter heatmap example
    - Backtrader Cerebro reference
  - Open-source snapshots cloned/inspected under `/tmp/quantcraft-wfa-research`:
    - `backtesting.py`
    - `pybroker`
    - `backtrader`
    - `vectorbt`
- Blockers or scope changes: none.

## Evaluator Review

- Findings:
  - No blocker findings.
  - The new resume spec includes the required product-spec sections and keeps
    technical implementation details deferred.
  - Existing WFA routing now points readers to the Stage 4 resume spec.
  - The older paused WFA spec no longer conflicts with the Stage 4 decision to
    defer objective aliases from the first slice.
  - The open-question section was first expanded into 50 decision questions.
  - The evidence-backed closure pass replaced those questions with
    `Evidence Consulted`, `Evidence-Based Decisions`, and `Human Review
    Required` sections.
  - After final human review, the original 50-question ambiguity list is fully
    closed for the Stage 4 resume product contract.
  - The spec records no open product questions for this stage; future runtime
    cap defaults and threshold-based robustness diagnostics are explicitly
    deferred as future slices.
- Verification evidence:
  - `rg -n "^## |^### " docs/product-specs/walk-forward-analysis-resume.md`
    confirmed the required section structure.
  - `rg -n "remains open|That remains open|may be added|Candidate diagnostic|Open Questions|Recommended default" docs/product-specs/walk-forward-analysis-resume.md docs/plans/2026-05-13-wfa-resume-product-spec.md`
    confirmed stale open-question wording was removed from the product spec.
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/walk-forward-analysis.md docs/product-specs/wfa-prerequisite-roadmap.md docs/product-specs/walk-forward-analysis-resume.md docs/plans/2026-05-13-wfa-resume-product-spec.md`
    passed for tracked paths.
  - `git diff --check -- docs/product-specs/index.md docs/product-specs/walk-forward-analysis.md docs/product-specs/wfa-prerequisite-roadmap.md && git diff --check --no-index /dev/null docs/product-specs/walk-forward-analysis-resume.md; test $? -le 1 && git diff --check --no-index /dev/null docs/plans/2026-05-13-wfa-resume-product-spec.md; test $? -le 1`
    passed, including new untracked files.
- Final disposition: accepted for this documentation slice.
