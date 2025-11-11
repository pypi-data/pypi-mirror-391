Getting started
===============

Parsim is a tool for working with parameterized simulation models.
The primary objective is to facilitate quality assurance of simulation projects.
The tool supports a scripted and automated workflow, where verified and validated simulation models
are parameterized, so that they can altered/modified in well-defined ways and reused with minimal user invention.
All events are logged on several levels, to support traceability, project documentation and quality control.

Parsim provides basic functionality for generating studies based on common design-of experiments
(DOE) methods, for example using factorial designs, response surface methods or random sampling,
like Monte Carlo or Latin Hypercube.

Parsim can also be used as an interface to the Dakota library; Dakota is run as a subprocess,
generating cases from a Parsim model template.

How it works
............

Once a prototype simulation case has been created, a corresponding simulation *model template* is created by
collecting all simulation input files, data files and scripts into a *template directory*.
The template directory may contain subdirectories, for example to separate files for different
phases of the simulation, or for different solvers, pre- and post-processors, etc.

The text files in a model template can then be parameterized by replacing numerical values, or text strings with
macro names. The filename extension :file:`.macro` is added to all files containing macros.
A model template usually defines default values for all its parameters in a specific parameter file.

When a simulation case is created, the model template directory is recursively replicated to create a *case directory*.
Parameterized files with extension :file:`.macro` are processed by a macro processor which replaces parameter names
by actual values. The processed file has the same name as the template file, but without the :file:`.macro` extension.

Parsim operations can also be carried out on a *study*, containing multiple cases.
A study is a directory containing multiple case directories. The cases of a study are defined in a *caselist* file;
the first column contains the case name, while other columns define values of parameters defined in a header row.
A study can also be created directly from one of the built-in DOE (Design Of Experiments) sampling schemes, e.g.
Monte Carlo, Latin-Hypercube, full or fractional factorial designs, etc. When the DOE functionality is used,
statistical distributions are specified in the parameter file for the variable parameters.

When creating a case or a study, custom parameter values can be defined on the command line, in a separate
*parameter file*, or in a *caselist* defining multiple cases of a *study*.

Your simulation project lives in a Parsim *project directory*, which holds all cases and studies of the project.
The project directory holds Parsim configuration settings and logs project events, like creation of cases and studies,
serious errors, change of configuration settings, etc.

The best way to learn more about how you can use Parsim, is to follow the tutorial examples.

.. _installation:

Installation
............

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
    is highly recommended. It works well on both Windows and Linux.


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

