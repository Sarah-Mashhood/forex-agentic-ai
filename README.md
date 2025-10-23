## 💹 Agentic Forex AI — Multi-Agent Forex Strategy Assistant

### *Built by Syeda Sarah Mashhood*

![Architecture Diagram](https://user-images.githubusercontent.com/placeholder/forex-ai-architecture.png)
*(Optional: add your architecture image later)*

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

## 🧡 Credits

**Developed by:** *Syeda Sarah Mashhood*
**Purpose:** Educational & analytical project for multi-agent observability and decision automation in Forex.
**Stack:** Python · FastAPI · Streamlit · Prometheus · Docker · Railway

---

## 🪄 Next Steps (Optional Enhancements)

* [ ] Add **Grafana JSON dashboard template**
* [ ] Push logs to **Logtail / Loki**
* [ ] Add persistent storage (PostgreSQL or Redis cache)
* [ ] Include CI/CD GitHub workflow
* [ ] Use **LangGraph** for more agentic orchestration

