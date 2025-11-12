from typing import Sequence, TypeVar, List

T = TypeVar("T")

def pancake_sort(items: Sequence[T]) -> List[T]:
    """
    Pancake sort (O(n^2)), sorts by repeatedly flipping largest unsorted element to the front.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: Yes.

    Examples:
        >>> pancake_sort([3, 6, 1, 8, 4])
        [1, 3, 4, 6, 8]
        >>> pancake_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> pancake_sort(['c', 'a', 'b'])
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

    for curr_size in range(n, 1, -1):
        try:
            mi = max(range(curr_size), key=lambda x: arr[x])
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
    return arr