import sys, pathlib, pytest

# add src/python to the import path
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

from enhanced_v2_example import process_items, ContractError

def test_process_items_happy_path():
    # evens <= 5 -> square them -> [2^2, 4^2] = [4, 16]
    assert process_items([1,2,3,4,5,6], limiter=5, timeout_s=5.0) == [4, 16]

def test_contracts_invalid_limiter():
    with pytest.raises(ContractError):
        process_items([1,2], limiter=-1)

def test_contracts_bad_item_type():
    with pytest.raises(ContractError):
        process_items([1, "x", 2], limiter=5, timeout_s=5.0)
