from typing import Sequence, List

def pigeonhole_sort(items: Sequence[int]) -> List[int]:
    """
    Pigeonhole sort (O(n + k)), for finite-range integers.

    Args:
        items: Sequence of integers.

    Returns:
        List[int]: Sorted list.

    Notes:
        - Time: O(n + k), where k is the range of values.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers with small/known range.

    Examples:
        >>> pigeonhole_sort([8, 3, 2, 7, 4, 6, 8])
        [2, 3, 4, 6, 7, 8, 8]
    """
    if not items:
        return []
    mini, maxi = min(items), max(items)
    size = maxi - mini + 1
    holes = [0] * size
    for x in items:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    return out