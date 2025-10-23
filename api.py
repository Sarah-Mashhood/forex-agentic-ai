# api.py
from fastapi import FastAPI, HTTPException, Query, APIRouter, Response
from typing import List
from datetime import datetime
from src.guardrails.input_validation import validate_pair
from src.guardrails.pipeline_safety import safe_run_pipeline_once
from src.schemas import Recommendation
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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

# Simple vanilla JS frontend so the API and dashboard can share the same port
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Agentic Forex AI Dashboard</title>
    <style>
      :root {
        color-scheme: dark light;
        font-family: \"Segoe UI\", Tahoma, Geneva, Verdana, sans-serif;
        background: #0f172a;
        color: #e2e8f0;
      }
      body {
        margin: 0;
        display: flex;
        justify-content: center;
        padding: 2rem 1rem 3rem;
      }
      main {
        width: min(720px, 100%);
        background: rgba(15, 23, 42, 0.85);
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 30px 60px rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.2);
      }
      h1 {
        margin-top: 0;
        font-size: clamp(1.8rem, 3vw, 2.4rem);
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: #38bdf8;
      }
      label {
        font-weight: 600;
        display: block;
        margin-bottom: 0.6rem;
      }
      select,
      input,
      button {
        width: 100%;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.4);
        font-size: 1rem;
        background: rgba(15, 23, 42, 0.6);
        color: inherit;
      }
      select:focus,
      input:focus,
      button:focus {
        outline: 2px solid #38bdf8;
        border-color: transparent;
      }
      button {
        margin-top: 1rem;
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        color: #0f172a;
        font-weight: 700;
        cursor: pointer;
        transition: transform 120ms ease, box-shadow 120ms ease;
      }
      button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 30px rgba(14, 165, 233, 0.35);
      }
      .card {
        margin-top: 1.5rem;
        padding: 1.5rem;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.2);
      }
      .status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 600;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: rgba(74, 222, 128, 0.12);
        color: #4ade80;
      }
      .status.error {
        background: rgba(248, 113, 113, 0.15);
        color: #f87171;
      }
      ul {
        padding-left: 1.2rem;
      }
      a {
        color: #38bdf8;
      }
      footer {
        text-align: center;
        margin-top: 2rem;
        color: rgba(148, 163, 184, 0.8);
        font-size: 0.9rem;
      }
      .loading {
        animation: pulse 1.2s ease-in-out infinite;
      }
      @keyframes pulse {
        0%,
        100% {
          opacity: 0.45;
        }
        50% {
          opacity: 1;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <h1>💹 Agentic Forex AI Dashboard</h1>
      <form id=\"run-form\">
        <label for=\"pair-select\">Select Currency Pair</label>
        <select id=\"pair-select\" name=\"pair\"></select>
        <label for=\"custom-pair\" style=\"margin-top:1rem;\">Or add your own custom currency pair (e.g., NZDUSD, USDCHF)</label>
        <input id=\"custom-pair\" name=\"custom-pair\" placeholder=\"Enter pair\" autocomplete=\"off\" />
        <button type=\"submit\">🚀 Run Strategy</button>
      </form>

      <section id=\"result\" class=\"card\" hidden>
        <h2 id=\"result-title\"></h2>
        <p id=\"confidence\"></p>
        <div>
          <h3>Rationale</h3>
          <ul id=\"rationale\"></ul>
        </div>
        <div>
          <h3>Related News</h3>
          <ul id=\"news\"></ul>
        </div>
      </section>

      <section class=\"card\">
        <h3>🩺 System Health</h3>
        <p id=\"health-status\" class=\"loading\">Checking API...</p>
      </section>

      <section class=\"card\" id=\"error-card\" hidden>
        <h3>⚠️ Something went wrong</h3>
        <p id=\"error-message\"></p>
        <p>Hint: confirm that <code>API_URL</code> is set correctly if you are running the Streamlit client.</p>
      </section>

      <footer>
        Built with ❤️ by Syeda Sarah Mashhood | Agentic Forex AI
      </footer>
    </main>

    <script>
      const defaultPairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'AUDCAD', 'GBPCAD'];
      const select = document.getElementById('pair-select');
      defaultPairs.forEach((pair) => {
        const option = document.createElement('option');
        option.value = pair;
        option.textContent = pair;
        select.appendChild(option);
      });

      const apiBase = `${window.location.origin}/api`;
      const form = document.getElementById('run-form');
      const resultCard = document.getElementById('result');
      const resultTitle = document.getElementById('result-title');
      const confidence = document.getElementById('confidence');
      const rationaleList = document.getElementById('rationale');
      const newsList = document.getElementById('news');
      const errorCard = document.getElementById('error-card');
      const errorMessage = document.getElementById('error-message');
      const healthStatus = document.getElementById('health-status');

      function showError(message) {
        errorCard.hidden = false;
        errorMessage.textContent = message;
      }

      function clearError() {
        errorCard.hidden = true;
        errorMessage.textContent = '';
      }

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearError();
        resultCard.hidden = true;

        const customPair = document.getElementById('custom-pair').value.trim();
        const selectedPair = customPair ? customPair.toUpperCase() : select.value;

        form.querySelector('button').disabled = true;
        form.querySelector('button').textContent = 'Running...';

        try {
          const response = await fetch(`${apiBase}/run?pair=${encodeURIComponent(selectedPair)}`);
          if (!response.ok) {
            const details = await response.json().catch(() => ({}));
            throw new Error(details.detail || `Request failed (${response.status})`);
          }
          const data = await response.json();

          resultTitle.textContent = `✅ Recommendation for ${data.pair}: ${data.stance}`;
          confidence.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
          rationaleList.innerHTML = '';
          data.rationale.forEach((item) => {
            const li = document.createElement('li');
            li.textContent = item;
            rationaleList.appendChild(li);
          });
          newsList.innerHTML = '';
          data.news.forEach((item) => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.url;
            link.target = '_blank';
            link.rel = 'noreferrer noopener';
            link.textContent = item.title;
            li.appendChild(link);
            li.insertAdjacentText('beforeend', ` — ${item.source}`);
            newsList.appendChild(li);
          });

          resultCard.hidden = false;
        } catch (error) {
          showError(error.message);
        } finally {
          form.querySelector('button').disabled = false;
          form.querySelector('button').textContent = '🚀 Run Strategy';
        }
      });

      async function checkHealth() {
        try {
          const response = await fetch(`${apiBase}/health`);
          if (!response.ok) {
            throw new Error('API health endpoint returned a non-200 status.');
          }
          const data = await response.json();
          healthStatus.classList.remove('loading');
          healthStatus.textContent = `API is healthy ✅ (${data.status})`;
        } catch (error) {
          healthStatus.classList.remove('loading');
          healthStatus.classList.add('status', 'error');
          healthStatus.textContent = 'API not reachable';
          showError(error.message);
        }
      }

      checkHealth();
    </script>
  </body>
</html>
"""

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


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve a lightweight dashboard so the API and UI share one port."""
    return HTMLResponse(content=FRONTEND_HTML)


@app.head("/")
def index_head() -> Response:
    """Fast heartbeat for platforms that probe the root path with HEAD."""
    return Response(status_code=200)
