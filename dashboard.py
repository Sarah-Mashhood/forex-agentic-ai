# dashboard.py
import os
import requests
import streamlit as st

# ===============================
# 🌐 API Base URL Handling
# ===============================
# Uses environment variable in production (Railway), falls back to localhost for local dev
API_URL = os.getenv("API_URL", "http://localhost:8000/api").rstrip("/")

st.set_page_config(page_title="Agentic Forex AI Dashboard", page_icon="💹", layout="centered")

st.title("💹 Agentic Forex AI Dashboard")

# ===============================
# Currency Pair Input
# ===============================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "AUDCAD", "GBPCAD"]
pair = st.selectbox("Select Currency Pair", options=pairs)
custom_pair = st.text_input("Or add your own custom currency pair (e.g., NZDUSD, USDCHF):")

if custom_pair.strip():
    pair = custom_pair.strip().upper()

# ===============================
# Run Strategy
# ===============================
if st.button("🚀 Run Strategy"):
    try:
        with st.spinner("Running strategy..."):
            response = requests.get(f"{API_URL}/run", params={"pair": pair}, timeout=60)
            response.raise_for_status()
            data = response.json()

        # ===============================
        # Show Output
        # ===============================
        st.success(f"✅ Recommendation for {data['pair']}: **{data['stance']}**")
        st.metric("Confidence", f"{data['confidence'] * 100:.1f}%")
        st.write("**Rationale:**")
        for line in data["rationale"]:
            st.write(f"• {line}")

        st.write("**Related News:**")
        for item in data["news"]:
            st.markdown(f"- [{item['title']}]({item['url']}) — *{item['source']}*")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")
        st.info(f"Hint: Is your API_URL set correctly?\n\n**Current API_URL:** `{API_URL}`")

# ===============================
# Health Check Section
# ===============================
st.divider()
st.subheader("🩺 System Health")
try:
    health = requests.get(f"{API_URL}/health", timeout=10)
    if health.status_code == 200:
        st.success("API is healthy ✅")
    else:
        st.warning(f"Health check failed ({health.status_code})")
except Exception:
    st.warning("⚠️ API not reachable")

# ===============================
# Footer
# ===============================
st.caption("Built with ❤️ by Syeda Sarah Mashhood | Agentic Forex AI")
