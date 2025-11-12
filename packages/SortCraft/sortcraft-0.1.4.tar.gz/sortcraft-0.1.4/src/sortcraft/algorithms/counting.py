from typing import Sequence, List

def counting_sort(items: Sequence[int]) -> List[int]:
    """
    Counting sort for integers (stable, O(n + k)), returns a new sorted list.

    Args:
        items: Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Notes:
        - Time: O(n + k), where k is range of input.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers >= 0.

    Examples:
        >>> counting_sort([2, 5, 3, 0, 2, 3, 0, 3])
        [0, 0, 2, 2, 3, 3, 3, 5]
    """
    if not items:
        return []
    max_val = max(items)
    counts = [0] * (max_val + 1)
    for num in items:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    return out