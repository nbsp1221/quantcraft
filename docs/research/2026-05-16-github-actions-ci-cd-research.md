# GitHub Actions CI/CD Research For Quantleet (2026)

## Status

- Status: `current`
- Class: `research`
- Canonical: `no`
- Role: `CI/CD ecosystem and implementation guidance`
- Last reviewed: `2026-05-16`

This document is a research artifact, not a system-of-record implementation
contract.

Use it to inform the Quantleet CI/CD implementation plan. If a conclusion from
this report should drive implementation, promote it into a product spec, design
doc, or execution plan first.

## Purpose

Quantleet is close to a first public beta package release. Runtime, package
build, and wheel smoke checks have passed locally, but the repository currently
has no GitHub Actions workflow beyond the pull request template.

This report answers:

1. Which GitHub Actions setup is the most appropriate for Quantleet's current
   Python package stack in 2026?
2. Which action versions and release patterns are current enough to use now?
3. How do comparable open-source projects configure CI and PyPI publishing in
   practice?
4. What should Quantleet implement first, and what should remain out of scope
   for the first beta?

## Quantleet Context

Observed repository state on 2026-05-16:

- package: `quantleet`
- version: `0.1.0b1`
- Python requirement: `>=3.12`
- local package manager and command runner: `uv` and `poethepoet`
- build backend: `uv_build`
- default verification command: `uv run poe verify`
- stronger runtime-sensitive verification command: `uv run poe verify-runtime`
- package build command: `uv build`
- package smoke evidence already used locally:
  - `uv run poe verify-runtime`
  - `uvx twine check dist/*`
  - isolated wheel install smoke for `BacktestEngine`, `ParameterStudy`, and
    `WalkForwardStudy`
- current GitHub Actions files: none under `.github/workflows`
- root `LICENSE`: present, MIT

The practical CI/CD gap is therefore not feature readiness. It is automated
verification, release artifact validation, and PyPI publishing.

## Research Method

Research inputs:

- official GitHub Actions documentation and official action repositories
- official uv documentation
- official Python Packaging User Guide and PyPI Trusted Publishing
  documentation
- local shallow clones of open-source repositories under
  `/tmp/quantleet-ci-research`

Local repositories inspected:

| Project | Reason inspected |
| --- | --- |
| `backtesting.py` | closest single-symbol backtesting UX comparator |
| `vectorbt` | Python quant research package with PyPI release workflow |
| `pybroker` | walk-forward/research comparator |
| `freqtrade` | active Python trading project using modern uv/GitHub Actions patterns |
| `backtrader` | classic backtesting comparator; useful mainly as a negative CI reference |
| `ruff` | modern Python/Rust packaging, release, and Trusted Publishing reference |
| `uv` | source-of-truth style reference for uv-oriented CI/CD |
| `pytest` | mature Python package release and packaging workflow reference |
| `packaging` | high-quality modern PyPA-adjacent package workflow reference |
| `rich` | broad Python project CI matrix reference |

Official sources used:

- GitHub `actions/checkout`: <https://github.com/actions/checkout>
- GitHub `actions/setup-python`: <https://github.com/actions/setup-python>
- GitHub artifact actions documentation and action repositories:
  - <https://github.com/actions/upload-artifact>
  - <https://github.com/actions/download-artifact>
- uv GitHub Actions guide:
  <https://docs.astral.sh/uv/guides/integration/github/>
- Python Packaging User Guide for GitHub Actions publishing:
  <https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>
- PyPI Trusted Publishing documentation:
  <https://docs.pypi.org/trusted-publishers/>
- PyPA GitHub Action for PyPI publish:
  <https://github.com/pypa/gh-action-pypi-publish>

## Current Action Version Findings

The strongest 2026 pattern is not only "use the latest major version." Mature
projects increasingly pin actions by full commit SHA and keep a version comment
beside the SHA.

Observed current versions in strong reference repositories:

| Purpose | Current/recommended action | Practical recommendation for Quantleet |
| --- | --- | --- |
| Checkout | `actions/checkout@v6`, observed `v6.0.2` in `packaging`, `pytest`, `uv`, and `freqtrade` | Use full SHA pin for `v6.0.2` with a comment. Use `persist-credentials: false` unless the job pushes. |
| Python setup | `actions/setup-python@v6`, observed `v6.2.0` in `packaging`, `pytest`, `uv`, and `freqtrade` | Use full SHA pin for `v6.2.0`, with `python-version: "3.12"`. |
| uv setup | `astral-sh/setup-uv@v8.1.0`, observed in `packaging`, `uv`, `ruff`, and `freqtrade` | Use full SHA pin for `v8.1.0`; enable cache for CI. |
| Upload artifacts | `actions/upload-artifact` v7 line, observed `v7.0.1` SHA pin in `packaging`, `uv`, `pytest`, and `freqtrade` | Use full SHA pin for release artifacts. |
| Download artifacts | `actions/download-artifact` v8 line, observed `v8.0.1` SHA pin in `packaging`, `uv`, `pytest`, and `freqtrade` | Use full SHA pin for publish jobs. |
| PyPI publish | `pypa/gh-action-pypi-publish@release/v1` or `v1.14.0` SHA pin | Prefer full SHA pin if adopting the hardened style; otherwise `release/v1` is the common documented stable channel. |
| GitHub Actions security scan | `zizmorcore/zizmor-action@v0.5.3` line observed in `uv` and `freqtrade` | Add after CI/CD exists, or include as a separate non-blocking hardening workflow. |

## Official Documentation Findings

### Python Setup

`actions/setup-python` is still the standard official way to install Python in
GitHub Actions. For Quantleet, the workflow should explicitly request Python
`3.12` because the package metadata requires `>=3.12` and the first beta is not
trying to support earlier Python versions.

Matrix testing across multiple Python versions is not useful yet unless the
project expands its declared Python support or intentionally supports
pre-release Python versions. A single Python `3.12` lane gives better
first-beta signal with less CI cost.

### uv Setup

The uv documentation recommends `astral-sh/setup-uv` for GitHub Actions and
supports cache configuration. For Quantleet, the workflow should stay aligned
with local development and run repository commands through `uv run poe ...`
instead of inventing separate CI-only commands.

Recommended CI shape:

```yaml
- uses: astral-sh/setup-uv@<pinned-sha> # v8.1.0
  with:
    enable-cache: true
    cache-dependency-glob: uv.lock

- run: uv sync --locked --dev
- run: uv run poe verify
```

### PyPI Trusted Publishing

The Python Packaging User Guide and PyPI documentation both favor Trusted
Publishing for GitHub Actions releases. This avoids storing a long-lived PyPI
API token in GitHub secrets.

The publish job needs:

```yaml
permissions:
  id-token: write
environment:
  name: pypi
```

The repository must also configure a matching Trusted Publisher in PyPI for the
project, owner, repository, workflow file, and environment.

### Artifact Separation

The recommended release flow builds artifacts in one job, uploads them, and
publishes from a later job that downloads exactly those artifacts.

This avoids rebuilding at publish time and makes the publish job smaller,
permission-limited, and easier to audit.

## Open-Source Findings

### `packaging`

`packaging` is the strongest compact reference for Quantleet.

Observed patterns:

- `permissions: {}` at workflow top level
- full SHA-pinned official actions with version comments
- `actions/checkout` with `persist-credentials: false`
- `actions/setup-python@v6.2.0`
- `astral-sh/setup-uv@v8.1.0`
- artifact upload/download split
- PyPI publish job with `id-token: write`
- environment named `pypi`
- `pypa/gh-action-pypi-publish` for publishing

Quantleet should use this style as the primary reference.

### `freqtrade`

`freqtrade` is the strongest domain-adjacent reference because it is a Python
trading project and uses modern uv setup.

Observed patterns:

- `permissions: {}`
- `actions/checkout` pinned to SHA with `persist-credentials: false`
- `astral-sh/setup-uv@v8.1.0`
- matrix across operating systems and Python versions
- separate TestPyPI and PyPI jobs
- `pypa/gh-action-pypi-publish`
- `id-token: write` for publishing
- `zizmor` workflow for GitHub Actions security analysis

Quantleet should copy the security posture, not the matrix size. The full
`freqtrade` matrix is too broad for a first beta.

### `uv`

`uv` is useful as a uv-native release reference, but it is much more complex
than Quantleet needs.

Observed patterns:

- full SHA-pinned actions
- `astral-sh/setup-uv@v8.1.0`
- artifact-driven release workflows
- Trusted Publishing through OIDC
- some workflows publish with `uv publish`
- `zizmor` check workflow

Quantleet can learn from the security and artifact boundaries, but should not
copy the release orchestration complexity.

### `ruff`

`ruff` shows modern release-hardening patterns:

- Trusted Publishing
- `uv publish`
- artifact attestations in release flows
- SHA-pinned actions
- reusable workflow calls

For Quantleet beta, this is a future reference. The first CI/CD implementation
should be smaller.

### `pytest`

`pytest` is a mature Python packaging reference.

Observed patterns:

- `permissions: {}`
- SHA-pinned `checkout`, `setup-python`, artifact actions
- package build and inspection before publish
- `pypa/gh-action-pypi-publish`
- `attestations: true` in the PyPI publish action
- release notes and GitHub release orchestration

Quantleet can consider package attestations later. For the first beta, Trusted
Publishing and artifact separation are enough.

### `vectorbt`

`vectorbt` shows a practical release workflow:

- release or manual dispatch trigger
- build job uploads distributions
- publish job downloads distributions
- `pypa/gh-action-pypi-publish@release/v1`
- `id-token: write`
- `environment: pypi`
- dry-run workflow input

This is a good example of a user-facing package release workflow, though its
action versions are older than the strongest 2026 references.

### `pybroker`

`pybroker` uses a simpler tox-based workflow:

- separate format, lint, typecheck, test, source build jobs
- `actions/checkout@v4`
- `actions/setup-python@v5`
- PyPI publish through a stored PyPI API token

This is a useful historical comparison, but not the recommended pattern for
Quantleet in 2026. Trusted Publishing is preferable.

### `backtesting.py`

`backtesting.py` has a compact CI workflow:

- lint, coverage, build, docs, Windows test jobs
- `actions/checkout@v4`
- `actions/setup-python@v5`
- no modern uv setup
- no obvious modern PyPI Trusted Publishing workflow in the inspected files

This is useful as a "keep CI small" reference, but not as a 2026 release
security reference.

### `rich`

`rich` shows broad matrix testing:

- Windows, Ubuntu, macOS
- Python `3.9` through `3.14`
- Poetry install
- format, mypy, pytest, coverage

This is not a direct fit for Quantleet because Quantleet is uv-based and Python
`>=3.12`. The matrix breadth is more than the first beta needs.

### `backtrader`

The inspected upstream did not provide a modern GitHub Actions CI/CD reference.
It is not useful for Quantleet's current CI/CD design.

## Recommended Quantleet CI/CD Shape

### 1. Minimal CI Workflow

File:

- `.github/workflows/ci.yml`

Triggers:

- `pull_request`
- `push` to `main`
- `workflow_dispatch`

Recommended jobs:

1. `verify`
   - Ubuntu only for the first beta.
   - Python `3.12`.
   - Run `uv sync --locked --dev`.
   - Run `uv run poe verify`.

2. Optional `runtime`
   - Manual or scheduled at first.
   - Run `uv run poe verify-runtime`.
   - Do not force this on every PR until the cost is acceptable.

Why:

- `uv run poe verify` is already the repo-local default gate.
- CI should not invent a parallel command surface.
- Python `3.12` matches `pyproject.toml`.
- OS matrix can be added after beta if user demand or bug reports justify it.

### 2. Release Build And Publish Workflow

File:

- `.github/workflows/release.yml`

Triggers:

- `push` tag pattern such as `v*`
- `workflow_dispatch`

Recommended build job:

- checkout with `persist-credentials: false`
- setup Python `3.12`
- setup uv with cache
- `uv sync --locked --dev`
- `uv run poe verify`
- `uv build`
- `uvx twine check --strict dist/*`
- isolated wheel smoke that imports and runs:
  - `BacktestEngine`
  - `ParameterStudy`
  - `WalkForwardStudy`
- upload `dist/*` as a release artifact

Recommended publish job:

- `needs: build`
- `environment: pypi`
- `permissions: id-token: write`
- download artifact into `dist/`
- publish with `pypa/gh-action-pypi-publish`
- configure PyPI Trusted Publisher before using this job

### 3. TestPyPI

For the first beta, add either:

- a separate `testpypi` job controlled by manual input, or
- a separate `.github/workflows/testpypi.yml`

Use:

```yaml
repository-url: https://test.pypi.org/legacy/
environment:
  name: testpypi
permissions:
  id-token: write
```

This lets the first release dry-run the real Trusted Publishing path without
using production PyPI.

## Recommended Security Posture

Use these defaults:

- top-level `permissions: {}`
- job-level permissions only where needed
- `id-token: write` only in publish jobs
- `contents: read` only when needed
- `persist-credentials: false` for checkout unless the job pushes
- full SHA pin actions with version comments
- avoid long-lived `PYPI_API_TOKEN`
- use GitHub environments named `testpypi` and `pypi`
- require manual environment approval for `pypi` if the repository is public or
  if accidental publish risk matters
- add `zizmor` after the first workflow lands

## Recommendation Summary

Quantleet should implement the first beta CI/CD in two workflow files:

1. `ci.yml`
   - PR and main verification
   - Python `3.12`
   - `uv`
   - `uv run poe verify`

2. `release.yml`
   - tag/manual release
   - build and check distributions
   - wheel smoke
   - artifact upload/download boundary
   - Trusted Publishing to PyPI

Avoid for the first beta:

- broad OS/Python matrix
- Docker publishing
- generated release notes
- GitHub Pages docs deployment
- package attestations as a blocker
- replacing repo-local `poe` commands with CI-only command sequences

## Proposed First Implementation Checklist

- Add `.github/workflows/ci.yml`.
- Add `.github/workflows/release.yml`.
- Configure PyPI Trusted Publisher for:
  - repository owner: `nbsp1221`
  - repository name: `quantleet`
  - workflow file: `release.yml`
  - environment: `pypi`
- Optionally configure TestPyPI Trusted Publisher for:
  - workflow file: `release.yml`
  - environment: `testpypi`
- Run local `uv run poe repo-check` after adding workflows.
- Run `zizmor` locally or through a later workflow once workflow files exist.

## Final Judgment

The best current model for Quantleet is:

- `packaging` for modern Python package workflow shape
- `freqtrade` for uv-based trading-project CI posture
- `uv` and `ruff` for hardened release-security examples
- `vectorbt` for simple release-trigger structure

The first beta should choose the small, boring version of those practices:
single-version CI, artifact-separated release build, Trusted Publishing, and
minimal permissions.
