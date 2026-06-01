# Active Plan

- Date: 2026-06-01
- Task: Add `strategy` to the default mutation gate and reproduce score failure
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Make `uv run poe mutation-gates` and therefore `uv run poe check` include `src/quantleet/strategy`, while avoiding the known mutmut `__init_subclass__` collection failure so the observed failure is a mutation score/no-tests failure.
- Governing docs: `AGENTS.md`, `ARCHITECTURE.md`, `docs/design-docs/package-topology-and-naming.md`
- Why these are governing: They define the repo workflow, bounded contexts, and check surface.
- In-repo scope: `pyproject.toml`, `src/quantleet/strategy/config.py`, `src/quantleet/strategy/strategy.py`, this plan.
- Out-of-repo scope: mutmut package patches, dependency changes, test fixes.
- Tier A progression requested: `no`
- Approval record, if required: not required; `strategy` is Tier B.
- Verification commands: `rm -rf mutants && uv run poe mutation-gates`
- Success criteria: Mutation run reaches score evaluation and fails because aggregate score is below the configured threshold or because `no_tests` is nonzero.
- Out of scope: Killing surviving mutants, changing the 80% threshold, or committing this reproduction slice.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Confirm the failure mode is not collection/import failure and record the final mutation score output.
- Acceptance artifact location: this plan and final report.
- How the generator and evaluator agreed on done before execution: The same agent will compare the command output against the success criteria above.
- Checks the evaluator will use: `uv run poe mutation-gates`
- Auto-fail conditions: collection error, suspicious/timeout/segfault mutants, or inability to restore/explain the working tree state.

## Generator Work Log

- Planned slice order: add strategy mutation scope, add minimal mutmut pragmas for `__init_subclass__`, run mutation gate, report score failure.
- Notes: `src/quantleet/strategy` was added to `paths_to_mutate`; `tests/unit/strategy` and `tests/integration/strategy` were added to mutmut test selection. The two `__init_subclass__` methods were marked with `# pragma: no mutate` to avoid mutmut trampoline collection failure.
- Blockers or scope changes: none.

## Evaluator Review

- Findings: `uv run poe mutation-gates` reached score evaluation. The failure is a mutation gate failure, not collection/import failure.
- Verification evidence: `mutation score: total=3357 killed=2681 survived=671 no_tests=5 suspicious=0 timeout=0 segfault=0 score=79.86% threshold=80%`; `mutation score gate failed: {'no_tests': 5, 'score': 79.86}`.
- Final disposition: reproduction complete; `strategy` is now included in the default mutation gate and currently causes the gate to fail.
