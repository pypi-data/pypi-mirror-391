from typing import Sequence, TypeVar, List

T = TypeVar("T")

def selection_sort(items: Sequence[T]) -> List[T]:
    """
    Selection sort algorithm (unstable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> selection_sort([2, 1, 3])
        [1, 2, 3]
        >>> selection_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> selection_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            try:
                if arr[j] < arr[idx_min]:
                    idx_min = j
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
    return arr