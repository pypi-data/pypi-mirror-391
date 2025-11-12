from typing import Sequence, TypeVar, List

T = TypeVar("T")

def heap_sort(items: Sequence[T]) -> List[T]:
    """
    Heap sort (unstable, O(n log n)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> heap_sort([2, 1, 3])
        [1, 2, 3]
        >>> heap_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> heap_sort(['c', 'b', 'a'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    _heapify(arr)
    end = len(arr) - 1
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]
        end -= 1
        _sift_down(arr, 0, end)
    return arr

def _heapify(arr: List[T]) -> None:
    n = len(arr)
    for i in reversed(range(n // 2)):
        _sift_down(arr, i, n - 1)

def _sift_down(arr: List[T], start: int, end: int) -> None:
    root = start
    while True:
        child = 2 * root + 1
        if child > end:
            break
        swap = root
        try:
            if arr[swap] < arr[child]:
                swap = child
            if child + 1 <= end and arr[swap] < arr[child + 1]:
                swap = child + 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if swap == root:
            return
        arr[root], arr[swap] = arr[swap], arr[root]
        root = swap