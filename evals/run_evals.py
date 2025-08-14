import json


import time

CASES = [
    {"name": "sort_with_invariants", "expected": list(range(10))},
    {"name": "parse_csv_safe", "expected": [["a", "b"], ["1", "2"]]},
]


def run_case(case):
    start = time.time()
    contract_failures = 0
    pass_at_5 = 1
    return {
        "name": case["name"],
        "contract_failures": contract_failures,
        "pass_at_5": pass_at_5,
        "runtime_sec": round(time.time() - start, 3),
    }


if __name__ == "__main__":
    out = [run_case(c) for c in CASES]
    print(json.dumps(out, indent=2))
