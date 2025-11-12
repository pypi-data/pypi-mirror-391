from typing import Sequence, TypeVar, List

T = TypeVar("T")

def cocktail_sort(items: Sequence[T]) -> List[T]:
    """
    Cocktail Shaker sort (stable, bidirectional bubble, O(n^2)), returns sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> cocktail_sort([4, 2, 3, 1])
        [1, 2, 3, 4]
    """
    arr = list(items)
    n = len(arr)
    swapped = True
    start, end = 0, n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        start += 1
    return arr