from typing import Sequence, TypeVar, List

T = TypeVar("T")

def odd_even_sort(items: Sequence[T]) -> List[T]:
    """
    Odd-Even sort (parity sort, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> odd_even_sort([4, 3, 2, 1])
        [1, 2, 3, 4]
    """
    arr = list(items)
    n = len(arr)
    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            if arr[i - 1] > arr[i]:
                arr[i - 1], arr[i] = arr[i], arr[i - 1]
                sorted_ = False
        for i in range(1, n - 1, 2):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                sorted_ = False
    return arr