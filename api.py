from fastapi import FastAPI, HTTPException, Query, APIRouter, Response
from typing import List
from datetime import datetime
import time
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from src.guardrails.input_validation import validate_pair
from src.guardrails.pipeline_safety import safe_run_pipeline_once
from src.schemas import Recommendation

# ====================================================
# 🚀 FastAPI App Configuration
# ====================================================
app = FastAPI(
    title="Agentic Forex AI API",
    description="Run multi-agent forex strategy pipelines and fetch results safely.",
    version="1.1.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================
# 📊 Loguru Setup (stdout → Railway logs)
# ====================================================
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

# ====================================================
# 📈 Prometheus Metrics
# ====================================================
REQUEST_COUNT = Counter(
    "api_request_total",
    "Total API requests received",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "API request latency (seconds)", ["path"]
)
HEALTH_STATUS = Gauge("api_health_status", "1 if healthy, 0 otherwise")

# Forex-specific metrics
FOREX_RUN_COUNT = Counter(
    "forex_run_total",
    "Total number of forex strategy runs",
    ["pair", "status"],
)
FOREX_RUN_LATENCY = Histogram(
    "forex_run_latency_seconds",
    "Execution time of forex strategy runs",
    ["pair"],
)
LAST_RUN_TIMESTAMP = Gauge(
    "forex_last_run_timestamp",
    "Timestamp of last successful strategy run (epoch)",
    ["pair"],
)

# ====================================================
# 🧠 In-memory cache
# ====================================================
LATEST_RECOMMENDATIONS = {}

# ====================================================
# 🧩 Router with prefix /api
# ====================================================
router = APIRouter(prefix="/api")

# ====================================================
# 🧩 Middleware for request logs + metrics
# ====================================================
@app.middleware("http")
async def access_log_and_metrics(request, call_next):
    start = time.time()
    path = request.url.path
    method = request.method
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duration = time.time() - start
        REQUEST_LATENCY.labels(path).observe(duration)
        REQUEST_COUNT.labels(method, path, str(status)).inc()
        logger.info(f"{method} {path} status={status} duration={duration:.3f}s")

# ====================================================
# 🔁 Endpoints
# ====================================================
@router.get("/run", response_model=Recommendation)
def run_pipeline(pair: str = Query(..., description="Currency pair e.g. EURUSD")):
    """Trigger the strategy pipeline for a single currency pair."""
    start = time.time()
    try:
        valid_pair = validate_pair(pair)
        rec = safe_run_pipeline_once(valid_pair)

        # cache latest result
        LATEST_RECOMMENDATIONS[valid_pair] = rec

        # metrics
        FOREX_RUN_COUNT.labels(pair=valid_pair, status="success").inc()
        FOREX_RUN_LATENCY.labels(pair=valid_pair).observe(time.time() - start)
        LAST_RUN_TIMESTAMP.labels(pair=valid_pair).set_to_current_time()

        return rec
    except ValueError as ve:
        FOREX_RUN_COUNT.labels(pair=pair, status="validation_error").inc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        FOREX_RUN_COUNT.labels(pair=pair, status="error").inc()
        logger.exception(f"Pipeline error for {pair}: {e}")
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
    """Return the latest recommendations for all cached pairs."""
    return list(LATEST_RECOMMENDATIONS.values())

@router.get("/health")
def health_check():
    """Health check endpoint for uptime monitoring."""
    HEALTH_STATUS.set(1.0)
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Agentic Forex AI API is running smoothly ✅",
    }

@router.get("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# Mount the router
app.include_router(router)
