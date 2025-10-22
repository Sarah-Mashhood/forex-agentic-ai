# src/guardrails/input_validation.py
from typing import List

# Allowed currency pairs
ALLOWED_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "AUDCAD", "GBPCAD"
]

def validate_pair(pair: str) -> str:
    """
    Validates a currency pair.
    Returns uppercase pair if valid.
    Raises ValueError if invalid.
    """
    if not isinstance(pair, str):
        raise ValueError(f"Pair must be a string, got {type(pair)}")
    
    pair = pair.strip().upper()
    if pair not in ALLOWED_PAIRS:
        raise ValueError(f"Pair '{pair}' is not supported. Allowed: {ALLOWED_PAIRS}")
    
    return pair

def validate_pairs(pairs: List[str]) -> List[str]:
    """
    Validates a list of currency pairs.
    Returns list of valid uppercase pairs.
    Raises ValueError if any invalid pair.
    """
    valid_pairs = []
    for p in pairs:
        valid_pairs.append(validate_pair(p))
    return valid_pairs
