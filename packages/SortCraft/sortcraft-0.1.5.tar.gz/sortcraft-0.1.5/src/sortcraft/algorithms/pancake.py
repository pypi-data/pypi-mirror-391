from typing import Sequence, TypeVar, List

T = TypeVar("T")

def pancake_sort(items: Sequence[T]) -> List[T]:
    """
    Pancake sort (O(n^2)), sorts by repeatedly flipping largest unsorted element to the front.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: Yes.

    Examples:
        >>> pancake_sort([3, 6, 1, 8, 4])
        [1, 3, 4, 6, 8]
    """
    arr = list(items)
    n = len(arr)
    for curr_size in range(n, 1, -1):
        mi = max(range(curr_size), key=lambda x: arr[x])
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
    return arr
