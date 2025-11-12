from typing import Sequence, List

def counting_sort(items: Sequence[int]) -> List[int]:
    """
    Counting sort for integers (stable, O(n + k)), returns a new sorted list.

    Args:
        items (Sequence[int]): Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence.
        ValueError: If elements are not non-negative integers.
        ValueError: If items is empty.

    Notes:
        - Time: O(n + k), where k is range of input.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers >= 0.

    Examples:
        >>> counting_sort([2, 5, 3, 0, 2, 3, 0, 3])
        [0, 0, 2, 2, 3, 3, 3, 5]
        >>> counting_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> counting_sort([2, -1, 3])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be non-negative integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for num in items:
        if not isinstance(num, int) or num < 0:
            raise ValueError("All elements must be non-negative integers.")

    max_val = max(items)
    counts = [0] * (max_val + 1)
    for num in items:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    return out