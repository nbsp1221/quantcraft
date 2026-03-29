import pytest

from quantcraft import Exchange, MarketType, TimeBar


def test_public_import_smoke() -> None:
    assert MarketType.SPOT == "spot"
    assert TimeBar is not None
    assert Exchange is not None


def test_public_import_surface_rejects_unknown_root_exports() -> None:
    import quantcraft

    with pytest.raises(AttributeError, match="has no attribute"):
        getattr(quantcraft, "UnknownExport")
