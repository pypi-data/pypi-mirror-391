from typing import Sequence, TypeVar, List

T = TypeVar("T")

def cycle_sort(items: Sequence[T]) -> List[T]:
    """
    Cycle sort (in-place, O(n^2)), minimizes memory writes.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If the input sequence is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: No
        - Used where write operations are expensive.

    Examples:
        >>> cycle_sort([3, 2, 4, 1])
        [1, 2, 3, 4]
        >>> cycle_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> cycle_sort(['c', 'a', 'b'])
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

    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            try:
                if arr[i] < item:
                    pos += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                try:
                    if arr[i] < item:
                        pos += 1
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
    return arr