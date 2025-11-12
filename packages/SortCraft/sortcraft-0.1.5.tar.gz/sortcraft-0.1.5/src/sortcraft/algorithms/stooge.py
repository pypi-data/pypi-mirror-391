from typing import Sequence, TypeVar, List

T = TypeVar("T")

def stooge_sort(items: Sequence[T]) -> List[T]:
    """
    Stooge sort (O(n^{2.7095})), famous as a highly impractical comparison sort.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(n)
        - Stable: Yes
        - Mostly used to illustrate pathological worst-cases.

    Examples:
        >>> stooge_sort([4, 2, 7, 1])
        [1, 2, 4, 7]
    """
    arr = list(items)
    def _stooge(arr, l, h):
        if l >= h:
            return
        if arr[l] > arr[h]:
            arr[l], arr[h] = arr[h], arr[l]
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
    return arr
