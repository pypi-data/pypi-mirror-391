from __future__ import annotations
from typing import List, Sequence, TypeVar
T = TypeVar("T")

def quick_sort(items: Sequence[T]) -> List[T]:
    """
    Quick sort (Lomuto partition), returns a new sorted list.

    Args:
        items: A finite sequence of comparable items.

    Returns:
        A new list in non-decreasing order.

    Notes:
        - Time: O(n log n) average, O(n^2) worst (already-sorted + bad pivot).
        - Space: O(log n) average recursion depth.
        - Stable: No.
    """
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
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i