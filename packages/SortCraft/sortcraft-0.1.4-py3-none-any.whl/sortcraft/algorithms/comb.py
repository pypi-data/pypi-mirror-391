from typing import Sequence, TypeVar, List

T = TypeVar("T")

def comb_sort(items: Sequence[T]) -> List[T]:
    """
    Comb sort (unstable, better than bubble, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2) but faster than bubble in practice.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> comb_sort([9, 4, 1, 5, 3])
        [1, 3, 4, 5, 9]
    """
    arr = list(items)
    n = len(arr)
    gap = n
    shrink = 1.3
    sorted_ = False
    while not sorted_:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_ = True
        i = 0
        while i + gap < n:
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False
            i += 1
    return arr