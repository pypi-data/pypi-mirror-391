.. _tutorial_section:

Tutorial
========

Your parameterized model templates are usually stored in the project directory.
The default location is a subdirectory :file:`modelTemplates` in the root of the project directory,
but this can be customized by changing the project configuration settings.
In some cases it is practical to store all model templates in a centralized location, separate from
the project directory.

In this tutorial we will set up a very simple simulation project example, with one model template
located inside the project directory.

For this tutorial, we assume that you work in Linux or Cygwin.

Parsim is a command-line tool. The main program is called :program:`psm`.
Use it with option :program:`-h` to get information about available subcommands.
You get detailed information about each subcommand using the command :program:`psm help <command>`.

Creating a project
------------------

Let's call our project "myProject" and assume we want it in project directory :file:`my_proj` in our
home directory. We create the project directory and initialize it using the :command:`psm init` command:

.. literalinclude:: demo/mkdir_psm_init


Creating a simple model template
--------------------------------

Assume we have the following Python script, named ``boxcalc.py``, which represents a very simple "simulation model":

.. literalinclude:: ../demo/boxcalc.py

You can run this script through the Python interpreter: ::

    $ python boxcalc.py
    base_area = 48
    volume = 72.0
    mass = 72000.0
    Successfully written results to output file "output.json"

If you run Linux, you can give the script executable permissions and run it directly: ::

    $ ./boxcalc.py
    base_area = 48
    volume = 72.0
    mass = 72000.0
    Successfully written results to output file "output.json"

The script uses the ``json`` library to format the output dictionary in json format.
The resulting output file :file:`output.json` has the following content: ::

    {"base_area": 48, "volume": 72.0, "mass": 72000.0}

This script has hard-coded parameter values. We can say that these values define
a working reference case, where the results are known and "validated", in some sense.
This is a good starting point for creating a parameterized model template, which we will call ``box``.

By default, Parsim assumes that model templates are stored in a subdirectory ``modelTemplates`` in the
project directory.
Let us start by creating the model template directory, and copy our existing model files there.
For your convenience, the ``boxcalc.py`` script can be found in the ``demo`` subdirectory of
your Parsim installation; in our case, Parsim is installed in ``$HOME/psm``.
As we copy, we change the name of the script to ``calc.py``.
Inside the project directory, ::

    $ mkdir modelTemplate
    $ mkdir modelTemplate/box
    $ copy $HOME/psm/demo/boxcalc.py modelTemplate/box/calc.py

Now we go to the template directory, and continue there: ::

    cd modelTemplate/box

In a real application, the executable for running the simulation would usually read input data from another file,
but in our example the input data is hard-coded in the script itself. This means that the script itself will be
parameterized. Let us start by adding  the extension ``.macro`` to the file name, so that Parsim will parse it for
parameter substitution when you create cases from the template. We also set execute permissions on the script file
(permission of the parameterized file will be inherited by the resulting script file, when
cases are created): ::

    $ mv calc.py calc.py.macro
    $ chmod u+x calc.py.macro

The file contains the following numerical model parameters: ``length``, ``width``, ``height`` and ``density``.
It also contains the string parameter ``color``. We note that the name of the output file is also hard-coded
in the script file; while we're at it, we let this file name be a parameter, too.

We now create a default parameter file with the standard name ``default.parameters``. We use the hard-coded
values as the default values, as this represents our known and presumably validated reference case...
The contents of ``default.parameters`` could then be:

.. literalinclude:: ../demo/modelTemplates/box/default.parameters

Note that we this file is in :term:`parameter file` format, and that we have used comments to
document the model template.

The next step is to substitute the hard-coded values in the script file with the parameters we defined:

.. literalinclude:: ../demo/modelTemplates/box/calc.py.macro
    :language: python

Note that we put quotes around ``$(output_file)``, as the parameter substitution returns the string without quotes.

That's it, our first model template is ready!

Creating a case and running the simulation
------------------------------------------

To create cases, we use the ``psm case`` command. See :ref:`psm_case` for details.
The following creates a case in a case directory ``case_ref``, with the default parameters defined above:

.. literalinclude:: demo/psm_case_ref

In this simple example, we can easily make a custom case with parameters modified on the command-line.
For example, let's make a case "bigBox", with higher box and larger density:

.. literalinclude:: demo/psm_case_define

Let's run the "simulation" of this larger box, using the :command:`psm run` command:

.. literalinclude:: demo/psm_run_case

As indicated by the console output, the standard output of the script is found
in the file ``calc.out`` in the case directory:

.. literalinclude:: demo/case_bigBox/calc.out

Creating and running a study
----------------------------

It is equally simple to setup and operate on a whole parameter study, containing several cases,
using the :command:`psm study` command.

You would usually use a :term:`parameter file` to define parameter values that are common to all cases and
a :term:`caselist file` to define the case names and the parameters that differ between cases.
In our simple tutorial example, however, it is sufficient to use only a :term:`caselist file`.

Let us assume that we want to create a study named ``variants``, with case names and parameters defined
in a caselist file named ``variants_caselist``, as follows:

.. literalinclude:: demo/variants_caselist

.. program:: psm study

We now use the :command:`psm study` command to create the study and all its cases:

.. literalinclude:: demo/psm_study

This creates a study directory ``study_variants`` in the current directory; the study directory
contains all the case directories.
Note that we used option `--name` for naming the study and the option `--description`
to provide useful information about its content.

We can run the simulation of all cases of the study with one single command:

.. literalinclude:: demo/psm_run_study

Collecting results from a Study
-------------------------------

We can use the :command:`psm collect` command to collect the output data from all cases and
present it in one single table.

.. literalinclude:: demo/psm_collect

By default, results are read from a JSON formatted file :file:`results.json` in the case directories. For the example
here, a results file in a case would look something like this:

.. literalinclude:: demo/study_variants/case_A3/results.json

The ``--input`` option can be used to specify a custom file path inside the case directory (a comma-separated list
of multiple files is allowed).
Unless a delimited format is requested (by defining a delimiter with the ``--delim`` option),
the output is in tabular format, white fixed column spacing.
The name of the output file is derived from the name of the (first) input file, unless specified explicitly with
the ``--output`` option. )
In this example, the output is written to the file ``results.txt``, located in the study directory:

.. literalinclude:: demo/study_variants/results.txt

If the input file is missing or incomplete for one or more cases, this will be reported. Only the succesfully
processed cases will be included in the output file.

Every time the collect command is run (e.g. collecting additional results from another simulation in the same Study),
a tabular text file "study.results" inside the Study directory will be updated with the new data. This file will
then contain all aggregated results for the study. All cases are reported in this file, even if
data is missing. Missing data is reported as "NaN" in the table. Input parameters are not included in "study.results".
These can instead be found separately in the file "study.caselist". The files "study.results" and "study.caselist"
could be conveniently imported into pandas DataFrame objects for further processing. As an example, consider a study
with 16 cases created from the "box" template. One simulation executable outputs results variables "basearea", "mass"
and "volume" for all 16 cases. Another simulation outputs the result variable "d_eff" in another results file, but this
simulation fails for several of the cases. The `psm collect` command is run separately after each of the simulations,
to collect results. The file "study.results" would now look something like this:

.. literalinclude:: demo/study_box_ff2n_A/study.results

Note that all output variables of both simulations are included in the file, but there is missing data, "NaN", in
the "d_eff" column for some of the cases.


Object information and event logs
---------------------------------

We can use the :command:`psm info` to get information about the properties of a case, study or about the project as
a whole. For example, let's look at the properties of
the ``bigBox`` case:

.. literalinclude:: demo/psm_info_bigBox

All Parsim objects (cases, studies and project) have an event log, where all events and operations are logged.
The :command:`psm log` command prints the event log to the console.
For example, we look at the event log of the ``bigBox`` case:

.. literalinclude:: demo/psm_log_bigBox
