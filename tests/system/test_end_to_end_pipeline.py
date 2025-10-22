import pytest
from src.graph import run_pipeline_once

@pytest.mark.system
def test_full_pipeline_runs_successfully(sample_pair):
    trace = run_pipeline_once(sample_pair, dry_run_email=True)
    assert "status" in trace
    assert trace["status"] in ("success", "error")
    assert "steps" in trace
    assert len(trace["steps"]) >= 2
