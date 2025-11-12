from typing import Sequence, TypeVar, List

T = TypeVar("T")

def timsort(items: Sequence[T]) -> List[T]:
    """
    TimSort (stable, O(n log n)), Python's built-in sorting algorithm.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.
        - Used by Python's built-in sorted() and .sort().

    Examples:
        >>> timsort([3, 1, 2])
        [1, 2, 3]
        >>> timsort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> timsort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        return sorted(items)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e