# tests/unit/test_email_tool.py
import pytest
from src.tools.email_tool import send_strategy_email


@pytest.mark.unit
def test_send_email_dryrun(fake_email_payload):
    result = send_strategy_email(
        fake_email_payload["subject"],
        fake_email_payload["body"],
        dry_run=True,  # ensures we never hit real SMTP
    )

    # Outer MCP wrapper result
    assert "status" in result
    assert result["status"] in ("success", "error")

    # Inner tool payload
    assert "data" in result
    inner = result["data"]

    assert inner["status"] in ("dryrun", "sent", "error")
    assert inner.get("subject") == fake_email_payload["subject"]
