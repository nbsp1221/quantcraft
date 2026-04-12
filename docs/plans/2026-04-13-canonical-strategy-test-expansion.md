# Canonical Strategy Test Expansion

**Goal:** Strengthen the integration harness beyond the single canonical RSI contract without growing an ambiguous public task surface.

**Current decision:** The repository keeps:

- canonical end-to-end RSI contract
- canonical end-to-end EMA crossover contract
- additional deterministic strategy regression contracts in the normal integration lane

The repository does **not** keep a separate `test-integration-extended` public task. That split was removed because it created an ambiguous harness surface and diverged from the stable direct `pytest` command surface.

## Why this changed

The initial draft proposed a dedicated extended integration lane for broader strategy breadth. After review, that approach was rejected for this repository because:

- `extended` did not describe a clear semantic axis like `live` or `perf`
- raw `pytest -q` and the Poe default lane would have run materially different test sets
- the extra public task increased control-plane complexity without enough runtime or environment justification

## Accepted harness shape

- `uv run poe test` runs the default repository test lane
- `uv run poe test-integration` runs all integration tests
- `uv run poe verify` remains the default correctness bundle
- `uv run poe perf-check` remains the explicit performance lane
- `uv run poe verify-runtime` remains the explicit stronger lane for runtime-sensitive research changes

## Strategy coverage

The default integration suite now carries three deterministic strategy-level contracts:

1. `RSI 30/70 mean reversion`
2. `EMA crossover`
3. `MACD crossover` regression contract

This keeps strategy breadth inside the normal integration taxonomy without inventing another public bucket.

## Follow-up rule

If future strategy coverage grows enough to justify another explicit lane, introduce it only when:

- the lane has a clear semantic axis
- the low-level direct surface and the Poe surface stay aligned
- the command is legible from the name alone
- the repository docs and structure checks are updated in the same batch
