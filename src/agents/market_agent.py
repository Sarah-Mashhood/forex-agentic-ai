"""
market_agent.py
---------------
Agent wrapper for market data retrieval.
Uses yfinance_tool (MCP-logged) to get recent candles.
"""

from src.tools.yfinance_tool import fetch_forex_candles
from src.schemas import Candle
from datetime import datetime, timezone

def run_market_agent(pair: str):
    """
    Fetch daily candle data for a given pair.
    Returns a list of Candle objects.
    """
    result = fetch_forex_candles(pair, days=3)
    candles = []
    if result.get("status") in ("success", "fallback_success"):
        for d in result.get("data", []):
            try:
                candles.append(
                    Candle(
                        ts=datetime.fromisoformat(d["ts"]),
                        open=float(d["open"]),
                        high=float(d["high"]),
                        low=float(d["low"]),
                        close=float(d["close"]),
                        volume=float(d.get("volume", 0.0) or 0.0),
                    )
                )
            except Exception:
                continue
    return candles
