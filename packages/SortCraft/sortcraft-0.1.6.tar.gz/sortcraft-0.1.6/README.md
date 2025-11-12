<p align="center">
    <img src="https://github.com/arijitkroy/sortcraft/blob/main/sortcraft.png?raw=true" alt="sortcraft logo" width="480">
</p>

![PyPI - Version](https://img.shields.io/pypi/v/sortcraft?label=Version)
![PyPI - Downloads](https://img.shields.io/pypi/dw/sortcraft?label=Downloads)
![PyPI - License](https://img.shields.io/pypi/l/sortcraftlabel=License)

SortCraft is a comprehensive Python package providing an extensive collection of sorting algorithms suitable for educational, research, and benchmarking purposes. All implementations are type-annotated, documented for clarity, and exposed through a clean flat API for easy import and exploration.

Features
--------
- More than twenty sorting algorithms, including classical, integer/distribution, advanced, parallel, and theoretical types.
- All functions have PEP 484 type annotations and rich, standardized docstrings suitable for IDE/hover documentation and Sphinx autodoc.
- Simple import model: `from sortcraft import merge_sort, quick_sort, cycle_sort, ...`.
- Designed for reliability, readability, and educational use cases as well as algorithmic experimentation.

Installation
------------
Install the latest release from PyPI:

    pip install sortcraft
    
Quick Usage
-----------

    from sortcraft import merge_sort, heap_sort
    data = [5, 2, 9, 1]
    sorted_data = merge_sort(data)  # [1, 2, 5, 9]

Included Algorithms
-------------------

- Classical comparison sorts: bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, heap_sort
- Counting/distribution sorts: counting_sort, radix_sort, pigeonhole_sort, flash_sort, bucket_sort
- Advanced or hybrid: shell_sort, comb_sort, cocktail_sort, timsort, bitonic_sort, cycle_sort
- Educational or theoretical: pancake_sort, gnome_sort, stooge_sort, bogo_sort, odd_even_sort

All functions require a sequence of comparable elements and return a new sorted list.

Type Annotations and Docstring Standards
----------------------------------------
- All user-facing APIs are type-annotated (PEP 484/561 compliant via the included py.typed marker).
- Docstrings follow the Google style, suitable for Sphinx autodoc and IDE hover documentation.
- Each algorithm documents its stability, complexity, and typical usage.

Version Logs:
------------
- `0.1.3`: Added 22 different types of sorting algorithms
- `0.1.4`: Modified logo for the package
- `0.1.5`: Added badges in README.md
- `0.1.6`: Added error handling in every algorithms

License
-------
SortCraft is licensed under the MIT License. See the LICENSE file for details.

Contributing
------------
Contributions by way of issue reports, algorithm additions, or improvements to documentation are welcome. Please open an issue or submit a pull request on GitHub.