from typing import Sequence, TypeVar, List

T = TypeVar("T")

def shell_sort(items: Sequence[T]) -> List[T]:
    """
    Shell sort (unstable, O(n log n) worst), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: Depends on gap sequence, O(n log n) to O(n^2).
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> shell_sort([5, 1, 3, 2, 9, 6])
        [1, 2, 3, 5, 6, 9]
        >>> shell_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> shell_sort(['c', 'a', 'b'])
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

    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap:
                try:
                    if arr[j - gap] > temp:
                        arr[j] = arr[j - gap]
                        j -= gap
                    else:
                        break
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            arr[j] = temp
        gap //= 2
    return arr