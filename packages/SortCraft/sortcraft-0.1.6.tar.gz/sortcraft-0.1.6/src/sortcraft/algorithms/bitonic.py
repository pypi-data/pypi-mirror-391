from typing import Sequence, TypeVar, List

T = TypeVar("T")

def bitonic_sort(items: Sequence[T]) -> List[T]:
    """
    Bitonic sort (O(n log^2 n)), suitable for parallel hardware or powers of two.

    Args:
        items (Sequence[T]): Sequence of comparable items. For optimal parallelization,
            length should be a power of two. Non-power-of-two lengths will still work,
            but performance characteristics may differ.

    Returns:
        List[T]: Sorted list of items.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If the sequence is empty.

    Notes:
        - Best for parallel architectures.
        - Time: O(n log^2 n).
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> bitonic_sort([5, 1, 3, 2])
        [1, 2, 3, 5]

        >>> bitonic_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.

        >>> bitonic_sort([2, 2, 2, 2])
        [2, 2, 2, 2]
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        arr = list(items)
    except Exception as e:
        raise TypeError("Could not convert input to list.") from e

    def _bitonic_sort(arr: List[T], low: int, cnt: int, up: bool) -> None:
        if cnt > 1:
            k = cnt // 2
            _bitonic_sort(arr, low, k, True)
            _bitonic_sort(arr, low + k, k, False)
            _bitonic_merge(arr, low, cnt, up)

    def _bitonic_merge(arr: List[T], low: int, cnt: int, up: bool) -> None:
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                try:
                    comparison = arr[i] > arr[i + k]
                except Exception as e:
                    raise TypeError("Elements must be comparable.") from e
                if comparison == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)

    _bitonic_sort(arr, 0, len(arr), True)
    return arr