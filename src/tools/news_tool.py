"""
news_tool.py
-------------
MCP-based tool to fetch forex-related news from public RSS feeds (FXStreet, Investing.com, DailyFX)
with robust timezone-aware parsing.
"""

import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from dateutil import parser as date_parser
from src.tools.mcp import mcp_tool

# --- RSS sources ---
RSS_SOURCES = [
    "https://www.fxstreet.com/rss/news",
    "https://www.investing.com/rss/news_25.rss",
    "https://www.dailyfx.com/feeds/market-news",
]


@mcp_tool(name="fetch_forex_news", description="Fetch recent forex-related news from multiple RSS sources.")
def fetch_forex_news(currency: str) -> List[Dict]:
    """
    Fetch recent news mentioning the specified currency (e.g., 'EUR', 'USD', 'JPY').

    Args:
        currency (str): Currency code (e.g., 'EUR', 'USD', 'JPY').

    Returns:
        List[Dict]: A list of news dictionaries containing title, link, published timestamp, and source.
    """
    keyword = currency.upper()
    cutoff = datetime.now(timezone.utc) - timedelta(days=2)

    all_news = []

    for url in RSS_SOURCES:
        try:
            print(f"🔎 Fetching from {url}")
            feed = feedparser.parse(url)

            if feed.bozo:
                print(f"⚠️ Skipped {url} (malformed feed)")
                continue
            if not feed.entries:
                print(f"⚠️ Skipped {url} (no entries)")
                continue

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                published_str = entry.get("published", "") or entry.get("updated", "")
                source = url.split("/")[2]

                # --- Parse and normalize timestamp ---
                try:
                    published = date_parser.parse(published_str)
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=timezone.utc)
                    else:
                        published = published.astimezone(timezone.utc)
                except Exception:
                    published = datetime.now(timezone.utc)

                # --- Filter by keyword and cutoff ---
                if keyword in title.upper() and published > cutoff:
                    all_news.append({
                        "title": title,
                        "url": link,
                        "timestamp": published.isoformat(),
                        "source": source,
                    })

            if all_news:
                print(f"✅ Found {len(all_news)} relevant items from {url}")

        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")

    if not all_news:
        print(f"⚠️ No relevant news found for {currency}")

    return all_news
