from typing import Sequence, TypeVar, List

T = TypeVar("T")

def bubble_sort(items: Sequence[T]) -> List[T]:
    """
    Bubble sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or its elements are not comparable.
        ValueError: If the input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> bubble_sort([2, 1, 3])
        [1, 2, 3]
        >>> bubble_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> bubble_sort(["b", "a", "c"])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        for j in range(n - 1 - i):
            try:
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
    return arr