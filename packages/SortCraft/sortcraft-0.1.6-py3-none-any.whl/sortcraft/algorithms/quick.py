from __future__ import annotations
from typing import List, Sequence, TypeVar

T = TypeVar("T")

def quick_sort(items: Sequence[T]) -> List[T]:
    """
    Quick sort (Lomuto partition), returns a new sorted list.

    Args:
        items (Sequence[T]): A finite sequence of comparable items.

    Returns:
        List[T]: A new list in non-decreasing order.

    Raises:
        TypeError: If items is not a sequence or its elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) average, O(n^2) worst (already-sorted + bad pivot).
        - Space: O(log n) average recursion depth.
        - Stable: No.

    Examples:
        >>> quick_sort([3, 2, 1])
        [1, 2, 3]
        >>> quick_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> quick_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        _ = items[0] <= items[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    arr = list(items)
    _qs(arr, 0, len(arr) - 1)
    return arr

def _qs(a: List[T], lo: int, hi: int) -> None:
    if lo >= hi:
        return
    p = _partition(a, lo, hi)
    _qs(a, lo, p - 1)
    _qs(a, p + 1, hi)

def _partition(a: List[T], lo: int, hi: int) -> int:
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        try:
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    a[i], a[hi] = a[hi], a[i]
    return i