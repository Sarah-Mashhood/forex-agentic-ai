# api.py
from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import List
from datetime import datetime
from src.guardrails.input_validation import validate_pair, validate_pairs
from src.guardrails.pipeline_safety import safe_run_pipeline_once
from src.schemas import Recommendation
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
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

# Create a router for /api prefix
router = APIRouter(prefix="/api")

# --- In-memory cache for latest recommendations ---
LATEST_RECOMMENDATIONS = {}

@router.get("/run", response_model=Recommendation)
def run_pipeline(pair: str = Query(..., description="Currency pair e.g. EURUSD")):
    """Trigger the pipeline for a single currency pair."""
    try:
        valid_pair = validate_pair(pair)
        rec = safe_run_pipeline_once(valid_pair)
        LATEST_RECOMMENDATIONS[valid_pair] = rec
        return rec
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

@router.get("/history")
def history(pair: str = Query(None, description="Optional currency pair to filter")):
    """Fetch past traces for one or all pairs."""
    if pair:
        try:
            valid_pair = validate_pair(pair)
            rec = LATEST_RECOMMENDATIONS.get(valid_pair)
            if rec:
                return rec
            return {"message": f"No data for {valid_pair}"}
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    return list(LATEST_RECOMMENDATIONS.values())

@router.get("/recommendations", response_model=List[Recommendation])
def recommendations():
    """Returns latest recommendations for all cached pairs."""
    return list(LATEST_RECOMMENDATIONS.values())

@router.get("/health")
def health_check():
    """Health check endpoint for uptime monitoring."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Agentic Forex AI API is running smoothly ✅"
    }

# Mount the router under /api
app.include_router(router)
