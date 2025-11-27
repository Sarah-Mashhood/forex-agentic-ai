"""
news_tool.py
-------------
MCP-based tool to fetch forex-related news from public RSS feeds (FXStreet, Investing.com, DailyFX)
with robust timezone-aware parsing and sensible fallbacks.
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

    If no currency-specific items are found, falls back to returning the most
    recent headlines across all feeds, so the UI is rarely empty.

    Args:
        currency (str): Currency code (e.g., 'EUR', 'USD', 'JPY').

    Returns:
        List[Dict]: A list of news dictionaries containing title, link, published timestamp, and source.
    """
    keyword = currency.upper()
    # Slightly wider window to ensure we get something for the demo
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)

    all_news: List[Dict] = []
    recent_fallback: List[Dict] = []

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
                title = (entry.get("title") or "").strip()
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

                # Skip very old items for both main & fallback lists
                if published < cutoff:
                    continue

                item = {
                    "title": title,
                    "url": link,
                    "timestamp": published.isoformat(),
                    "source": source,
                }

                # Build a combined text field for flexible matching
                combined_text = (
                    (entry.get("title") or "")
                    + " "
                    + (entry.get("summary") or "")
                    + " "
                    + (entry.get("description") or "")
                ).upper()

                # Currency match in title/summary/description
                if keyword in combined_text:
                    all_news.append(item)

                # Always store for fallback
                recent_fallback.append(item)

        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")

    # ✅ Fallback: if no currency-specific items, return most recent headlines
    if not all_news and recent_fallback:
        print(f"⚠️ No currency-specific news found for {currency}, returning recent headlines instead.")
        recent_fallback.sort(key=lambda x: x["timestamp"], reverse=True)
        return recent_fallback[:10]

    if not all_news:
        print(f"⚠️ No relevant news found for {currency}")
        return []

    # Sort and limit main list too (for consistency)
    all_news.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_news[:15]
