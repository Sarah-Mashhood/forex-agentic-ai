import os
from src.schemas import Recommendation
from src.tools.email_tool import send_strategy_email

def send_email(rec: Recommendation):
    """
    Sends or prints a daily forex strategy email depending on EMAIL_DRYRUN setting.
    """
    dry_run = os.getenv("EMAIL_DRYRUN", "True").lower() == "true"

    # --- Email subject ---
    subject = f"Daily Forex Strategy — {rec.pair} — {rec.stance}"

    # --- Core message ---
    lines = [
        f"Pair: {rec.pair}",
        f"Stance: {rec.stance}",
        f"Confidence: {rec.confidence:.2f}",
        "",
        "Rationale:",
        *[f"- {r}" for r in rec.rationale]
    ]

    # --- Add News Highlights (if any) ---
    if hasattr(rec, "news") and rec.news:
        lines.append("\n📰 News Highlights:")
        for n in rec.news[:5]:
            title = n.title or "No title"
            source = n.source or "Unknown"
            url = f" ({n.url})" if n.url else ""
            lines.append(f"• {title} — {source}{url}")

    body = "\n".join(lines)

    # --- Send (real or dry-run) ---
    return send_strategy_email(subject, body, dry_run=dry_run)
