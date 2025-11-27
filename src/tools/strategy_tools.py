# src/tools/strategy_tools.py
from datetime import datetime, timezone
from typing import List, Any, Dict

from src.tools.yfinance_tool import fetch_forex_candles
from src.tools.news_tool import fetch_forex_news
from src.agents.strategy_agent import simple_strategy
from src.schemas import Candle, NewsItem, Recommendation


def _dict_to_newsitem(d: Dict[str, Any]) -> NewsItem:
    """Safely convert a raw news dict into a NewsItem Pydantic model."""
    ts = d.get("timestamp")
    if isinstance(ts, str):
        try:
            ts_parsed = datetime.fromisoformat(ts)
        except Exception:
            ts_parsed = datetime.now(timezone.utc)
    else:
        ts_parsed = datetime.now(timezone.utc)

    return NewsItem(
        title=d.get("title", "") or "",
        url=d.get("url"),
        timestamp=ts_parsed,
        source=d.get("source"),
        sentiment=None,
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
    candles: List[Candle] = fetch_forex_candles(pair, days=3)

    # --- 2️⃣ News data ---
    currency_code = pair[:3].upper()
    raw_news = fetch_forex_news(currency_code)

    news_items: List[NewsItem] = []

    # Because of @mcp_tool, fetch_forex_news may return:
    #  - {"status": "success", "data": [ ... ]}
    #  - or a raw List[Dict] (depending on how it's called)
    payload: List[Dict[str, Any]] = []

    if isinstance(raw_news, dict):
        # Common keys used by wrappers
        payload = (
            raw_news.get("data")
            or raw_news.get("output")
            or raw_news.get("news")
            or []
        )
    elif isinstance(raw_news, list):
        payload = raw_news

    if isinstance(payload, list):
        for d in payload:
            try:
                news_items.append(_dict_to_newsitem(d))
            except Exception:
                # Skip malformed news entries without failing the strategy
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
                rationale=["Strategy error: failed to build Recommendation object"],
                news=[],
            )

    return rec
