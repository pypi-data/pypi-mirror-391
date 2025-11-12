from typing import Sequence, TypeVar, List

T = TypeVar("T")

def shell_sort(items: Sequence[T]) -> List[T]:
    """
    Shell sort (unstable, O(n log n) worst), returns a new sorted list.

    Args:
        items: Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Notes:
        - Time: Depends on gap sequence, O(n log n) to O(n^2).
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> shell_sort([5, 1, 3, 2, 9, 6])
        [1, 2, 3, 5, 6, 9]
    """
    arr = list(items)
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr