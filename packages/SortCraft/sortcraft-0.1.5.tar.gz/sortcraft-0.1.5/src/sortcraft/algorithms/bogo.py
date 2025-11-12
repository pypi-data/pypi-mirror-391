from typing import Sequence, TypeVar, List
import random

T = TypeVar("T")

def bogo_sort(items: Sequence[T], max_attempts: int = 50000) -> List[T]:
    """
    Bogo sort (stupid sort, O(∞) expected), randomly shuffles list until sorted.

    Args:
        items: Sequence of comparable items.
        max_attempts: Safety limit to prevent infinite loops.

    Returns:
        List[T]: Sorted list or input if max_attempts exceeded.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if you get lucky).
        - Used only for jokes, demos, or unit tests for misbehavior.

    Examples:
        >>> bogo_sort([2, 3, 1], max_attempts=10000)
        [1, 2, 3]
    """
    arr = list(items)
    attempts = 0
    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1
    return arr
