# tests/unit/test_guardrails.py
import pytest
from src.guardrails.input_validation import validate_pair, validate_pairs
from src.guardrails.pipeline_safety import _fallback_recommendation
from src.schemas import Recommendation


def test_validate_pair_valid_uppercase():
    assert validate_pair("EURUSD") == "EURUSD"


def test_validate_pair_valid_lowercase():
    assert validate_pair("gbpusd") == "GBPUSD"


def test_validate_pair_invalid_raises():
    with pytest.raises(ValueError):
        validate_pair("INVALID")


def test_validate_pair_non_string_raises():
    with pytest.raises(ValueError):
        validate_pair(123)  # type: ignore


def test_validate_pairs_all_valid():
    pairs = ["EURUSD", "usdjpy"]
    validated = validate_pairs(pairs)
    assert validated == ["EURUSD", "USDJPY"]


def test_validate_pairs_with_invalid_raises():
    with pytest.raises(ValueError):
        validate_pairs(["AUDCAD", "INVALID"])


def test_fallback_recommendation_shape():
    rec = _fallback_recommendation("EURUSD")
    assert isinstance(rec, Recommendation)
    assert rec.pair == "EURUSD"
    assert rec.stance == "AVOID"
    assert rec.confidence == 0.0
    assert rec.rationale  # non-empty list
