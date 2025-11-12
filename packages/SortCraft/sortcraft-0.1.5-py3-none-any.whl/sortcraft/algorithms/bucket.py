from typing import Sequence, List

def bucket_sort(items: Sequence[float], bucket_size: int = 5) -> List[float]:
    """
    Bucket sort for floats in [0, 1), returns a new sorted list.

    Args:
        items: Sequence of floats.
        bucket_size: Approx bucket granularity (default=5).

    Returns:
        List[float]: Sorted list.

    Notes:
        - Time: O(n + k) on uniform distributions.
        - Space: O(n + k).
        - Stable: Yes if underlying sort is stable.
        - Only suitable for floats in [0, 1).

    Examples:
        >>> bucket_sort([0.93, 0.14, 0.52, 0.4, 0.75])
        [0.14, 0.4, 0.52, 0.75, 0.93]
    """
    if not items:
        return []
    buckets = [[] for _ in range(bucket_size)]
    for x in items:
        idx = int(x * bucket_size)
        buckets[min(idx, bucket_size-1)].append(x)
    result = []
    for b in buckets:
        result.extend(sorted(b))  # stable built-in
    return result