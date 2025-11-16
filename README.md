## 💹 Agentic Forex AI — Multi-Agent Forex Strategy Assistant

### *Built by Syeda Sarah Mashhood*

## 🏗 Architecture Diagram

![Agentic Forex AI Architecture](assets/forex_agentic_architecture.png)

The system follows a modular multi-agent architecture:

- The **API Layer** exposes `/api/run`, `/api/health`, and `/api/metrics`
- The **Agents Layer** coordinates Market, News, Strategy, Validation, and Email agents
- The **Streamlit Dashboard** provides an interactive UI for running strategies and viewing recommendations
- **Prometheus Metrics** power observability and health monitoring

---

### 🧠 Overview

**Agentic Forex AI** is a fully containerized, multi-agent Forex trading intelligence system.
It integrates:

* **FastAPI** backend — for multi-agent orchestration & strategy execution
* **Streamlit** dashboard — for interactive visualization
* **Prometheus metrics** — for real-time monitoring and observability
* **Docker + Railway** — for simple, free, cloud deployment

Each strategy run combines live forex data, market news, and rule-based decision agents to generate daily BUY/SELL/AVOID recommendations.

---

## ⚙️ Features

| Category                 | Feature                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| **💬 AI Orchestration**  | Multi-agent pipeline fetching live data, parsing RSS feeds, generating strategy rationale |
| **🧩 API Layer**         | FastAPI endpoints for `/run`, `/health`, `/metrics`, `/history`                           |
| **📊 Dashboard**         | Streamlit UI for running strategies, viewing insights, and observing metrics              |
| **🧠 Caching**           | In-memory storage of latest recommendations                                               |
| **🚀 Deployment**        | Fully containerized via Docker, easily deployable to Railway                              |
| **📈 Observability**     | Prometheus metrics for latency, request count, and pair-wise runs                         |
| **🩺 Health Monitoring** | `/api/health` endpoint + integrated dashboard system check                                |

---

## 🔧 Prerequisites & Requirements

### System Requirements
- Python 3.10+
- 4 GB RAM (minimum)
- Docker (optional but recommended)
- Stable internet connection (required for yFinance & RSS feeds)

### Python Dependencies
Installed automatically via `requirements.txt`:
- FastAPI, Uvicorn
- Streamlit
- Pydantic
- feedparser
- yfinance
- Prometheus client
- Loguru

### Knowledge Requirements
Users should be familiar with:
- Basic Python scripting
- REST API concepts
- JSON data formats
- Fundamentals of forex candles & terminology

---

## 🧩 Architecture

```
+----------------------------+
|        Streamlit UI        |
|  (dashboard.py)            |
|   ↳ /api/run               |
|   ↳ /api/health            |
|   ↳ /api/metrics           |
+-------------+--------------+
              |
              v
+----------------------------+
|        FastAPI API         |
|  (api.py)                  |
|   - validate_pair()        |
|   - safe_run_pipeline_once()|
|   - expose Prometheus metrics |
+-------------+--------------+
              |
              v
+----------------------------+
|      Multi-Agent Core      |
|  (src/tools, src/agents)   |
|   - fetch forex candles    |
|   - analyze news RSS       |
|   - generate strategies    |
+----------------------------+
```

---
## 🤖 Agent Roles & Responsibilities

**Market Agent**  
Fetches hourly/daily forex candles using yFinance. Handles API errors and retries.

**News Agent**  
Parses financial news via RSS feeds (FXStreet, Investing.com, DailyFX). Extracts timestamps and deduplicates items.

**Strategy Agent**  
Combines candle data and news signals to output BUY / SELL / AVOID recommendations with confidence scoring.

**Validation Guard**  
Validates currency pairs, enforces runtime safety rules, and ensures fallback behavior during failures.

**Email Agent**  
Sends daily strategy summaries to the user’s email (supports Live and Dry modes).

---

## 🔄 Orchestration Framework

All agent interactions are coordinated through a lightweight orchestration layer defined in `src/graph.py`.

The orchestrator:
- Defines the execution order: **Market → News → Strategy → Validation → Email**
- Ensures synchronous communication between agents
- Wraps each agent stage with safe execution via `pipeline_safety.py`
- Applies **timeouts, retries, and fallback logic**
- Captures structured traces for observability and debugging

This design ensures that a failure in one agent does not collapse the entire pipeline and keeps the system modular and extensible.

---

## 🧑‍💻 Human-in-the-Loop (HITL) Integration

Although the system runs autonomously, specific checkpoints allow user oversight:

- **Streamlit Dashboard** — Users can inspect market data, news, and generated recommendations.
- **Email Reports** — Daily summaries let users validate signals before taking action.
- **Validation Guard** — Prevents incorrect inputs from causing invalid decisions.
- **Trace Logs** — Each run is fully traceable for manual review.

This balance of automation and human oversight ensures safe and explainable financial decision support.

---

## 🧠 API Endpoints

| Endpoint               | Method | Description                             |
| ---------------------- | ------ | --------------------------------------- |
| `/api/run?pair=EURUSD` | GET    | Run the forex strategy for a given pair |
| `/api/history`         | GET    | Fetch recent results                    |
| `/api/recommendations` | GET    | Retrieve all cached recommendations     |
| `/api/health`          | GET    | Health check                            |
| `/api/metrics`         | GET    | Prometheus metrics for observability    |

---

## 🔍 Prometheus Metrics

Your API now exposes metrics at `/api/metrics` including:

| Metric                        | Description                                          |
| ----------------------------- | ---------------------------------------------------- |
| `api_request_total`           | Count of API calls by method, path, and status       |
| `api_request_latency_seconds` | Histogram of request durations                       |
| `forex_run_total`             | Successful, failed, or invalid `/run` calls per pair |
| `forex_run_latency_seconds`   | Strategy execution duration per pair                 |
| `forex_last_run_timestamp`    | Timestamp of last successful forex run               |
| `api_health_status`           | 1 if API healthy, 0 otherwise                        |

These are visible directly or through Grafana Cloud (see below).

---

## 🖥️ Dashboard Features

**URL:** `http://localhost:8501` (or Railway public link)

* Select currency pairs (e.g., EURUSD, GBPUSD, AUDCAD)
* Run strategy → view BUY/SELL/AVOID with rationale & news
* Real-time system health indicator
* Observability dashboard — fetches `/api/metrics` for system insight

---

## 🐳 Docker Setup

### Build the image

```bash
docker build -t forex-ai .
```

### Run locally

```bash
docker run -p 8501:8501 -p 8000:8000 forex-ai
```

### Test endpoints

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/run?pair=EURUSD
curl http://localhost:8000/api/metrics
```

---


## 🔐 Environment Variables

This project includes a .env.example file.

Create your .env file by copying it:
```bash
cp .env.example .env
```

Then fill in:

- Currency pairs
- Email sender/receiver
- Gmail App Password
- Optional trace directory

Using env vars with Docker

```bash
docker run --env-file .env -p 8501:8501 -p 8000:8000 forex-ai
```

For Railway deployment, add the same variables in **Settings → Variables**.

---

## 🚀 Deploy on Railway (Free)

1. Push code to GitHub

   ```bash
   git add .
   git commit -m "Add monitoring and observability"
   git push origin main
   ```

2. Log in to [Railway.app](https://railway.app)

3. **Create a new project → Deploy from GitHub repo**

4. Railway will auto-detect the `Dockerfile` and deploy.

5. After deploy:

   * Dashboard URL → `https://your-app.up.railway.app`
   * API → `https://your-app.up.railway.app/api/health`
   * Metrics → `https://your-app.up.railway.app/api/metrics`

---

## 🛡 Resilience & Fault Tolerance

The system is designed for stability under real-world network and data issues:

- **Retry logic** for yFinance and RSS requests  
- **Timeout protection** (via `pipeline_safety.py`)  
- **Graceful fallback behavior** when feeds are unavailable  
- **Input validation** — unsupported or malformed pairs are rejected  
- **Structured error logs** written to `/data/traces/`  
- **Agent isolation** — failure in one agent does not crash the entire pipeline

These guardrails ensure consistent execution even under unreliable data sources.

---

## 📈 (Optional but Recommended) Grafana Cloud Integration — *Free setup*

1. Go to [https://grafana.com/products/cloud/](https://grafana.com/products/cloud/)
   Create a **free Grafana Cloud account**

2. In your Grafana account:

   * Navigate to **Connections → Prometheus**
   * Choose **“Add remote-write endpoint”**

3. Copy your Grafana Cloud **remote_write URL** and **API key**

4. In Railway → your project → **Settings → Variables**, add:

   ```env
   PROMETHEUS_REMOTE_URL=<your_grafana_url>
   PROMETHEUS_API_KEY=<your_grafana_key>
   ```

5. Optional: connect via [Prometheus Agent](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-prometheus-agent/) if you prefer to forward metrics.

6. Add a **Prometheus Data Source** in Grafana:

   ```
   URL: https://your-app.up.railway.app/api/metrics
   ```

7. Create a new **Dashboard** → import visualizations for:

   * `forex_run_total`
   * `forex_run_latency_seconds`
   * `api_request_total`
   * `api_health_status`

✅ You now have a **live observability panel** for your Agentic Forex AI.

---

## 🧾 Folder Structure

```
fx_multiagent/
├── src/
│   ├── agents/
│   ├── tools/
│   ├── guardrails/
│   ├── schemas.py
│   ├── graph.py
│   └── ...
├── api.py
├── dashboard.py
├── Dockerfile
├── supervisord.conf
├── requirements.txt
└── README.md
```

---

## 🧰 Tech Stack

| Layer                   | Tools                |
| ----------------------- | -------------------- |
| **Backend**             | FastAPI, Loguru      |
| **Frontend**            | Streamlit            |
| **Metrics**             | Prometheus client    |
| **Containerization**    | Docker, Supervisor   |
| **Deployment**          | Railway              |
| **Optional Monitoring** | Grafana Cloud (free) |

---

## ✅ Health Check

| Component                    | URL            | Status      |
| ---------------------------- | -------------- | ----------- |
| **FastAPI**                  | `/api/health`  | ✅ OK        |
| **Streamlit**                | `/`            | ✅ Running   |
| **Prometheus Metrics**       | `/api/metrics` | ✅ Exposed   |
| **Grafana Cloud (optional)** | Remote write   | 🟢 Optional |

---

## 🐞 Troubleshooting Guide

**RSS feeds return 0 items**  
• RSS source may be unavailable → retry  
• Check firewall / internet  
• Some feeds (DailyFX) block too many requests

**Email sending fails**  
• Verify Gmail App Password  
• Ensure `EMAIL_USER` and `EMAIL_PASS` env variables are set  
• Check Google “less secure app” restrictions

**yFinance returning empty data**  
• This is common during off-market hours  
• Try switching interval from `1h` to `30m`  
• yFinance occasionally rate-limits

**Docker container not starting**  
• Make sure Docker Desktop is running  
• Run: `docker system prune -f` and rebuild

**Prometheus metrics not visible**  
• Ensure `/api/metrics` is exposed  
• On Railway, verify no port conflict

---

## 🧡 Credits

**Developed by:** *Syeda Sarah Mashhood*
**Purpose:** Educational & analytical project for multi-agent observability and decision automation in Forex.
**Stack:** Python · FastAPI · Streamlit · Prometheus · Docker · Railway

---
## 🔧 Maintenance & Support Status

Agentic Forex AI is an actively maintained project. Updates include:

- Dependency updates (FastAPI, yFinance, Prometheus client)
- Bug fixes and resilience improvements
- Enhancements to strategy logic and agent interactions
- Security patches when required
- Migration guides provided for breaking changes

For issues, suggestions, or feature requests, please use the GitHub **Issues** tab.

---

## 📜 License

This project is licensed under the **Creative Commons Attribution-ShareAlike (CC BY-SA 4.0)** license.

You are free to:
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit.
- **ShareAlike** — Derivatives must be distributed under the same license.

See the full license in the `LICENSE` file.

---
## 🧪 Testing

This project uses a layered test suite to validate behavior from individual agents up to full end-to-end runs.

### Test Types

- **Unit Tests** (`tests/unit/`)  
  Validate each agent, tool, and guard in isolation (e.g., candle fetching, RSS parsing, recommendation logic).

- **Integration Tests** (`tests/integration/`)  
  Exercise the multi-agent pipeline across components, ensuring that Market → News → Strategy → Validation → Email work together correctly.

- **System / End-to-End Tests** (`tests/system/`)  
  Hit the public FastAPI endpoints (`/api/run`, `/api/health`, `/api/metrics`) and verify that requests flow through the entire stack, including orchestration and logging.

- **Performance Tests** (`tests/performance/`)  
  Measure latency and throughput for multiple currency pairs and validate that Prometheus metrics reflect real load.

### Running Tests

Run the full suite:

```bash
pytest --maxfail=1 --disable-warnings -q
```

With coverage (goal: ≥ 70% over core logic in `src/agents`, `src/tools`, `src/guards`, and `src/graph`)

Current coverage (measured via `pytest --cov=src`) is **~56%** overall, with higher coverage on critical modules such as validation, schemas, orchestration (`graph.py`), and core tools (`yfinance_tool.py`, `news_tool.py`). Additional tests are planned for agent wrappers and pipeline safety fallbacks.

```bash
pytest --cov=src
```


---

## 🪄 Next Steps (Optional Enhancements)

* [ ] Add **Grafana JSON dashboard template**
* [ ] Push logs to **Logtail / Loki**
* [ ] Add persistent storage (PostgreSQL or Redis cache)
* [ ] Include CI/CD GitHub workflow
* [ ] Use **LangGraph** for more agentic orchestration

