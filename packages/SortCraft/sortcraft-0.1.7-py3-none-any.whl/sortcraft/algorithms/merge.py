from __future__ import annotations
from typing import Iterable, List, Sequence, TypeVar, Protocol

class SupportsLT(Protocol):
    def __lt__(self, other: "SupportsLT", /) -> bool: ...

T = TypeVar("T", bound=SupportsLT)

def merge_sort(items: Sequence[T]) -> List[T]:
    """
    Stable, O(n log n) merge sort that returns a new sorted list.

    Args:
        items (Sequence[T]): A finite sequence of comparable items.

    Returns:
        List[T]: A new list containing the items in non-decreasing order.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If items is empty.

    Notes:
        - Time: O(n log n) average/worst.
        - Space: O(n) auxiliary.
        - Stable: Yes.

    Examples:
        >>> merge_sort([3, 1, 2])
        [1, 2, 3]
        >>> merge_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> merge_sort(['z', 'a', 'x'])
        ['a', 'x', 'z']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        _ = items[0] < items[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

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
        try:
            if b[j] < a[i]:  # maintain stability
                out.append(b[j]); j += 1
            else:
                out.append(a[i]); i += 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    if i < len(a): out.extend(a[i:])
    if j < len(b): out.extend(b[j:])
    return out