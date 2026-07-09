from __future__ import annotations

from tests.support import ROOT


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_validation_pipeline_docs_route_to_current_research_public_path() -> None:
    product_spec = _read("docs/product-specs/validation-pipeline.md")

    assert "WalkForwardValidation" in product_spec
    assert "RollingSplitPolicy" in product_spec
    assert "MetricSelectionPolicy` is intentionally not public" in product_spec


def test_public_docs_do_not_promote_deferred_beta_controls() -> None:
    docs = "\n".join(
        (
            _read("README.md"),
            _read("docs/product-specs/validation-pipeline.md"),
            _read("docs/site/guides/parameter-exploration.md"),
            _read("docs/site/guides/walk-forward-analysis.md"),
            _read("docs/references/research-ergonomics-quickstart.md"),
        )
    )

    forbidden_fragments = (
        "ParameterStudy(source=",
        "grid_search(source=",
        "n_jobs=",
        "workers=",
        "parallel=",
        "executor=",
        "GridSearchResult.heatmap",
        "resume=",
        "from quantcraft.research import ParameterStudy",
        "`Strategy`, `ParameterStudy`",
        "`ParameterStudy`,\n  `ta`, `qc`",
    )
    for fragment in forbidden_fragments:
        assert fragment not in docs


def test_docs_keep_candidate_search_as_research_diagnostic_not_recommendation() -> None:
    product_spec = _read("docs/product-specs/validation-pipeline.md")
    normalized_spec = " ".join(product_spec.split())

    assert "not an optimizer guarantee or a trading recommendation" in normalized_spec
