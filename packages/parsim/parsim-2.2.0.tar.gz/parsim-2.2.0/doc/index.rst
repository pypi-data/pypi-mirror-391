.. parsim documentation master file, created by
   sphinx-quickstart on Tue Apr 26 15:21:40 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _contents:

Welcome to the documentation of Parsim
======================================

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

.. toctree::
   :maxdepth: 2

   intro
   basics
   tutorial
   parameterization
   doe
   dakota
   cli
   api
   installation
   glossary
   using_API
   changes

..
   parameters
   projects
   reference
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

