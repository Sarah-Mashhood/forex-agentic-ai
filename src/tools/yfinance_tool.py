# src/tools/yfinance_tool.py
import yfinance as yf
from datetime import datetime, timezone, timedelta
from src.schemas import Candle

def fetch_forex_candles(pair: str, interval: str = "1h", days: int = 7) -> list[Candle]:
    """
    Fetch historical candle data for a forex pair.

    Args:
        pair: Forex pair string, e.g., "EURUSD=X"
        interval: '1m', '5m', '1h', '1d', etc.
        days: How many past days to fetch.

    Returns:
        List of Candle objects
    """
    # Ensure yfinance format: EURUSD -> EURUSD=X
    yf_pair = f"{pair}=X" if not pair.endswith("=X") else pair
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    # Explicitly set auto_adjust=True to remove FutureWarning
    df = yf.download(
        yf_pair,
        start=start,
        end=end,
        interval=interval,
        progress=False,
        auto_adjust=True
    )

    # Convert numeric columns to float safely
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)

    candles = []
    for idx, row in df.iterrows():
        candles.append(
            Candle(
                ts=idx.to_pydatetime(),
                open=float(row["Open"].iloc[0]) if hasattr(row["Open"], "iloc") else float(row["Open"]),
                high=float(row["High"].iloc[0]) if hasattr(row["High"], "iloc") else float(row["High"]),
                low=float(row["Low"].iloc[0]) if hasattr(row["Low"], "iloc") else float(row["Low"]),
                close=float(row["Close"].iloc[0]) if hasattr(row["Close"], "iloc") else float(row["Close"]),
                volume=float(row["Volume"].iloc[0]) if "Volume" in row and row["Volume"] is not None and hasattr(row["Volume"], "iloc") else float(row.get("Volume", 0.0)),
            )
        )

    return candles