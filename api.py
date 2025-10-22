# api.py
from fastapi import FastAPI, HTTPException, Query
from typing import List
from datetime import datetime
from src.guardrails.input_validation import validate_pair, validate_pairs
from src.guardrails.pipeline_safety import safe_run_pipeline_once
from src.schemas import Recommendation
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Agentic Forex AI API",
    description="Run multi-agent forex strategy pipelines and fetch results safely.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory cache for latest recommendations ---
LATEST_RECOMMENDATIONS = {}

@app.get("/run", response_model=Recommendation)
def run_pipeline(pair: str = Query(..., description="Currency pair e.g. EURUSD")):
    """
    Trigger the pipeline for a single currency pair.
    Returns the Recommendation object (with guardrails).
    """
    try:
        valid_pair = validate_pair(pair)
        rec = safe_run_pipeline_once(valid_pair)
        # Update cache
        LATEST_RECOMMENDATIONS[valid_pair] = rec
        return rec
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


@app.get("/history")
def history(pair: str = Query(None, description="Optional currency pair to filter")):
    """
    Fetch past traces for one or all pairs.
    Returns the list of cached recommendations (latest run).
    """
    if pair:
        try:
            valid_pair = validate_pair(pair)
            rec = LATEST_RECOMMENDATIONS.get(valid_pair)
            if rec:
                return rec
            else:
                return {"message": f"No data for {valid_pair}"}
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    else:
        return list(LATEST_RECOMMENDATIONS.values())


@app.get("/recommendations", response_model=List[Recommendation])
def recommendations():
    """
    Returns latest recommendations for all cached pairs.
    """
    return list(LATEST_RECOMMENDATIONS.values())

@app.get("/health")
def health_check():
    """
    Health check endpoint for uptime monitoring.
    Returns a timestamp and status message.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Agentic Forex AI API is running smoothly ✅"
    }

