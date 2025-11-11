Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[2.2.0] - 2025-11-10
--------------------

Now uses pyDOE3, rather than pyDOE2, due to the use of deprecated libraries in the pyDOE2 code base.

This release is verified to work correctly with Python versions from 3.8 to 3.13, 
pyexpander versions from 1.9.x to 2.2.1.

Fixed
..... 

* Avoided use of pandas.DataFrame.append method, as this is deprecated in recent pandas versions.
* Fixed issue with recent pyexpander versions (>=2.0). Now using keyword arguments in call to 
  pyexpander.lib.expandFile. Works with both new and old pyexpander versions.
* Use raw strings for regexp patterns, to avoid problems with escape sequences 
  in recent versions of Python.
* Parsim object info() methods had problems with info string escape sequences in recent versions of Python. Now corrected. 
* Fixed crash when saving parsim objects to disk: Starting with Python 3.10, the __getstate__ method now exists also for many "state-less" 
  objects (like lists) and returns "None". This is now handled correctly.
* Now using pyDOE3 instead of pyDOE2, as pyDOE2 still uses the "imp" module, which was deprecated and removed in Python 3.12.
* Fixed minor documentation issues.



[2.1.0] - 2020-08-03
--------------------

Added
.....

* Special parameters with parsim-related case information are available for macro expansion on case creation.
  They are also available as environent variables of the subprocesses started with the ``psm run`` command.


[2.0.0] - 2019-09-27
--------------------

Added
.....

* Implemented DOE scheme `gsd` (Generalized Subset Design), as available in pyDOE2 package.
  Allows reduced factorial designs with more than two levels.
* With DOE scheme `fracfact`, the user can now define the reduced design either by a generator
  expression (option "gen"), or by the design resolution (option "res").
* Property-based getter functions in `Case` and `Study` classes now provide caselist, results and
  parameter info as pandas `DataFrame` or `Series` objects.
* `Study.collect()` method now aggregates all collected results in a file "study.results" in the
  study directory. This file includes also cases with missing data (marked as "NaN", pandas-style).
* `pyDOE2`, `numpy`, `scipy` and pandas are now mandatory dependencies.
* Constructor of `Case` class now handles colon-separated format <study>:<case> for cases inside studies.
  This simplifies use of the parsim Python API for working with results.
* Examples of how to use the Python API for post-processing and data analysis.

Removed
.......

* Support for Python 2 has been removed!
* Config option `paramlist_upper_names` has been removed (controlled optional automatic conversion
  of all parameter names to uppercase).

Changed
.......

* API changes in ParsimObjects (incl. subclasses `Project`, `Study` and `Case`), especially in
  constructors (`__init__`) and `create()` method. These changes makes the CLI command implementations
  shorter and easier to understand. Better checking of sane `name` and `path` arguments to constructor.


[1.0.0] - 2018-12-19
--------------------

Changed
.......

* Use `pyDOE2 package <https://github.com/clicumu/pyDOE2>`_, instead of pyDOE.

Fixed
.....

* Now works with Python 3 (and Python 2.7, as before).
* Fixed problems with parsing of DOE command-line arguments.

[0.7.0] - 2018-07-26
--------------------
