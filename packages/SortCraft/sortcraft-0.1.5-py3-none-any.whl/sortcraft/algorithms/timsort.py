from typing import Sequence, TypeVar, List

T = TypeVar("T")

def timsort(items: Sequence[T]) -> List[T]:
    """
    TimSort (stable, O(n log n)), Python's built-in sorting algorithm.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.
        - Used by Python's built-in sorted() and .sort().

    Examples:
        >>> timsort([3, 1, 2])
        [1, 2, 3]
    """
    return sorted(items)  # uses Python's built-in TimSort