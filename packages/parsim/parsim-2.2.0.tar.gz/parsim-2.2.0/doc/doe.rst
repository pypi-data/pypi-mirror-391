.. _doe_section:

Design Of Experiments (DOE)
===========================

Parsim integrates functionality for common Design Of Experiments (DOE) methods, both
random sampling schemes and well-known factorial designs.

The implementation of all methods (except Monte Carlo sampling) rely on the pyDOE
Python library; for details, see the pyDOE documentation.

The psm doe command is used to create a study, based on the specified DOE scheme and parameter
definitions in a parameter file. Some parameters are typically given fixed values in the
parameter file, as for an ordinary study. The difference from an ordinary study is that the parameter
file also defines a statistical distribution for each "uncertain", or varying, parameter.
The distribution specifications must follow the syntax of distribution in the scipy.stats module.
The cases created inside the study will then be sampled or mapped from these distributions
according to the chosen DOE scheme.

All schemes implemented in the pyDOE2 package (and possibly others) will eventually
be made accessible, but currently only the following schemes can be used:

* Monte Carlo random sampling (MC)
* Latin Hypercube Sampling (LHS)
* Plackett-Burman (fraction factorial designs)
* Two-level full factorial design
* General full factorial sampling (for more than two levels)
* Two-level fractional factorial sampling
* Central Composite Design (CCD)
* Generalized Subset Design (GSD)

To get help on using the ``psm doe`` command, you use the ``-h`` option, as usual: ::

    psm doe -h

This also gives a list of the currently implemented DOE schemes. You can get detailed help on
syntax and capabilities for each of these by adding the name of the scheme as argument to the
``-h`` option. For example, to get help on using the Plackett-Burman scheme, ::

    psm doe -h pb


Example: Tutorial "box" model with full factorial design
--------------------------------------------------------

We use the simplistic "box" model from the tutorial, assuming we want to investigate a full factorial
design in the parameters ``length``, ``width``, ``height`` and ``density``.

The lower and upper levels to use will be obtained by sampling the statistical distributions defined
for the variability of the parameters. These distributions are defined in
a parsim parameter file, and must match distribution classes defined in the ``scipy.stats`` library.
In this example we assume uniform distributions centred around the nominal values in the default parameters file.
The ``scipy.stats.uniform`` class takes the lower bound and the width as arguments.
The parameter file ``box_uniform.par`` looks like this:

.. literalinclude:: ../demo/box_uniform.par

Running ``psm doe -h`` tells you that the two-level full factorial scheme is called ``ff2n``.
Let's check for additional options:

.. literalinclude:: demo/psm_doe_h_ff2n

Considering all our distributions are uniform, it would be natural to use the lower and upper bound as our two
test levels. This, however, would not work for a normal distribution, or any other unbounded distribution.
The default method (and the only one currently implemented) for mapping levels to a given distribution is ``int``,
which means that we use a confidence interval of the distribution to define the lower and upper levels.
The ``beta`` argument defines the width of this interval. If we set ``beta`` to 0.999, for example,
then 0.01 % of the PDF is outside of this interval; half of it below the lower level, half above the upper level.

We create a study named "box_ff2n" for a two-level full factorial design:

.. literalinclude:: demo/psm_doe_ff2n

This design creates 16 cases in the study. The actual simulations can now be run as in the tutorial:

.. literalinclude:: demo/psm_run_doe

Collect is also done as before:

.. literalinclude:: demo/psm_collect_doe











