from typing import Sequence, TypeVar, List

T = TypeVar("T")

def odd_even_sort(items: Sequence[T]) -> List[T]:
    """
    Odd-Even sort (parity sort, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> odd_even_sort([4, 3, 2, 1])
        [1, 2, 3, 4]
        >>> odd_even_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> odd_even_sort(['c', 'b', 'a'])
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

    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            try:
                if arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        for i in range(1, n - 1, 2):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
    return arr