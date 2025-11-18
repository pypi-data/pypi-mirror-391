# Release Notes

## v1.2.0 (2025-11-14)

* Important review of the code and package structure.
    - Comparing objects of the included classes with other objects that are not of their own class (or integers, in the case of `BabN` class) now raises `NotImplementedError`.
    - Classes are now hashable.
    - Method `__int__` added to all clases. Methods `__len__` and `__round__` added to `BabN` class.
    - New simple utility to print sexagesimal multiplication tables.
    - The package and repository now have a more standard structure.
    - Some test files for `pytest` added.
    - Obsolete `mesolib.py` and old test files removed.

## v1.1.1 (2025-11-05).

* Some bug fixes and other minor improvements.

## v1.1.0 (2025-09-23).

* Documentation prepared using [Sphinx](https://www.sphinx-doc.org/en/master/index.html) now resides in  [https://mesomath.readthedocs.io/index.html](https://mesomath.readthedocs.io/index.html). It includes the tutorials.
* Bug fix: `mtlookup.py` now admit integer values e.g.: `$ mtlookup -t L 123`
* Code reformated with `Black`. [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
* Added method `.metval()` to `_MesoM` class.
* Added basic support for actual or academic unit names in methods `.__init__()`, `.scheme()` and `.prtf()` so that strings of type: `(1 dis) 1/3 kuš3 (4 dis) šu-si` can be obtained in output and used in input.
* `metrotable` and `mtlookup` utilities adapted to use *academic* names.
* Updated tutorials moved to [documentation](https://mesomath.readthedocs.io/index.html).
* Restructured and cleared repository.

## v1.0.0 Initial release 2025-09-16.

* The intended functionality of the package is complete and testing (intensive but not exhaustive) is satisfactory.