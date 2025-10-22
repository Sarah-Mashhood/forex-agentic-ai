#schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Candle(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0   # ✅ default avoids NoneType issues


class NewsItem(BaseModel):
    title: str
    url: Optional[str] = None
    timestamp: datetime
    source: Optional[str] = None
    sentiment: Optional[float] = None   # placeholder, for future sentiment


class Recommendation(BaseModel):
    pair: str
    stance: str              # BUY / SELL / AVOID
    confidence: float = 0.5
    horizon_hours: int = 24
    rationale: List[str] = Field(default_factory=list)
    news: Optional[List[NewsItem]] = Field(default_factory=list)