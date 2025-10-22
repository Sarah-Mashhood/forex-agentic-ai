# tests/conftest.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.tools.strategy_tools import run_strategy_for_pair
from src.tools.email_tool import send_strategy_email

@pytest.fixture
def sample_pair():
    return "EURUSD"

@pytest.fixture
def sample_recommendation(sample_pair):
    """Run one full strategy to get a real Recommendation object."""
    return run_strategy_for_pair(sample_pair)

@pytest.fixture
def fake_email_payload():
    return {
        "subject": "FX Test Email",
        "body": "This is a test body for email sending.",
        "dry_run": True
    }
