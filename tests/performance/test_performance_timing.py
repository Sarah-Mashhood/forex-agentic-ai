import pytest
import time
from src.tools.strategy_tools import run_strategy_for_pair

@pytest.mark.performance
def test_strategy_exec_time(sample_pair):
    start = time.time()
    run_strategy_for_pair(sample_pair)
    duration = time.time() - start
    assert duration < 10, f"Strategy took too long: {duration:.2f}s"
