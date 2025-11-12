from typing import Sequence, TypeVar, List

T = TypeVar("T")

def cycle_sort(items: Sequence[T]) -> List[T]:
    """
    Cycle sort (in-place, O(n^2)), minimizes memory writes.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: No
        - Used where write operations are expensive.

    Examples:
        >>> cycle_sort([3, 2, 4, 1])
        [1, 2, 3, 4]
    """
    arr = list(items)
    n = len(arr)
    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            if arr[i] < item:
                pos += 1
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                if arr[i] < item:
                    pos += 1
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
    return arr
