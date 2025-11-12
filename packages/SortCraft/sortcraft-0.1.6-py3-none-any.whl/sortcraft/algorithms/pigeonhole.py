from typing import Sequence, List

def pigeonhole_sort(items: Sequence[int]) -> List[int]:
    """
    Pigeonhole sort (O(n + k)), for finite-range integers.

    Args:
        items (Sequence[int]): Sequence of integers (ideally small/finite range).

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not integers.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n + k), where k is the range of values.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers with small/known range.

    Examples:
        >>> pigeonhole_sort([8, 3, 2, 7, 4, 6, 8])
        [2, 3, 4, 6, 7, 8, 8]
        >>> pigeonhole_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> pigeonhole_sort(['a', 2, 3])
        Traceback (most recent call last):
            ...
        TypeError: All elements must be integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for x in items:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")

    mini, maxi = min(items), max(items)
    size = maxi - mini + 1
    holes = [0] * size
    for x in items:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    return out