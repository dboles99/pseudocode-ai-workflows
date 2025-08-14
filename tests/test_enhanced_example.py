import sys, pathlib, pytest

# Add src/python to import path
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

import enhanced_v2_example as m
from enhanced_v2_example import process_items, ContractError, with_retry

def test_process_items_happy_path():
    # evens <= 5 -> [2,4] -> squares = [4,16]
    assert process_items([1,2,3,4,5,6], limiter=5, timeout_s=5.0) == [4, 16]

def test_contracts_invalid_limiter():
    with pytest.raises(ContractError):
        process_items([1,2], limiter=-1)

def test_contracts_bad_item_type():
    with pytest.raises(ContractError):
        process_items([1, "x", 2], limiter=5, timeout_s=5.0)

def test_with_retry_success_after_one_retry():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise ValueError("boom")
        return 42
    assert with_retry(flaky, retries=1) == 42

def test_timeout_raises_fast(monkeypatch):
    # Make the second perf_counter call jump forward a lot to force timeout
    base = 1000.0
    seq = iter([base, base + 999.0])
    monkeypatch.setattr(m.time, "perf_counter", lambda: next(seq))
    with pytest.raises(TimeoutError):
        process_items([1,2,3], limiter=10, timeout_s=0.0)
