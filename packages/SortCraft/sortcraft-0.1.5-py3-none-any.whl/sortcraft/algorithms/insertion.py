from typing import Sequence, TypeVar, List

T = TypeVar("T")

def insertion_sort(items: Sequence[T]) -> List[T]:
    """
    Insertion sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Notes:
        - Time: O(n^2) worst/average, best O(n) when nearly sorted.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> insertion_sort([2, 1, 3])
        [1, 2, 3]
    """
    arr = list(items)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
