from typing import Sequence, TypeVar, List

T = TypeVar("T")

def bitonic_sort(items: Sequence[T]) -> List[T]:
    """
    Bitonic sort (O(n log^2 n)), suitable for parallel hardware or powers of two.

    Args:
        items: Sequence of comparable items (length a power of two for full parallelization).

    Returns:
        List[T]: Sorted list.

    Notes:
        - Best for parallel architectures.
        - Time: O(n log^2 n).
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> bitonic_sort([5, 1, 3, 2])
        [1, 2, 3, 5]
    """
    arr = list(items)
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
                if (arr[i] > arr[i + k]) == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)
    _bitonic_sort(arr, 0, len(arr), True)
    return arr