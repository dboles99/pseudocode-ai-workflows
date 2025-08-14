"""
PURPOSE: Batch filter & process items with contracts, timeout, retry
INPUTS: items: Iterable[int], limiter: int
OUTPUTS: list[int]
"""

from __future__ import annotations
from typing import Callable, Iterable, List
import time


class ContractError(AssertionError):
    pass


class RetryError(RuntimeError):
    pass


def requires(cond: bool, msg: str = "") -> None:
    if not cond:
        raise ContractError(f"REQUIRES failed: {msg}")


def ensures(cond: bool, msg: str = "") -> None:
    if not cond:
        raise ContractError(f"ENSURES failed: {msg}")


def with_retry(fn: Callable[[], int], retries: int = 2, delay_s: float = 0.0) -> int:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if attempt < retries:
                if delay_s > 0:
                    time.sleep(delay_s)
            else:
                raise RetryError(f"exhausted retries after {retries} retries") from e
    # for type-checkers; code never reaches here
    raise RetryError("unreachable") from last_exc


def process_items(
    items: Iterable[int], limiter: int, timeout_s: float = 2.0
) -> List[int]:
    """
    Filter even ints <= limiter and square them, with simple contracts, timeout, and retry demo.
    """
    start = time.perf_counter()
    requires(
        isinstance(limiter, int) and limiter >= 0, "limiter must be a non-negative int"
    )

    out: List[int] = []
    for x in items:
        # cooperative timeout check
        if time.perf_counter() - start > timeout_s:
            raise TimeoutError("process_items timed out")
        requires(isinstance(x, int), "all items must be ints")

        if x <= limiter and x % 2 == 0:

            def work() -> int:
                # demo: if a specific sentinel were present, it would fail once, then succeed on retry
                # (we don't trigger this in tests; it's illustrative)
                return x * x

            y = with_retry(work, retries=1, delay_s=0.0)
            out.append(y)

    ensures(
        all(y <= (limiter * limiter) for y in out),
        "outputs should be bounded by limiter^2",
    )
    return out
