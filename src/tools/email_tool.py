"""
email_tool.py
--------------
MCP-based tool for sending (or simulating) daily forex strategy emails.
Supports both dry-run printing and actual SMTP email sending.
"""

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from src.tools.mcp import mcp_tool

load_dotenv()

@mcp_tool(name="send_strategy_email", description="Send a daily forex strategy email or print it in dry-run mode.")
def send_strategy_email(
    subject: str,
    body: str,
    recipient: str = None,
    dry_run: bool = None
):
    """
    Send or simulate an email containing the forex trading strategy summary.

    Args:
        subject (str): Email subject line.
        body (str): Email message body.
        recipient (str, optional): Target email address. Defaults to EMAIL_TO in .env.
        dry_run (bool, optional): If True, print instead of sending. Reads EMAIL_DRYRUN from .env if None.

    Returns:
        dict: { "status": "sent" | "dryrun" | "error", "recipient": str, "subject": str }
    """

    # --- Load environment settings ---
    recipient = recipient or os.getenv("EMAIL_TO")
    sender = os.getenv("EMAIL_FROM", "forex-agent@localhost")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    dry_run = dry_run if dry_run is not None else os.getenv("EMAIL_DRYRUN", "True").lower() == "true"

    # --- Validate configuration ---
    if not recipient:
        print("⚠️ No recipient specified; skipping email.")
        dry_run = True

    if dry_run or not smtp_user or not smtp_pass:
        print("\n=== DRYRUN EMAIL ===")
        print(f"Subject: {subject}")
        print(body)
        print("====================\n")
        return {"status": "dryrun", "subject": subject, "recipient": recipient}

    try:
        # --- Construct email ---
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # --- Send via Gmail SMTP ---
        print(f"📤 Connecting to SMTP server {smtp_host}:{smtp_port} ...")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        print(f"✅ Email sent successfully to {recipient}")
        return {"status": "sent", "recipient": recipient, "subject": subject}

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {"status": "error", "recipient": recipient, "subject": subject, "error": str(e)}


def test_send():
    """Quick manual test: send or dry-run an email without running full pipeline."""
    dry_run_env = os.getenv("EMAIL_DRYRUN", "True").lower() == "true"
    subject = "📈 FX Test Email"
    body = "This is a test email from your Forex Multi-Agent project.\nIf you're reading this, SMTP works!"
    return send_strategy_email(subject, body, dry_run=dry_run_env)


if __name__ == "__main__":
    test_send()