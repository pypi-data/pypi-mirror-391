"""
sortcraft: An educational and comprehensive collection of sorting algorithms.

Algorithms included:
    bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, heap_sort,
    counting_sort, radix_sort, bucket_sort, shell_sort, cocktail_sort, timsort, 
    gnome_sort, odd_even_sort, comb_sort, pigeonhole_sort, bitonic_sort, 
    pancake_sort, spaghetti_sort, stooge_sort, bogo_sort, cycle_sort, flash_sort

Usage:
    from sortcraft import merge_sort, heap_sort, bogo_sort, ...
"""

from .algorithms.bubble import bubble_sort
from .algorithms.selection import selection_sort
from .algorithms.insertion import insertion_sort
from .algorithms.merge import merge_sort
from .algorithms.quick import quick_sort
from .algorithms.heap import heap_sort
from .algorithms.counting import counting_sort
from .algorithms.radix import radix_sort
from .algorithms.bucket import bucket_sort
from .algorithms.shell import shell_sort
from .algorithms.cocktail import cocktail_sort
from .algorithms.timsort import timsort
from .algorithms.gnome import gnome_sort
from .algorithms.odd_even import odd_even_sort
from .algorithms.comb import comb_sort
from .algorithms.pigeonhole import pigeonhole_sort
from .algorithms.bitonic import bitonic_sort
from .algorithms.pancake import pancake_sort
from .algorithms.stooge import stooge_sort
from .algorithms.bogo import bogo_sort
from .algorithms.cycle import cycle_sort
from .algorithms.flash import flash_sort

__all__ = [
    # Classic sorts
    "bubble_sort",
    "selection_sort",
    "insertion_sort",
    "merge_sort",
    "quick_sort",
    "heap_sort",
    # Integer/distributional sorts
    "counting_sort",
    "radix_sort",
    "bucket_sort",
    "pigeonhole_sort",
    # Optimized/hybrid/real-world sorts
    "shell_sort",
    "cocktail_sort",
    "timsort",
    # Quirky, educational, rare, and fun sorts
    "gnome_sort",
    "odd_even_sort",
    "comb_sort",
    "bitonic_sort",
    "pancake_sort",
    "stooge_sort",
    "bogo_sort",
    "cycle_sort",
    "flash_sort",
]