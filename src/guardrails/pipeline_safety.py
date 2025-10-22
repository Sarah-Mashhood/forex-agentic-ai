# src/guardrails/pipeline_safety.py
import time
from datetime import datetime, timezone
from src.graph import run_pipeline_once
from src.schemas import Recommendation

def safe_run_pipeline_once(pair: str, retries: int = 3, delay: float = 1.0) -> Recommendation:
    """Runs pipeline safely with retries and fallback."""
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            trace = run_pipeline_once(pair, dry_run_email=True)

            if trace.get("status") == "success" and "recommendation" in trace:
                rec = trace["recommendation"]
                if isinstance(rec, Recommendation):
                    return rec
                else:
                    # Coerce dict to Recommendation
                    return Recommendation(**rec)

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for {pair}: {e}")
            last_exception = e
            time.sleep(delay)

    print(f"❌ All retries failed for {pair}, returning fallback recommendation")
    if last_exception:
        print(f"Last error: {last_exception}")
    return _fallback_recommendation(pair)


def _fallback_recommendation(pair: str) -> Recommendation:
    """Returns a safe default Recommendation if pipeline fails."""
    return Recommendation(
        pair=pair,
        stance="AVOID",
        confidence=0.0,
        horizon_hours=24,
        rationale=[
            f"Fallback recommendation issued at {datetime.now(timezone.utc).isoformat()}"],
        news=[],
    )
