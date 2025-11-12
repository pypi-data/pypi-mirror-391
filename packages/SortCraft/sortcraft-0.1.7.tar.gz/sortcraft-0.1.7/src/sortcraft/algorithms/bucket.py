from typing import Sequence, List

def bucket_sort(items: Sequence[float], bucket_size: int = 5) -> List[float]:
    """
    Bucket sort for floats in [0, 1), returns a new sorted list.

    Args:
        items (Sequence[float]): Sequence of floats. Values must be in [0, 1).
        bucket_size (int, optional): Approximate bucket granularity (default=5).

    Returns:
        List[float]: Sorted list.

    Raises:
        TypeError: If items is not a sequence, or bucket_size is not an int.
        ValueError: If any element is not a float in [0, 1).
        ValueError: If bucket_size is not a positive integer.

    Notes:
        - Time: O(n + k) on uniform distributions.
        - Space: O(n + k).
        - Stable: Yes if underlying sort is stable.
        - Only suitable for floats in [0, 1).

    Examples:
        >>> bucket_sort([0.93, 0.14, 0.52, 0.4, 0.75])
        [0.14, 0.4, 0.52, 0.75, 0.93]
        >>> bucket_sort([])
        []
        >>> bucket_sort([0.7, 1.1])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be floats in [0, 1).
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input items must be a sequence.")
    if not isinstance(bucket_size, int) or bucket_size < 1:
        raise ValueError("bucket_size must be a positive integer.")

    if not items:
        return []

    for x in items:
        if not isinstance(x, (float, int)):
            raise TypeError("All elements must be of float type.")
        if not (0 <= float(x) < 1):
            raise ValueError("All elements must be floats in [0, 1).")

    buckets = [[] for _ in range(bucket_size)]
    for x in items:
        idx = int(float(x) * bucket_size)
        buckets[min(idx, bucket_size - 1)].append(float(x))
    result = []
    for b in buckets:
        result.extend(sorted(b))
    return result