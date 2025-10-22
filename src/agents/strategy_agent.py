# src/agents/strategy_agent.py
from typing import List, Union
from ..schemas import Recommendation, Candle, NewsItem
from textblob import TextBlob


def _headline_sentiment(text: str) -> float:
    """Return sentiment polarity between -1.0 (negative) and +1.0 (positive)."""
    try:
        if not text.strip():
            return 0.0
        return TextBlob(text).sentiment.polarity
    except Exception:
        return 0.0


def simple_strategy(pair: str, candles: List[Union[Candle, dict]], news: List[Union[NewsItem, dict]]) -> Recommendation:
    """
    Hybrid sentiment-aware strategy:
    - Uses candle trend direction as quantitative signal.
    - Uses average news sentiment as qualitative signal.
    - Adjusts confidence if both signals align or contradict.
    """

    # --- Normalize candles ---
    cleaned_candles = []
    for c in candles:
        if isinstance(c, dict):
            try:
                cleaned_candles.append(Candle(**c))
            except Exception:
                continue
        elif isinstance(c, Candle):
            cleaned_candles.append(c)

    # --- Normalize news ---
    cleaned_news = []
    for n in news:
        if isinstance(n, dict):
            try:
                cleaned_news.append(NewsItem(**n))
            except Exception:
                continue
        elif isinstance(n, NewsItem):
            cleaned_news.append(n)

    # --- Not enough candle data ---
    if len(cleaned_candles) < 2:
        return Recommendation(
            pair=pair,
            stance="AVOID",
            confidence=0.0,
            horizon_hours=24,
            rationale=["Not enough candle data"],
            news=[]
        )

    yesterday = cleaned_candles[-2]
    today = cleaned_candles[-1]
    daily_move = today.close - yesterday.close
    rationale = [f"Daily move {daily_move:.4f}"]

    # --- Sentiment analysis on news ---
    relevant_news = []
    sentiment_scores = []
    seen_titles = set()

    for item in cleaned_news[:10]:
        title = (item.title or "").strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        sentiment = _headline_sentiment(title)
        sentiment_scores.append(sentiment)
        relevant_news.append(item)
        rationale.append(f"{title} ({item.source or 'Unknown'}) [Sentiment={sentiment:+.2f}]")

    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    rationale.append(f"🧠 Average news sentiment = {avg_sentiment:+.2f}")

    # --- Base stance from price movement ---
    if abs(daily_move) < 0.0005:
        stance = "AVOID"
        confidence = 0.45
    else:
        stance = "BUY" if daily_move > 0 else "SELL"
        confidence = 0.7

    # --- Adjust confidence based on sentiment alignment ---
    if avg_sentiment > 0.2 and stance == "BUY":
        confidence += 0.1
        rationale.append("✅ Positive sentiment reinforces BUY stance.")
    elif avg_sentiment < -0.2 and stance == "SELL":
        confidence += 0.1
        rationale.append("✅ Negative sentiment reinforces SELL stance.")
    elif (avg_sentiment > 0.2 and stance == "SELL") or (avg_sentiment < -0.2 and stance == "BUY"):
        confidence -= 0.15
        rationale.append("⚠️ Sentiment contradicts price action — confidence reduced.")
    else:
        rationale.append("😐 Neutral or mixed sentiment; no strong news influence.")

    confidence = max(0.0, min(confidence, 1.0))
    rationale.append("This is not financial advice.")

    # --- Return Recommendation ---
    return Recommendation(
        pair=pair,
        stance=stance,
        confidence=round(confidence, 2),
        horizon_hours=24,
        rationale=rationale,
        news=relevant_news
    )



