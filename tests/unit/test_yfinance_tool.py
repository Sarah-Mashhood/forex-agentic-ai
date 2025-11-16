# tests/unit/test_yfinance_tool.py
import pytest
from src.tools.yfinance_tool import fetch_forex_candles
from src.schemas import Candle


@pytest.mark.unit
def test_fetch_forex_candles_structure():
    candles = fetch_forex_candles("EURUSD")
    if not candles:
        pytest.skip("Yahoo Finance unavailable or returned empty data")

    first = candles[0]
    assert isinstance(first, Candle)
    assert first.ts is not None
    assert isinstance(first.close, float)
