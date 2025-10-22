# dashboard.py
import streamlit as st
import requests

# ----------------------------
# API Base URL
# ----------------------------
API_BASE = "http://localhost:8000"
try:
    API_BASE = st.secrets.get("API_URL", API_BASE)
except Exception:
    pass

# ----------------------------
# Streamlit App
# ----------------------------
st.set_page_config(page_title="Forex Multi-Agent Dashboard", layout="centered")
st.title("💹 Agentic Forex AI Dashboard")

# Default pairs
default_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "AUDCAD", "GBPCAD"]
selected_pair = st.selectbox("Select Currency Pair", default_pairs)

# --- Custom pair input ---
st.markdown("Or add your own custom currency pair:")
custom_pair = st.text_input("Enter custom pair (e.g., NZDUSD, USDCHF):").strip().upper()

# If user entered a custom pair, use it instead of dropdown
final_pair = custom_pair if custom_pair else selected_pair

if st.button("🚀 Run Strategy"):
    if not final_pair:
        st.warning("Please select or enter a currency pair.")
    else:
        with st.spinner(f"Running pipeline for {final_pair}..."):
            try:
                response = requests.get(f"{API_BASE}/run?pair={final_pair}", timeout=90)
                if response.status_code == 200:
                    rec = response.json()

                    st.subheader(f"📊 Recommendation for {rec['pair']}")
                    st.write(f"**Stance:** {rec['stance']}")
                    st.write(f"**Confidence:** {rec['confidence']:.2f}")
                    st.write(f"**Horizon:** {rec['horizon_hours']} hours")

                    st.markdown("### 🧠 Rationale")
                    for r in rec.get("rationale", []):
                        st.markdown(f"- {r}")

                    # --- News section ---
                    if rec.get("news"):
                        st.markdown("### 📰 Related News")
                        for item in rec["news"]:
                            with st.expander(item.get("title", "No title")):
                                st.write(f"**Source:** {item.get('source', 'Unknown')}")
                                if item.get("url"):
                                    st.markdown(f"[Read more]({item['url']})")
                                st.caption(item.get("timestamp", ""))
                    else:
                        st.info("No news found for this currency pair.")

                else:
                    st.error(f"API error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"❌ Request failed: {e}")

st.markdown("---")
st.caption(f"Connected to API: {API_BASE}")
