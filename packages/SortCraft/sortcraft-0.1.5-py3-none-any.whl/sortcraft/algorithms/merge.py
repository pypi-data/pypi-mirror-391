from __future__ import annotations
from typing import Iterable, List, Sequence, TypeVar, Protocol

class SupportsLT(Protocol):
    def __lt__(self, other: "SupportsLT", /) -> bool: ...

T = TypeVar("T", bound=SupportsLT)

def merge_sort(items: Sequence[T]) -> List[T]:
    """
    Stable, O(n log n) merge sort that returns a new sorted list.

    Args:
        items: A finite sequence of comparable items.

    Returns:
        A new list containing the items in non-decreasing order.

    Notes:
        - Time: O(n log n) average/worst.
        - Space: O(n) auxiliary.
        - Stable: Yes.

    Examples:
        >>> merge_sort([3, 1, 2])
        [1, 2, 3]
    """
    n = len(items)
    if n <= 1:
        return list(items)
    mid = n // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return _merge(left, right)

def _merge(a: List[T], b: List[T]) -> List[T]:
    i = j = 0
    out: List[T] = []
    while i < len(a) and j < len(b):
        if a[j] < b[i]:  # maintain stability
            out.append(b[j]); j += 1
        else:
            out.append(a[i]); i += 1
    if i < len(a): out.extend(a[i:])
    if j < len(b): out.extend(b[j:])
    return out