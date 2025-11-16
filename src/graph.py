# src/graph.py
"""
End-to-end multi-agent orchestration for the Forex strategy system.

Flow:
1️⃣ Market + News (via run_strategy_for_pair)
2️⃣ Strategy Agent
3️⃣ Email Agent
4️⃣ Tracing for evaluation and audit
"""

import os
import json
import uuid
from datetime import datetime, timezone
from src.tools.strategy_tools import run_strategy_for_pair
from src.tools.email_tool import send_strategy_email

# Local trace storage (env override with sensible default)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
DEFAULT_TRACE_DIR = os.path.join(BASE_DIR, "data", "traces")
TRACE_DIR = os.getenv("TRACE_DIR", DEFAULT_TRACE_DIR)
os.makedirs(TRACE_DIR, exist_ok=True)


def save_trace(run_id: str, trace: dict):
    """Persist trace log for evaluation/fallback checks."""
    path = os.path.join(TRACE_DIR, f"{run_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, default=str)


def run_pipeline_once(pair: str, dry_run_email: bool = True):
    """
    Executes the full pipeline for one forex pair.
    Handles market, news, strategy, and email stages.
    """
    run_id = uuid.uuid4().hex
    trace = {
        "run_id": run_id,
        "pair": pair,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }

    rec = None  # ensure defined even if strategy fails

    try:
        print(f"\n🔹 Starting pipeline for {pair}")

        # 1️⃣ Strategy Tool (includes market + news)
        trace["steps"].append({
            "step": "strategy_tool_start",
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        rec = run_strategy_for_pair(pair)

        # Validate Recommendation fields
        rec.stance = getattr(rec, "stance", "AVOID")
        rec.confidence = getattr(rec, "confidence", 0.0)
        rec.rationale = getattr(rec, "rationale", ["No rationale available"])
        rec.news = getattr(rec, "news", [])

        trace["steps"].append({
            "step": "strategy_tool_end",
            "stance": rec.stance,
            "confidence": rec.confidence,
            "rationale_count": len(rec.rationale),
            "news_count": len(rec.news),
            "ts": datetime.now(timezone.utc).isoformat(),
        })

        # 2️⃣ Email Agent
        trace["steps"].append({
            "step": "email_agent_start",
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        subject = f"Daily Forex Strategy — {rec.pair} — {rec.stance}"
        rationale = "\n".join([f"- {r}" for r in rec.rationale])
        body = (
            f"Pair: {rec.pair}\n"
            f"Stance: {rec.stance}\n"
            f"Confidence: {rec.confidence:.2f}\n\n"
            f"Rationale:\n{rationale}\n"
        )

        if rec.news:
            body += "\n📰 News Highlights:\n"
            for n in rec.news[:5]:
                title = getattr(n, "title", None) or "No title"
                source = getattr(n, "source", None) or "Unknown"
                url = getattr(n, "url", None)
                url_suffix = f" ({url})" if url else ""
                body += f"• {title} — {source}{url_suffix}\n"

        email_resp = send_strategy_email(subject, body, dry_run=dry_run_email)

        trace["steps"].append({
            "step": "email_agent_end",
            "email_status": email_resp.get("status"),
            "recipient": email_resp.get("recipient"),
            "ts": datetime.now(timezone.utc).isoformat(),
        })

        trace["finished_at"] = datetime.now(timezone.utc).isoformat()
        trace["status"] = "success"

        if email_resp.get("status") == "sent":
            print(f"📧 Email successfully sent to {email_resp.get('recipient')}")
        else:
            print("✉️ Email simulated (dry-run mode)")

        print(f"✅ Completed pipeline for {pair}")

    except Exception as e:
        trace["error"] = str(e)
        trace["status"] = "error"
        print(f"❌ Error processing {pair}: {e}")

    finally:
        if rec is not None:
            trace["recommendation"] = rec
        save_trace(run_id, trace)
        return trace


def run_pipeline_for_pairs(pairs: list, dry_run_email: bool = True):
    """Runs the multi-agent pipeline for multiple currency pairs."""
    all_traces = []
    print(f"\n🚀 Starting multi-agent forex run at {datetime.now(timezone.utc).isoformat()}")
    for p in pairs:
        t = run_pipeline_once(p, dry_run_email=dry_run_email)
        all_traces.append(t)
    print("\n🏁 All currency pairs processed.\n")
    return all_traces
