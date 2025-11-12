from typing import Sequence, TypeVar, List

T = TypeVar("T")

def comb_sort(items: Sequence[T]) -> List[T]:
    """
    Comb sort (unstable, better than bubble, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence, or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2) but faster than bubble in practice.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> comb_sort([9, 4, 1, 5, 3])
        [1, 3, 4, 5, 9]
        >>> comb_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> comb_sort(['e', 'd', 'c'])
        ['c', 'd', 'e']
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

    gap = n
    shrink = 1.3
    sorted_ = False
    while not sorted_:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_ = True
        i = 0
        while i + gap < n:
            try:
                if arr[i] > arr[i + gap]:
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
            i += 1
    return arr