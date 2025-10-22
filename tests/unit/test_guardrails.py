# tests/unit/test_guardrails.py
from src.guardrails.input_validation import validate_pair, validate_pairs
from src.guardrails.pipeline_safety import safe_run_pipeline_once, _fallback_recommendation
from src.schemas import Recommendation

print("\n=== Testing input_validation.py ===\n")

# --- Single pair tests ---
test_pairs = ["EURUSD", "gbpusd", "INVALID", 123]

for p in test_pairs:
    try:
        validated = validate_pair(p)
        print(f"✅ Pair '{p}' validated as '{validated}'")
    except Exception as e:
        print(f"❌ Pair '{p}' validation failed: {e}")

# --- Multiple pairs tests ---
multi_pairs_tests = [
    ["EURUSD", "USDJPY"],       # valid
    ["AUDCAD", "INVALID"],      # contains invalid
]

for pairs in multi_pairs_tests:
    try:
        validated = validate_pairs(pairs)
        print(f"✅ Pairs {pairs} validated as {validated}")
    except Exception as e:
        print(f"❌ Pairs {pairs} validation failed: {e}")


print("\n=== Testing pipeline_safety.py ===\n")

# --- Test fallback recommendation ---
fallback = _fallback_recommendation("EURUSD")
print(f"Fallback recommendation: pair={fallback.pair}, stance={fallback.stance}, confidence={fallback.confidence}")
print(f"Rationale: {fallback.rationale}\n")

# --- Test safe_run_pipeline_once ---
# NOTE: This will actually run your pipeline; dry-run=True is already set in safe_run_pipeline_once
test_pairs_for_pipeline = ["EURUSD", "GBPUSD"]

for pair in test_pairs_for_pipeline:
    try:
        rec = safe_run_pipeline_once(pair, retries=2, delay=0.5)
        if isinstance(rec, Recommendation):
            print(f"✅ Safe run for {pair}: stance={rec.stance}, confidence={rec.confidence}")
        else:
            print(f"⚠️ Safe run for {pair} returned unexpected type: {type(rec)}")
    except Exception as e:
        print(f"❌ Safe run for {pair} failed: {e}")
