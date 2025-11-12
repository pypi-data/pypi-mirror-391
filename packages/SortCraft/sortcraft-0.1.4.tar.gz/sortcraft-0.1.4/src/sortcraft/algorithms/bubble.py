from typing import Sequence, TypeVar, List

T = TypeVar("T")

def bubble_sort(items: Sequence[T]) -> List[T]:
    """
    Bubble sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> bubble_sort([2, 1, 3])
        [1, 2, 3]
    """
    arr = list(items)
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr