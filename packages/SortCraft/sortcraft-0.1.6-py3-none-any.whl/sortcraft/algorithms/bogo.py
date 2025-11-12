from typing import Sequence, TypeVar, List
import random

T = TypeVar("T")

def bogo_sort(items: Sequence[T], max_attempts: int = 50000) -> List[T]:
    """
    Bogo sort (stupid sort, O(∞) expected), randomly shuffles list until sorted.

    Args:
        items (Sequence[T]): Sequence of comparable items.
        max_attempts (int, optional): Safety limit to prevent infinite loops.
            Defaults to 50000.

    Returns:
        List[T]: Sorted list if successful, or the final shuffled list if max_attempts exceeded.

    Raises:
        TypeError: If items is not a sequence or items are not comparable.
        ValueError: If max_attempts is not a positive integer.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if you get lucky).
        - Used only for jokes, demos, or unit tests for misbehavior.

    Examples:
        >>> bogo_sort([2, 3, 1], max_attempts=10000)
        [1, 2, 3]

        >>> bogo_sort([], max_attempts=10)
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.

        >>> bogo_sort(["a", "b", "c"], max_attempts=1)
        ['b', 'c', 'a']  # May vary
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")

    arr = list(items)
    attempts = 0
    try:
        _ = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1
    return arr