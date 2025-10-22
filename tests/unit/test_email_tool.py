import pytest
from src.tools.email_tool import send_strategy_email

@pytest.mark.unit
def test_send_email_dryrun(fake_email_payload):
    result = send_strategy_email(
        fake_email_payload["subject"],
        fake_email_payload["body"],
        dry_run=True
    )
    assert result["status"] in ("dry_run", "sent", "skipped", "success")

