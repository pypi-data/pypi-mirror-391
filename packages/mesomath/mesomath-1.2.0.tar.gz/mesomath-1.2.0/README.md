![mesomath](docs/source/_static/mesomath.png) 


## Overview

This project aims to bring:

*  the arithmetic of natural sexagesimal numbers, mainly in their “floating” aspect (i.e., by removing all possible trailing sexagesimal zeros from the right), as performed by the Babylonian scribes and their apprentices in ancient times. 

* the arithmetic of physical quantities, length, surface, etc. described using the metrology of the Old Babylonian Period.

to `Python3` programming and to the `Python3` command line as an interactive calculator.

It has been inspired by the arithmetic and metrological parts of [MesoCalc](https://github.com/BapMel/mesocalc) by Baptiste Mélès. 

The package includes:

* the `mesomath` module containing three main submodules:

    *  `babn.py`: Containing the class `BabN` for *Babylonian* (sexagesimal) *numbers*.
    *  `npvs.py`: Containing *metrological* classes for measurements of distance, area, volume, capacity, weight,...
    *  `hamming.py`: For generating lists of *regular numbers*, as well as the [`SQLite3`](https://www.sqlite.org/) database of these used by the `BabN` class.


* four application submodules:

    * `babcalc.py` implementing the interactive *Babylonian calculator* `babcalc`.
    * `metrotable.py`: implementation of the metrological table printing application `metrotable`.
    * `mtlookup.py`: implementation of the metrological table search application `mtlookup`.
    * `multable.py`: implementation of the sexagesimal multiplication table printing utility `bmultab`.

* Test files for `pytest` in the `test` subdirectory.
* [`Sphinx`](https://www.sphinx-doc.org/en/master/) source files for the documentation in the `docs` subdirectory, including tutorials for the four applications: `babcalc`, `metrotable`, `mtlookup` and `bmultab`.


## Download

From the [GitHub repository](https://github.com/jccsvq/mesomath). Read below about the [installation](installation).

## Documentation

Documentation for this package is in [Read the Docs](https://mesomath.readthedocs.io/index.html).

## Install

For instance:

    $ pip install mesomath

to install from [pypi.org](https://pypi.org/). Read the [documentation](https://mesomath.readthedocs.io/install.html).

## Dependencies

`mesomath` only uses  standard Python modules: `math`, `itertools`, `argparse`, `os`, `re`, `types`, `typing` and `sqlite3`. 

The dependencies expressed in `requirements.txt` are for testing and documentation building.

Tested with Python 3.11.2 under Debian GNU/Linux 12 (bookworm) in x86_64 and aarch64 (raspberrypi 5).

##   `babn.py`

This is the main module defining the `BabN` class for representing sexagesimal natural numbers. You can perform mathematical operations on objects of the `BabN` class using the operators +, -, *, **, /, and //, and combine them using parentheses, both in a program and interactively on the Python command line. It also allows you to obtain their reciprocals in the case of regular numbers, their approximate inverses in the general case, approximate square and cube floating roots and obtain divisors and lists of "nearest" regular numbers. See the `test-babn.py` script.

### Note:

*  Operator `/` return the approximate floating division of `a/b` for any pair of numbers.
*  Operator `//` is for the "Babylonian Division" of `a` by `b`, i.e. `a//b` returns `a` times the reciprocal of `b`, which requires `b` to be regular.

###  Use as an interactive calculator

Once `mesomath` is installed, simply run:

    $ babcalc

Consult the [tutorial](https://mesomath.readthedocs.io/tutorial.html)!

## `hamming.py`

Regular or Hamming numbers are numbers of the form:

    H = 2^i * 3^j × 5^k
    
    where  i, j, k ≥ 0 

This module is used to obtain lists of such numbers and ultimately build a SQLite3 database of them up to 20 sexagesimal digits. This database is used by BabN to search for regular numbers close to a given one. See the scripts: `createDB.py` and `test-hamming.py`.

## `npvs.py`

This module defines the generic class `Npvs` for handling measurements in various units within a system. It is built using length measurements in the imperial system of units, from inches to leagues, as an example. This class is inherited by the `_MesoM` class which adapts it to Mesopotamian metrological use. The `_MesoM` class, in turn, is inherited by:

*  class `BsyG`: Babylonian counting System G (iku ese bur bur_u sar sar_u sar_gal)
*  class `BsyS`: Babylonian counting  System S (dis u ges gesu sar sar_u sar_gal)
*  class `MesoM`: To represent physical quantities, inherited by:
    *  class `Blen`: Babylonian length system (susi kus ninda us danna)
    *  class `Bsur`: Babylonian surface system (se gin sar gan)
    *  class `Bvol`: Babylonian volume system  (se gin sar gan)
    *  class `Bcap`: Babylonian capacity system  (se gin sila ban bariga gur)
    *  class `Bwei`: Babylonian weight system (se gin mana gu)
    *  class `Bbri`: Babylonian brick counting system (se gin sar gan)

Please, read the [tutorial](https://mesomath.readthedocs.io/tutorial.html) to see how to use all these classes.


