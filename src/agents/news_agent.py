"""
news_agent.py
-------------
Agent wrapper for forex news retrieval.
Uses news_tool (MCP-logged) to get recent news headlines.
"""

from src.tools.news_tool import fetch_forex_news
from src.schemas import NewsItem
from datetime import datetime, timezone

def run_news_agent(currency_code: str):
    """
    Fetch recent news items for a currency code (e.g., 'EUR', 'USD').
    Returns a list of NewsItem objects.
    """
    result = fetch_forex_news(currency_code)
    news_list = []
    if result.get("status") in ("success", "fallback_success"):
        for d in result.get("data", []):
            try:
                news_list.append(
                    NewsItem(
                        title=d.get("title", ""),
                        url=d.get("url"),
                        timestamp=datetime.fromisoformat(d["timestamp"]),
                        source=d.get("source"),
                    )
                )
            except Exception:
                continue
    return news_list
