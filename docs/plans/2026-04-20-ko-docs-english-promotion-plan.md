# Active Plan

- Date: `2026-04-20`
- Task: `Promote Korean draft and research docs to English repository-local references`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Promote the current Korean `-ko.md` draft/research docs into maintained
  English equivalents so future agents can use the same content more
  effectively, while preserving role separation between research, design, and
  workflow artifacts.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow contract, documentation authority model,
    Tier A safety expectations, package/document routing policy, and the
    distinction between governing, draft, research, and plan artifacts that
    this slice must preserve.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
  - `https://www.anthropic.com/engineering/harness-design-long-running-apps`
- Why these references matter:
  - They reinforce the agent-first harness expectation the user explicitly
    requested: repository-local docs should be legible to agents, and human
    attention should be conserved via strong review loops and clear system-of-
    record documents.
- In-repo scope:
  - Promote these Korean-language docs into English counterparts:
    - `docs/design-docs/order-runtime-model-design-ko.md`
    - `docs/design-docs/trading-kernel-contract-draft-ko.md`
    - `docs/research/2026-04-20-order-runtime-model-comparison-ko.md`
  - Update affected cross-links and routing indexes.
  - Update repo tests or fixtures that hardcode the old filenames if needed.
  - Treat the existing uncommitted Order-runtime doc slice as carryover
    context already present in the worktree rather than as new scope created by
    this slice.
- Out-of-repo scope:
  - No Python source changes.
  - No product-spec contract changes.
  - No new architectural decisions beyond restating the already-reviewed
    content in English.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to rewrite all `-ko.md` docs in English, get
      them reviewed, and keep the docs as the system of record for future AI
      agents
    - Granted scope:
      docs-only translation/promotion work touching Tier A `trading`
      documentation and any repo-local routing/tests required to keep those
      docs discoverable
    - Expiration:
      end of this `2026-04-20` English-promotion slice
    - Audit reference:
      this active plan plus the resulting English docs and review findings
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - All current `docs/**/*ko.md` artifacts in scope are removed after their
    English replacements and routing updates land.
  - Cross-links, indexes, and any repo tests referencing the old filenames are
    updated coherently.
  - Reviewer fan-out includes at least one contrarian review pass.
  - The final evaluator record shows no material findings remain.
  - `uv run poe repo-check` passes from the current repository state.
- Out of scope:
  - Rewriting unrelated historical execution logs
  - Changing the substance of the already-reviewed Order-runtime decisions
  - Promoting draft docs into governing authority

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after all current Korean `-ko.md` docs in `docs/`
    have been removed after English replacement, all repo-local routing
    references are coherent, bounded review fan-out has found no material
    issues, and fresh repo-check evidence is recorded.
- Acceptance artifact location:
  - English draft/research replacements under `docs/design-docs/` and
    `docs/research/`
  - updated indexes/cross-links
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - This slice is done when a future agent can navigate English-language
    canonical draft/research docs from the current routing surface without
    losing any reviewed substance.
- Checks the evaluator will use:
  - Confirm every current `docs/**/*ko.md` file in scope is removed.
  - Confirm indexes and cross-links prefer the English canonical filenames.
  - Confirm the new English docs preserve draft/research roles rather than
    collapsing into one authority blob.
  - Confirm bounded reviewer fan-out includes contrarian feedback and
    synthesis.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Leaving mixed-language duplicate docs as equal-priority routing targets
  - Breaking cross-links or index discoverability
  - Quietly changing the substance of the reviewed design decisions
  - Skipping reviewer synthesis or verification evidence

## Generator Work Log

- Planned slice order:
  1. Create the active plan and inventory all `-ko.md` docs plus references.
  2. Author English replacements and update cross-links/routing.
  3. Update repo tests/fixtures tied to the old filenames if necessary.
  4. Run bounded review fan-out including a contrarian pass.
  5. Revise until no material findings remain.
  6. Run `uv run poe repo-check` and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Subagents stay read-only and evidence-bearing.
  - This slice intentionally keeps the already-reviewed content stable and
    focuses on language promotion plus routing integrity.
  - The worktree already contains carryover edits from the immediately
    preceding runtime-Order doc slice; this promotion slice owns the English
    draft/research replacements, routing updates, and any necessary repo-check
    fixture adjustments.
- Blockers or scope changes:
  - User explicitly rejected compatibility stubs and required deletion of the
    old `-ko.md` files. Historical archive records therefore keep the old
    Korean filenames as plain audit text, while current routing and active
    docs move to the English canonical drafts.

## Evaluator Review

- Findings:
  - The English canonical docs now exist at:
    - `docs/design-docs/order-runtime-model-design.md`
    - `docs/design-docs/trading-kernel-contract-draft.md`
    - `docs/research/2026-04-20-order-runtime-model-comparison.md`
  - Current routing surfaces prefer the English canonical paths:
    - `docs/design-docs/index.md`
    - `docs/research/index.md`
    - `docs/design-docs/architecture-governance.md`
    - `docs/product-specs/backtest-mvp.md`
  - The old `-ko.md` docs covered by this slice were removed rather than kept
    as compatibility stubs, per explicit user direction.
  - Historical archive records were preserved as audit text rather than
    rewritten into a second routing surface.
  - Structure tests now protect the English-routing policy and removal of the
    `-ko` targets.
  - Reviewer synthesis:
    1. initial review found stale plan references, a repo-check blind spot for
       the rename class, and an audit/history concern around archive rewrites
    2. the slice was revised by:
       - adding focused structure tests for English canonical routing
       - removing the compatibility stubs after user rejection
       - restoring historical archive text to preserve original filenames
       - repairing the earlier completed runtime-design plan so its historical
         Korean outputs and later English promotion are both explicit
    3. after those revisions, no material issues remained in the
       English-promotion slice itself
- Verification evidence:
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
    -> `28 passed`
  - `uv run poe repo-check`
    -> `repository checks passed`
- Final disposition:
  - `complete`
