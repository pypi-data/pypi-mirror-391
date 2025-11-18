"""Test gmtorch."""

import gmtorch


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(gmtorch.__name__, str)
