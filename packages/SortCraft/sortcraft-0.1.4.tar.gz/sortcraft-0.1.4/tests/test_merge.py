import random
from sortcraft import merge_sort

def test_small_examples():
    assert merge_sort([3, 1, 2]) == [1, 2, 3]
    assert merge_sort([]) == []
    assert merge_sort([1]) == [1]

def test_random_against_builtin():
    for _ in range(200):
        arr = [random.randint(-100, 100) for _ in range(50)]
        assert merge_sort(arr) == sorted(arr)