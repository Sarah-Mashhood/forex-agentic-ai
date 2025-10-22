import pytest
from src.tools.yfinance_tool import fetch_forex_candles

@pytest.mark.unit
def test_fetch_forex_candles_structure():
    candles = fetch_forex_candles("EURUSD")
    if not candles:
        pytest.skip("Yahoo Finance unavailable or returned empty data")
    assert len(candles) > 0
    assert all(hasattr(c, "ts") for c in candles)
    assert all(hasattr(c, "close") for c in candles)
