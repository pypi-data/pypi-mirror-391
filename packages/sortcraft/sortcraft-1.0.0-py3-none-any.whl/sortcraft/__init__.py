"""
sortcraft: An educational and comprehensive collection of sorting algorithms.

Algorithms included:
    bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, heap_sort,
    counting_sort, radix_sort, bucket_sort, shell_sort, cocktail_sort, timsort, 
    gnome_sort, odd_even_sort, comb_sort, pigeonhole_sort, bitonic_sort, 
    pancake_sort, spaghetti_sort, stooge_sort, bogo_sort, cycle_sort, flash_sort

Linked list variants (all in-place/rewriting values):
    bubble_sort_singly, bubble_sort_doubly, bubble_sort_circular,
    selection_sort_singly, selection_sort_doubly, selection_sort_circular,
    ... # and so forth for all algorithms.
    
Usage:
    from sortcraft import merge_sort, merge_sort_singly, ...
"""

from .algorithms.bubble import bubble_sort, bubble_sort_circular, bubble_sort_doubly, bubble_sort_singly
from .algorithms.selection import selection_sort, selection_sort_circular, selection_sort_doubly, selection_sort_singly
from .algorithms.insertion import insertion_sort, insertion_sort_circular, insertion_sort_doubly, insertion_sort_singly
from .algorithms.merge import merge_sort, merge_sort_circular, merge_sort_doubly, merge_sort_singly
from .algorithms.quick import quick_sort, quick_sort_circular, quick_sort_doubly, quick_sort_singly
from .algorithms.heap import heap_sort, heap_sort_circular, heap_sort_doubly, heap_sort_singly
from .algorithms.counting import counting_sort, counting_sort_circular, counting_sort_doubly, counting_sort_singly
from .algorithms.radix import radix_sort, radix_sort_circular, radix_sort_doubly, radix_sort_singly
from .algorithms.bucket import bucket_sort, bucket_sort_circular, bucket_sort_doubly, bucket_sort_singly
from .algorithms.shell import shell_sort, shell_sort_circular, shell_sort_doubly, shell_sort_singly
from .algorithms.cocktail import cocktail_sort, cocktail_sort_circular, cocktail_sort_doubly, cocktail_sort_singly
from .algorithms.timsort import timsort, timsort_circular, timsort_doubly, timsort_singly
from .algorithms.gnome import gnome_sort, gnome_sort_circular, gnome_sort_doubly, gnome_sort_singly
from .algorithms.odd_even import odd_even_sort, odd_even_sort_circular, odd_even_sort_doubly, odd_even_sort_singly
from .algorithms.comb import comb_sort, comb_sort_circular, comb_sort_doubly, comb_sort_singly
from .algorithms.pigeonhole import pigeonhole_sort, pigeonhole_sort_circular, pigeonhole_sort_doubly, pigeonhole_sort_singly
from .algorithms.bitonic import bitonic_sort, bitonic_sort_circular, bitonic_sort_doubly, bitonic_sort_singly
from .algorithms.pancake import pancake_sort, pancake_sort_circular, pancake_sort_doubly, pancake_sort_singly
from .algorithms.stooge import stooge_sort, stooge_sort_circular, stooge_sort_doubly, stooge_sort_singly
from .algorithms.bogo import bogo_sort, bogo_sort_circular, bogo_sort_doubly, bogo_sort_singly
from .algorithms.cycle import cycle_sort, cycle_sort_circular, cycle_sort_doubly, cycle_sort_singly
from .algorithms.flash import flash_sort, flash_sort_circular, flash_sort_doubly, flash_sort_singly

__all__ = [
    "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort", "heap_sort",
    "counting_sort", "radix_sort", "bucket_sort", "shell_sort", "cocktail_sort", "timsort",
    "gnome_sort", "odd_even_sort", "comb_sort", "pigeonhole_sort", "bitonic_sort", "pancake_sort",
    "spaghetti_sort", "stooge_sort", "bogo_sort", "cycle_sort", "flash_sort",

    "bubble_sort_singly", "selection_sort_singly", "insertion_sort_singly",
    "merge_sort_singly", "quick_sort_singly", "heap_sort_singly",
    "counting_sort_singly", "radix_sort_singly", "bucket_sort_singly",
    "shell_sort_singly", "cocktail_sort_singly", "timsort_singly",
    "gnome_sort_singly", "odd_even_sort_singly", "comb_sort_singly",
    "pigeonhole_sort_singly", "bitonic_sort_singly", "pancake_sort_singly",
    "stooge_sort_singly", "bogo_sort_singly", "cycle_sort_singly",
    "flash_sort_singly",

    "bubble_sort_doubly", "selection_sort_doubly", "insertion_sort_doubly",
    "merge_sort_doubly", "quick_sort_doubly", "heap_sort_doubly",
    "counting_sort_doubly", "radix_sort_doubly", "bucket_sort_doubly",
    "shell_sort_doubly", "cocktail_sort_doubly", "timsort_doubly",
    "gnome_sort_doubly", "odd_even_sort_doubly", "comb_sort_doubly",
    "pigeonhole_sort_doubly", "bitonic_sort_doubly", "pancake_sort_doubly",
    "stooge_sort_doubly", "bogo_sort_doubly", "cycle_sort_doubly",
    "flash_sort_doubly",

    "bubble_sort_circular", "selection_sort_circular", "insertion_sort_circular",
    "merge_sort_circular", "quick_sort_circular", "heap_sort_circular",
    "counting_sort_circular", "radix_sort_circular", "bucket_sort_circular",
    "shell_sort_circular", "cocktail_sort_circular", "timsort_circular",
    "gnome_sort_circular", "odd_even_sort_circular", "comb_sort_circular",
    "pigeonhole_sort_circular", "bitonic_sort_circular", "pancake_sort_circular",
    "stooge_sort_circular", "bogo_sort_circular", "cycle_sort_circular",
    "flash_sort_circular",
]