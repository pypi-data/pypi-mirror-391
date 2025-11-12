from typing import Sequence, TypeVar, List

T = TypeVar("T")

def insertion_sort(items: Sequence[T]) -> List[T]:
    """
    Insertion sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average, best O(n) when nearly sorted.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> insertion_sort([2, 1, 3])
        [1, 2, 3]
        >>> insertion_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> insertion_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            try:
                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[j + 1] = key
    return arr