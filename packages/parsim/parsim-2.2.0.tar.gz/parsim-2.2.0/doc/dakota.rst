.. _dakota_section:

Dakota interface
================

Parsim can be used as an interface to the `Dakota toolkit <https://dakota.sandia.gov/>`_,
developed by Sandia National Laboratories.
For projects where you already have developed parameterized models with Parsim, this gives
easy access to the most complete collection of methods and tools for
optimization, uncertainty quantification and parameter estimation available.

What you need is a Dakota input file, which specifies which method to use and which variables to vary.
You also need to add a couple of lines to your simulation script, so that it outputs the response variables
that Dakota wants back. You then use the ``psm dakota`` command to have Parsim create an empty Study and start Dakota.
Dakota uses a special analysis driver to create the cases needed for the analysis, based on your existing Parsim
model template.

Dakota must be installed according to instructions. The Dakota executable should be in the executable path of your
OS environment, so that the single command ``dakota`` will start the program.
To check your Dakota installation, you can run Dakota to output version information: ::

    > dakota -v
    Dakota version 6.5 released Nov 11 2016.
    Repository revision f928f89 (2016-11-10) built Nov 11 2016 05:09:45.


The Dakota input file
---------------------

The Dakota input file contains a specification of the method to use, the model parameters to modify,
how to execute the simulation and what output to expect.
You need to study the Dakota user documentation and tutorials to learn how to use the functionality provided.

In the "variables" section of the input file, you need to make sure the variable "descriptors" match parameter names
in your Parsim model template.

In the "interface" section of the Dakota input file, you need to tell Dakota how to create a new case and
execute the simulation. This section must have exactly this content: ::

    interface
      analysis_driver = 'psm_dakota_driver'
        fork
        parameters_file = 'params.in'
        results_file = 'results.out'

Here ``psm_dakota_driver`` is a special script executable installed with Parsim.


Output from the simulation
--------------------------

Your simulation script needs to be modified so that it writes the response variables in the proper format
to an output file in the case directory, usually ``results.out``.
The name of the output file is specified by the "results_file" entry in the
interface section of the Dakota input file (see above).

Restarts
--------

The Parsim interface supports the Dakota restart functionality. Dakota writes a binary restart file with
results from the function evaluations. Parsim saves restart files in the Study directory, for successive Dakota
restarts. The initial Dakota run will have a run index of 0, and restarts will be numbered from 1, 2, etc.
Parsim also saves copies of the Dakota inputfile used at each run, tagged by the same run index.

The ``psm dakota`` command has an option ``--restart`` to request restart and specify the index of
the restart file to use.
The index number itself is optional; if no index is given, the last restart file will be used for the restart.
You will still need to specify Dakota input file and simulation executable, as these may have changed.

Dakota has an option ``-stop_restart`` to specify how many saves records to read from the restart file.
The ``psm dakota`` command has a corresponding option ``--stop_restart``.

To understand how the Dakota restart functionality works, please consult the Dakota documentation.

Dakota execution phases and pre-run
-----------------------------------

Dakota has three execution phases: pre-run, run and post-run. Some Dakota methods are implemented
so that the pre-run phase can be run separately, which means that a table of case specifications
will be generated without actually launching a simulation executable.
This functionality is typically supported for sampling, parameter study and DACE methods.

The ``psm dakota`` command has an option ``--pre_run`` to use Dakota in pre-run mode.
If supported by the selected method, this will create the corresponding Parsim cases of the study.
The user can then use this as any other study, running simulation scripts and other activities using the
``psm run`` command, collecting results with the ``psm collect`` command, etc.


Example: Rosenbrock, gradient optimization
------------------------------------------

As an example, let us look at the Rosenbrock problem of the Dakota user documenation, where the gradient
optimization method is used to find the minimum of the Rosenbrock function.

Assume we have the following Python script, which computes the Rosenbrock function for a fixed point:

.. literalinclude:: ../demo/rosenbrock.py

We assume you already have Parsim project to work with, otherwise create one as explained in the tutorial.

Creating the model template
...........................

In the ``modelTemplates`` directory of your project, create a new model template called "rosenbrock": ::

    > cd modelTemplates
    > mkdir rosenbrock

Inside the rosenbrock directory, create a parameterized version of the Python script above, and name it
``rb.py.macro``:

.. literalinclude:: ../demo/modelTemplates/rosenbrock/rb.py.macro

The only changes we have made is to introduce parameters ``x1`` and ``x2`` for the input data,
and to write the computed function value to the output file ``results.out``.
We also chose to output the results in json format, as discussed in the Parsim tutorial,
in case we would want to collect the results also in tabular format with the ``psm collect`` command.

The model template must also have a ``default.parameters`` file, which defines default values for the parameters:

.. literalinclude:: ../demo/modelTemplates/rosenbrock/default.parameters

Modifying the Dakota input file
...............................

Compared to the original example in the Dakota manual, the only change needed in the input file
``rosen_grad_opt.in`` is the specification of the analysis driver in the interface section:

.. literalinclude:: ../demo/rosen_grad_opt.in

We here need to use the special executable ``psm_dakota_driver``.

Running Dakota with Parsim
..........................

To run the Dakota optimization, with our new Parsim model template, use the ``psm dakota`` command: ::

    psm dakota --template rosenbrock --name rb1 rosen_grad_opt.in rb.py

The first positional argument is the Dakota input file, the second is the name of the simulation executable,
in this case the simple parameterized Python script above.

The output from Dakota is found inside the study directory ``study_rb1``.
The standard output from Dakota (the execution history) is found in ``dakota.out``.
The Dakota input file also instructed Dakota to write tabular data to the file ``rosen_grad_opt.dat``.

Restarting a failed Dakota run
..............................

The example above generates 134 cases in the study. Assume that the process stops and crashes after, say,
20 succesful cases (for example because of a full disk, or something else). We would then want to restart
the Dakota run, but making use of the existing 20 succesful function evaluations.
The Dakota restart functionality makes this possible.
In this example, you restart the Dakota execution with the command ::

    psm dakota -t rosenbrock --name rb1 --restart 0 --stop_restart 20 rosen_grad_opt.in rb.py

We here explicitly selected the initial restart file (0), although this is the same as the last one
generated in this example.
Parsim stores succesive restart files in the study directory, numbered by an integer run index, 0 corresponding
to the original run.
We also explicitly told Dakota to only use the first 20 function evaluations
of the restart file; by default it would use as many as it would find.

Note that we define the name of the Dakota input file and the simulation executable for the restart.
This is because one may want to modify these, to avoid the problems experienced in the previous run.

Example: Generating cases with the Dakota pre-run functionality
---------------------------------------------------------------

For the optimization problem above, Dakota must select parameter values for each new case based on the result
of the previous cases. For other methods, for example random sampling methods or traditional
response surface designs, parameter values for all cases can be produced before starting any simulations.
This is possible with the Dakota pre-run functionality.

Let us assume we want to create a complete study with 200 cases, based on the Dakota random sampling method, using
the Dakota input file ``rosen_sampling.in``:

.. literalinclude:: ../demo/rosen_sampling.in

This file is essentially the same as in the Dakota documentation.
For consistency, we have modified the interface section to use
the Parsim simulation driver, although the driver will never be executed in pre-run mode.

The Parsim study ``rb2`` can now be created in Dakota pre-run mode, ::

    psm dakota -t rosenbrock --name rb2 --pre_run rosen_sampling.in rb.py

With the command-line syntax currently implemented, we have to provide a name of a simulation executable,
although it is not used.

Once the study and its cases are created, you interact with it as with any other Parsim study.
For exemple, you would run the actual Rosenbrock "simulation" for all cases with the ``psm run`` command, ::

    psm run rb2 rb.py

Since the ``rb.py`` script above also outputs the response in the json file ``results.json``, we can
use the ``psm collect`` command to collect all results into a table: ::

    psm collect -i results.json rb2

The default, the results table was written in space-separated format to the file ``results.txt``
in the study direcory.

Example: Polynomial Chaos Expansion on the Rosenbrock problem
-------------------------------------------------------------

As an additional example, we apply the Polynomial Chaos Expansion method (PCE) on the
Rosenbrock function.
This example is taken from Section 5.4.1.1 in the Dakota User's Manual; the interested
reader should read about these methods there, to fully appreciate what is going on.

Again, we modify the interface section of the input file found in the Dakota documentation:

.. literalinclude:: ../demo/rosen_uq_pce.in

We then run Dakota through Parsim, as before, ::

    psm dakota --template rosenbrock --name pce rosen_uq_pce.in rb.py

The results output by Dakota are found in the file ``dakota.out`` in the study directory ``study_pce``.
