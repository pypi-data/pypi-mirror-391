from typing import Sequence, TypeVar, List

T = TypeVar("T")

def gnome_sort(items: Sequence[T]) -> List[T]:
    """
    Gnome sort (stable, O(n^2)), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> gnome_sort([3, 2, 1])
        [1, 2, 3]
    """
    arr = list(items)
    i = 0
    while i < len(arr):
        if i == 0 or arr[i - 1] <= arr[i]:
            i += 1
        else:
            arr[i], arr[i - 1] = arr[i - 1], arr[i]
            i -= 1
    return arr