import pytest
from src.tools.strategy_tools import run_strategy_for_pair

@pytest.mark.integration
def test_strategy_tool_output_shape(sample_pair):
    rec = run_strategy_for_pair(sample_pair)
    assert rec is not None
    assert hasattr(rec, "pair")
    assert hasattr(rec, "stance")
    assert hasattr(rec, "confidence")
    assert isinstance(rec.confidence, float)
    assert rec.stance in ("BUY", "SELL", "AVOID")
