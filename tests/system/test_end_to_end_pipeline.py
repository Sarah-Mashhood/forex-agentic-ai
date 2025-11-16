# tests/system/testend_to_end_pipeline.py
import pytest
from src.graph import run_pipeline_once


@pytest.fixture
def sample_pair():
    return "EURUSD"


@pytest.mark.system
def test_full_pipeline_runs_successfully(sample_pair):
    trace = run_pipeline_once(sample_pair, dry_run_email=True)

    # Basic required structure
    assert "status" in trace
    assert trace["status"] in ("success", "error")

    assert "run_id" in trace
    assert isinstance(trace["run_id"], str)

    assert "pair" in trace
    assert trace["pair"].upper() == sample_pair.upper()

    # Steps should exist and include at least one stage
    assert "steps" in trace
    assert isinstance(trace["steps"], list)
    assert len(trace["steps"]) >= 1

    # Each step should contain a timestamp
    for step in trace["steps"]:
        assert "ts" in step

    # Recommendation may or may not exist depending on success
    if trace["status"] == "success":
        assert "recommendation" in trace
