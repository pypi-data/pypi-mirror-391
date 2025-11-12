from typing import Sequence, List

def flash_sort(items: Sequence[int]) -> List[int]:
    """
    Flash sort (O(n) to O(n^2)), distribution-based, very fast for certain data.

    Args:
        items (Sequence[int]): Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence.
        ValueError: If any element is not a non-negative integer.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n) best, O(n^2) worst
        - Space: O(n)
        - Stable: No
        - Used for large, uniformly distributed integer arrays.

    Examples:
        >>> flash_sort([6, 4, 1, 7, 9, 1, 3])
        [1, 1, 3, 4, 6, 7, 9]
        >>> flash_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> flash_sort([7, -2, 6])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be non-negative integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for x in items:
        if not isinstance(x, int) or x < 0:
            raise ValueError("All elements must be non-negative integers.")

    arr = list(items)
    n = len(arr)
    if n == 0:
        return []
    min_val, max_val = min(arr), max(arr)
    if min_val == max_val:
        return arr
    m = int(0.45 * n) + 1
    counts = [0] * m
    for x in arr:
        idx = int((m - 1) * (x - min_val) / (max_val - min_val))
        counts[idx] += 1
    for i in range(1, m):
        counts[i] += counts[i - 1]
    output = [0] * n
    for x in reversed(arr):
        idx = int((m - 1) * (x - min_val) / (max_val - min_val))
        counts[idx] -= 1
        output[counts[idx]] = x
    return output