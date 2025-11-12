from typing import Sequence, TypeVar, List

T = TypeVar("T")

def stooge_sort(items: Sequence[T]) -> List[T]:
    """
    Stooge sort (O(n^{2.7095})), famous as a highly impractical comparison sort.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(n)
        - Stable: Yes
        - Mostly used to illustrate pathological worst-cases.

    Examples:
        >>> stooge_sort([4, 2, 7, 1])
        [1, 2, 4, 7]
        >>> stooge_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> stooge_sort(['b', 'c', 'a'])
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

    def _stooge(arr, l, h):
        if l >= h:
            return
        try:
            if arr[l] > arr[h]:
                arr[l], arr[h] = arr[h], arr[l]
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
    return arr