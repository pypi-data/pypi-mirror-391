Introduction
============

Parsim is a tool for working with parameterized simulation models.
The primary objective is to facilitate quality assurance of simulation projects.
The tool supports a scripted and automated workflow, where verified and validated simulation models
are parameterized, so that they can be altered/modified in well-defined ways and reused with minimal user invention.
All events are logged on several levels, to support traceability, project documentation and quality control.

Parsim provides basic functionality for generating studies based on common design-of experiments
(DOE) methods, for example using factorial designs, response surface methods or random sampling,
like Monte Carlo or Latin Hypercube.

Parsim can also be used as an interface to the `Dakota <https://dakota.sandia.gov>`_ library;
Dakota is run as a subprocess, generating cases from a Parsim model template.

How it works
============

Once a prototype simulation case has been developed, a corresponding simulation
*model template* is created by collecting all simulation input files, data
files and scripts into a *template directory*. The text files in a model
template can then be parameterized by replacing numerical values, or text
strings with macro names. Parsim uses the pyexpander macro processing library, which
supports embedding of arbitrarly complex Python code in the template files.
This can be used for advanced parameterization needs, for example to compute data
tables from functions, generate graphs for reports, generate content in loops or
conditionals, etc.

When a simulation case is created, the model template directory is recursively
replicated to create a *case directory*. Parsim operations can also be carried
out on a *study*, containing multiple cases. A study is a directory containing
multiple case directories.

You operate on your cases (either individually or on all cases of a study at once)
by executing scripts written to perform specific tasks, e.g.
meshing operations, starting a simulation, or post-processing of results.

Your simulation project lives in a Parsim *project directory*, which holds all
cases and studies of the project. The project directory holds Parsim
configuration settings and logs project events, like creation of cases and
studies, serious errors, change of configuration settings, etc.

Summary of features:

* Flexible and full-featured support for parameterization of text-based simulation models.
* Cases and parameter studies kept together in projects.
* Scripted workflow can be applied to individual cases as well as to large parameter studies.
* Logging and error handling, for traceability and project documentation.
* Python API can be conveniently used for post-processing and analysis, with input parameters
  and output available as pandas DataFrames.
* Built-in support for many common design-of-experiments (DOE) methods.
* Can be used as an interface to the Dakota library, for complex uncertainty quantification and optimization tasks.
* Based on Python.
* One simple workflow for any kind of simulation application.
* Platform independent: Works in both Linux, Windows and MacOS environments.
* Simple installation from public Python repositories (install with pip or conda).
* Available under open-source license (GNU Public License v. 3)


Installation
============

Parsim is available at both `PyPI, the Python Package Index <https://pypi.python.org/pypi>`_ and as a conda package
through the `conda-forge repository <https://conda-forge.org>`_, depending on which Python distribution and package
manager you use (``pip`` and ``conda``, respectively).

The Parsim installation requires and automatically installs the
Python library `pyexpander <http://pyexpander.sourceforge.net>`_,
which is used for macro and parameter expansion (parameterization of input files).
The DOE (Design of Experiments) functionality is provided by the pyDOE3, numpy and
scipy libraries. The pandas library is used, so that the Python API can
provide results and caselist data as pandas DataFrames.
If you want to use the `Dakota toolkit <https://dakota.sandia.gov/>`_, it is installed separately;
the ``dakota`` executable should be in your ``PATH``.

.. note::

    If you experience issues with the installation, it is recommended to first make a clean and fully
    functional installation of the NumPy, SciPy and pandas libraries. The best way to do this depends on
    which Python distribution you use. The `anaconda Python distribution <https://www.continuum.io/downloads>`_
    or miniconda with packages from conda-forge both work well on both Windows and Linux.


Installation from PyPI
----------------------

Use the package installer ``pip`` to install: ::

    pip install parsim


Installation with conda
-----------------------

Note that you need to select the ``conda-forge`` channel to find parsim with conda.

To install in your base environment: ::

    conda install -c conda-forge parsim

Alternatively, create a separate conda environment (here called ``psm-env``) for using parsim: ::

    conda create -n psm-env -c conda-forge parsim
    conda activate psm-env


Documentation
=============

The Parsim documentation is hosted at `ReadTheDocs <https://parsim.readthedocs.io>`_.

Author
======

Parsim was developed by `Ola Widlund <https://www.ri.se/en/ola-widlund>`_,
`RISE Research Institutes of Sweden <https://www.ri.se/en>`_, to
provide basic and generic functionality for uncertainty quantification
and quality assurance of parameterized simulation models.

Licensing
=========

Parsim is licensed under the GNU Public License, GPL, version 3 or later.
Copyright belongs to `RISE Research Institutes of Sweden AB <https://www.ri.se/en>`_.

Source code and reporting of issues
===================================

The source code is hosted at `GitLab.com <https://gitlab.com/olwi/psm>`_.
Here you can also report issues and suggest improvements.
