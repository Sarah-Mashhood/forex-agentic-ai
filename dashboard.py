import os
import requests
import streamlit as st
import re
import time
from loguru import logger

# ==================================
# 🌐 API Base URL
# ==================================
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Logging setup (send logs to stdout for Railway)
logger.remove()
logger.add(sink=lambda msg: print(msg, end=""), level="INFO")

st.set_page_config(page_title="Agentic Forex AI Dashboard", page_icon="💹", layout="centered")
st.title("💹 Agentic Forex AI Dashboard")

# ==================================
# Currency Pair Input
# ==================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
pair = st.selectbox("Select Currency Pair", options=pairs)
custom_pair = st.text_input("Or add your own custom currency pair (e.g., NZDUSD, USDCHF):")

if custom_pair.strip():
    pair = custom_pair.strip().upper()

# ==================================
# Run Strategy
# ==================================
if st.button("🚀 Run Strategy"):
    logger.info(f"Run Strategy clicked for {pair}")
    try:
        with st.spinner("Running strategy..."):
            response = requests.get(f"{API_URL}/run", params={"pair": pair}, timeout=60)
            response.raise_for_status()
            data = response.json()

        st.success(f"✅ Recommendation for {data['pair']}: **{data['stance']}**")
        st.metric("Confidence", f"{data['confidence'] * 100:.1f}%")
        st.write("**Rationale:**")
        for line in data.get("rationale", []):
            st.write(f"• {line}")

        # ---- Related News section with graceful empty handling ----
        st.write("**Related News:**")
        news_items = data.get("news") or []
        if news_items:
            for item in news_items:
                title = item.get("title") or "No title"
                source = item.get("source") or "Unknown"
                url = item.get("url")
                if url:
                    st.markdown(f"- [{title}]({url}) — *{source}*")
                else:
                    st.markdown(f"- {title} — *{source}*")
        else:
            st.write("No recent news articles found for this pair in the last 48 hours.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        st.error(f"❌ Request failed: {e}")
        st.info(f"Hint: Is your API_URL set correctly?\n\n**Current API_URL:** `{API_URL}`")

# ==================================
# Health Check Section
# ==================================
st.divider()
st.subheader("🩺 System Health")

health_status = "❌ API not reachable"
try:
    logger.info("Performing health check")
    health = requests.get(f"{API_URL}/health", timeout=10)
    if health.status_code == 200:
        health_status = "✅ API Healthy"
        st.success("API is healthy ✅")
    else:
        st.warning(f"Health check failed ({health.status_code})")
except Exception as e:
    logger.error(f"Health check failed: {e}")
    st.warning("⚠️ API not reachable")

# ==================================
# 📈 Observability & Metrics
# ==================================
st.divider()
st.subheader("📊 Observability Dashboard")

try:
    metrics_response = requests.get(f"{API_URL}/metrics", timeout=10)
    if metrics_response.status_code == 200:
        metrics_text = metrics_response.text

        # Extract latency histogram buckets
        latencies = re.findall(
            r'api_request_latency_seconds_bucket{path=".*?"[^}]*} (\d+)', metrics_text
        )
        total_requests = re.findall(
            r'api_request_total{method="GET",path=".*?",status="200"} (\d+)', metrics_text
        )
        health_gauge = re.search(r'api_health_status (\d+)', metrics_text)

        latency_value = int(latencies[-1]) if latencies else 0
        total_reqs = sum(map(int, total_requests)) if total_requests else 0
        health_value = int(health_gauge.group(1)) if health_gauge else 0

        st.metric("API Health", "✅" if health_value else "⚠️", help="Gauge 1 = Healthy, 0 = Unhealthy")
        st.metric("Total API Requests", total_reqs)
        st.metric("Recent Latency (observed count)", latency_value)

        # ---- Removed tiny sparkline chart that caused the '0 0' at bottom ----
        # If you ever want a chart back, you can gate it like:
        # if len(latencies) > 1 and any(int(v) > 0 for v in latencies):
        #     latency_chart = [int(v) for v in latencies[-20:]]
        #     st.line_chart(latency_chart, height=100)

    else:
        st.warning("⚠️ Unable to fetch metrics from /api/metrics")
except Exception as e:
    logger.error(f"Metrics fetch failed: {e}")
    st.warning("⚠️ Observability metrics not available")

# ==================================
# Footer
# ==================================
st.caption("Built with ❤️ by Syeda Sarah Mashhood | Agentic Forex AI")
