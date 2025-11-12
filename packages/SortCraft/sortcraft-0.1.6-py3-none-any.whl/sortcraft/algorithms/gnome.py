from typing import Sequence, TypeVar, List

T = TypeVar("T")

def gnome_sort(items: Sequence[T]) -> List[T]:
    """
    Gnome sort (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> gnome_sort([3, 2, 1])
        [1, 2, 3]
        >>> gnome_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> gnome_sort(['b', 'c', 'a'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] <= arr[0]  # Check if comparable
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    i = 0
    while i < len(arr):
        try:
            if i == 0 or arr[i - 1] <= arr[i]:
                i += 1
            else:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                i -= 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    return arr