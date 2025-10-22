# src/tools/strategy_tools.py
from datetime import datetime, timezone
from typing import List
from src.tools.yfinance_tool import fetch_forex_candles
from src.tools.news_tool import fetch_forex_news
from src.agents.strategy_agent import simple_strategy
from src.schemas import Candle, NewsItem, Recommendation


def _dict_to_newsitem(d: dict) -> NewsItem:
    ts = d.get("timestamp")
    if isinstance(ts, str):
        try:
            ts_parsed = datetime.fromisoformat(ts)
        except Exception:
            ts_parsed = datetime.now(timezone.utc)
    else:
        ts_parsed = datetime.now(timezone.utc)
    return NewsItem(
        title=d.get("title", ""),
        url=d.get("url"),
        timestamp=ts_parsed,
        source=d.get("source"),
        sentiment=None
    )


def run_strategy_for_pair(pair: str) -> Recommendation:
    """
    High-level strategy tool:
    1) Fetches candles using yfinance_tool
    2) Fetches recent forex news via news_tool
    3) Feeds both into strategy_agent.simple_strategy()
    Returns a Recommendation Pydantic object
    """

    # --- 1️⃣ Market data ---
    candles = fetch_forex_candles(pair, days=3)

    # --- 2️⃣ News data ---
    currency_code = pair[:3].upper()
    news_resp = fetch_forex_news(currency_code)
    news_items = []
    if news_resp.get("status") in ("success", "fallback_success"):
        for d in news_resp.get("data", []):
            try:
                news_items.append(_dict_to_newsitem(d))
            except Exception:
                continue

    # --- 3️⃣ Strategy logic ---
    rec = simple_strategy(pair, candles, news_items)

    # --- Validate and coerce output ---
    if not isinstance(rec, Recommendation):
        try:
            rec = Recommendation(**rec)
        except Exception:
            rec = Recommendation(
                pair=pair,
                stance="AVOID",
                confidence=0.0,
                horizon_hours=24,
                rationale=["strategy error"]
            )

    return rec