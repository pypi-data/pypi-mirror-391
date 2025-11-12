from typing import Sequence, List

def radix_sort(items: Sequence[int]) -> List[int]:
    """
    Radix sort (stable, O(nk)), returns a new sorted list.

    Args:
        items: Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Notes:
        - Time: O(nk), k is number of digits.
        - Space: O(n + k).
        - Stable: Yes.
        - Works for non-negative integers only.

    Examples:
        >>> radix_sort([170, 45, 75, 90, 802, 24, 2, 66])
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    arr = list(items)
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = _counting_sort_exp(arr, exp)
        exp *= 10
    return arr

def _counting_sort_exp(items: List[int], exp: int) -> List[int]:
    n = len(items)
    output = [0] * n
    count = [0] * 10
    for num in items:
        index = (num // exp) % 10
        count[index] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for num in reversed(items):
        index = (num // exp) % 10
        output[count[index] - 1] = num
        count[index] -= 1
    return output