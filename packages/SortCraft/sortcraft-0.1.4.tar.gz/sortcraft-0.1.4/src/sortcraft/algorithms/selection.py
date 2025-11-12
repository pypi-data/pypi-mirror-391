from typing import Sequence, TypeVar, List

T = TypeVar("T")

def selection_sort(items: Sequence[T]) -> List[T]:
    """
    Selection sort algorithm (unstable, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> selection_sort([2, 1, 3])
        [1, 2, 3]
    """
    arr = list(items)
    n = len(arr)
    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            if arr[j] < arr[idx_min]:
                idx_min = j
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
    return arr
