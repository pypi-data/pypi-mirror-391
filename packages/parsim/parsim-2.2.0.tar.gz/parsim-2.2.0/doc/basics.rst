Basic concepts
==============

Projects
--------

A Parsim simulation project lives in a project directory.
The project directory holds alla cases and studies of the project,
as well as custom Parsim configuration settings and event logs for the project.

To start using Parsim with your simulation, you need to initiate Parsim
in an existing directory,  using the ``psm init`` command.
This directory is now your Parsim project directory.

Configuration settings
......................

There are a number of configuration settings, which control how Parsim works with you project.
All settings have sensible defaults, which can be altered when the project is created.
For an existing project, configuration settings can be modified with the ``psm config`` command.

The following table describes the available project configuration settings.

.. tabularcolumns:: |l|p{7cm}|p{3cm}|

+----------------------------+-----------------------------------------------------------+-----------------------+
| Parameter                  | Description                                               | Default value(s)      |
+============================+===========================================================+=======================+
| ``template_root``          | Path to directory holding model templates for             | 'modelTemplates'      |
|                            | the project. Either an absolute path, or relative         |                       |
|                            | to the project directory.                                 |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
| ``default_template``       | Name of default model template directory                  | 'default'             |
|                            | (inside the ``template_root`` directory).                 |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
| ``default_parameter_file`` | Name of file defining default values for all              | 'default.parameters'  |
|                            | parameters of a model template. Path relative             |                       |
|                            | to template directory.                                    |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``default_executable``    | Name of default executable for ``psm run`` command,       |  None                 |
|                            | if not given on the command line.                         |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``python_exe``            | Path/name of Python executable, for use with              | 'python'              |
|                            | Python scripts and the ``psm run`` command.               |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``dakota_exe``            | Path/name of Dakota executable, for using Parsim as an    | 'dakota'              |
|                            | interface to the Dakota library.                          |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``psm_ignore_file``       | File containing ignore patterns. Files/directories        | '.psmignore'          |
|                            | matching a pattern will be ignored when templates         |                       |
|                            | are replicated into new cases.                            |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``psm_ignore_patterns``   | Project-wide definition of patterns to be ignored         | '.psm*', '.git*',     |
|                            | when processing model templates and creating cases.       | '.svn*', '\*~',       |
|                            | a pattern will be ignored when templates are              | 'default.parameters'  |
|                            | replicated into new cases.                                |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``log_level``             | Log level to use for parsim loggers (use only             | 'info'                |
|                            | 'info' or 'debug' for correct behavior).                  |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``default_results_file``  | Default name of file containing results, to               | 'results.json'        |
|                            | collect with the ``psm collect`` command.                 |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``case_prefix``           | Prefix to use when constructing a directory name          | 'case\_'              |
|                            | for case directories from a case name.                    |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+
|  ``study_prefix``          | Prefix to use when constructing a directory name          | 'study\_'             |
|                            | for study directories from a study name.                  |                       |
+----------------------------+-----------------------------------------------------------+-----------------------+



.. _templates:

Model templates
---------------

A :term:`model template` is a directory containing all files necessary to run a particular simulation.
The input files and scripts may be parameterized by replacing values and pieces of text with parameter names.
When a new case is created, the template directory will be replicated into a case directory, and all parameter names
replaced by case-specific values.

To create a model template, you usually start by creating a working prototype case, including all scripts used for
pre- and post-processing and running the simulation. Then you identify the settings and parameters you want to modify.

Where to store templates
........................

It is practical to place all model templates you want to use in the :term:`template root directory` of your project.
When you create projects, the model template to use is then specified as a relative path to this directory.

The template root directory is defined when you initialize your project directory, but can be changed later.
By default, the template root directory is a subdirectory named :file:`modelTemplates` inside the project directory.
In some situations, the template root directory could be in a central location separate from the project, for example
if you share model templates with your colleagues.

When you create new cases, it is also possible to specify the model template as an absolute path.

Parametrization of files and scripts
....................................

Parsim uses the Python library pyexpander to process parameterized text files in a model template.
The syntax for parameters is a valid Python variable name, enclosed in ``$()``.
For example, to introduce a parameter ``DENSITY`` in an input file, you would replace all
occurencies of the nominal value by the string ``$(DENSITY)``.

You must add the extension ``.macro`` to the name of all files containing parameters or macros;
the extension is removed when a case is created and the file is processed for macro expansion.

The **pyexpander** library allows you to do very advanced operations in your input files,
for example working with loops and conditionals; see the pyexpander documentation for details.

.. warning::

    The syntax for the pyexpander library can in principle be used to *redefine* the value of a model
    parameter inside a parameterized text files. **NEVER DO THIS**, as it breaks the link between
    the values you define when you created the case and the actual values in your input files!

Default parameters
..................

It is very important that all parameters of a model have well-defined values.
Each model template should therefor define default values for all parameters in the model template.
The default values usually represent a well documented and validated reference case.

Default parameter values are defined in a :term:`parameter file` named :file:`default.parameters`,
located in the root of the model template directory.

Ignoring files in templates
...........................

When you define model templates, you may have files in the template directory that you do
not want copied or processed when you create cases.
You can tell Parsim to ignore these files by specifying a matching ignore pattern in
a file named :file:`.psmignore`, placed in the same directory.

For example, you may keep detailed model documentation in a subdirectory :file:`docs` in
the model template, and you have som include files with extension :file:`.inc`, which are
included by macro expresssions in other files.
To avoid having these files copied into every case you create, you could but these
ignore patterns into a file :file:`.psmignore` in the template directory: ::

    docs
    *.inc

The following patterns are ignored by default: ::

    default.parameters
    .psm*
    .svn*
    .git*

These standard patterns prevent copying of the default parameters file and version control system files
(in case your model template is under version control).


Cases and Studies
-----------------

Your simulations take place in Parsim :term:`cases`.
When a simulation case is created, a :term:`model template` directory is recursively replicated to create
a case directory.
Parsim operations can also be carried out on a :term:`study`, containing multiple cases.
A study is a directory containing multiple case directories.

Parsim cases and studies are created using the commands :program:`psm case` and :program:`psm study`, respectively.
With the ``psm study`` command, multiple cases are defined in a :term:`caselist` file;
see Section :ref:`caselists` below.
Studies are also created by the ``psm doe`` command, which offers support
for common :ref:`Design of Experiments (DOE) <doe_section>` methods like full factorial and central
composite designs, or random sampling schemes like Monte Carlo or Latin Hypercube.
The ``psm dakota`` command allows parsim to be used as a
:ref:`front-end to the versatile Dakota library <dakota_section>`;
cases of a study are spawned dynamically by Dakota, based on the methods defined in a Dakota input file.

To run your simulation, you would use the command :program:`psm run` to execute a script on the case, or on all
cases of a study, see Section :ref:`running_scripts_executables`.
All events and operations are logged in event logs for the case, study and/or project.
This provides tracebaility and helps documentation of your simulation project.

When creating a case or a study, custom parameter values can be defined using several sources, which are listed
here, in order of precedence:

#. Parameter definitions on the command-line (see the command-line reference,
   Sections :ref:`psm_case` or :ref:`psm_study`),

#. For studies only: Parameters defined case-by-case in a :term:`caselist file`
   (see Section :ref:`caselists` below),

#. In a separate :term:`parameter file`, which is named on the command-line
   (see Section :ref:`param_files` below),

#. In a default parameters file located in the :term:`model template` directory
   (this file has the same format as other parameter files; see
   Section :ref:`param_files` below).

Parsim also defines a set of parameters containing parsim-related case information,
as defined in the table :ref:`table_parsim_parameters` below. The names of these parameters
all start with ``PARSIM_``.

.. tabularcolumns:: |l|p{7cm}|

.. _table_parsim_parameters:

.. Table:: Automatically defined parameters with parsim-related case information

    +----------------------------+-----------------------------------------------------------+
    | Parameter                  | Description                                               |
    +============================+===========================================================+
    | ``PARSIM_PROJECT_NAME``    | Name of the parsim project.                               |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_PROJECT_PATH``    | Path to directory of the parsim project.                  |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_TEMPLATE_PATH``   | Path to template directory used to create the case.       |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_STUDY_NAME``      | Name of Study, if any (otherwise empty string).           |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_CASE_NAME``       | Name of Case.                                             |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_CASE_ID``         | Case ID, which can be used as "target" with some          |
    |                            | parsim commands. Uses colon notation, for example         |
    |                            | ``A:1`` for a case "1" of a study named "A".              |
    +----------------------------+-----------------------------------------------------------+
    | ``PARSIM_VERSION``         | Version of parsim used to create the case.                |
    +----------------------------+-----------------------------------------------------------+


.. program:: psm case

When you create cases and studies from model templates, the default values are often used for many of the
model parameters, for example solver settings. The command-line option :option:`--define` can be used to set
custom values for a small number of parameters. Otherwise it is more practical to prepare a parameter file,
especially if this parameter combination will be used several times.
When you create a study with multiple cases, a :term:`parameter file` is often used to define parameter values
shared by all cases in the study. The :term:`caselist file` is then used to define only the parameter values that
vary between cases.

The properties and formats of :term:`parameter files` and :term:`caselist files`
are described in the following sections.


.. _param_files:

Parameter files
...............

Parameter files assign real values for parameters in your model. Paraeter files are used when you create
individual cases. When creating studies, a parameter file is often used to define all parameters that have the same
values for all cases.
The :term:`default parameter file` ``default.parameters``, located in the root of every model template, is also written in
the same format.

In its simplest form, a parameter file is a text file with two columns separated by white-space.
The first column contains parameter names and the second column defines their values.
Parameter values can be numbers or text strings. Strings should be enclosed in single or double quotes.

The complete syntax of parameter files are described by the following rules:

* Rows starting with  characters "#" or ";" will be treated as comments and skipped.

* Parameter name and value columns can be separated by white-space and/or by a single colon ":".

* Values may be numbers or text strings. Strings should be enclosed in single or double quotes.

* If the value column (column two) is followed by one of the chracters "#" or ";", everything
  that follows is treated as a description of the parameter. This may be used in later Parsim
  versions, to provide help to the user of a model template.


The following is an example of a parameter file, where we have used all valid format options: ::

    #------------------------------------------------------------------------
    #  This is a sample parameter file (these comment lines are skipped...)
    #------------------------------------------------------------------------
    ; This is also a comment line. They can start with both "#" and ";".
    ; The blank line below is also skipped...

    # Geometry parameters
    length = 12.0
    width: 8
    height      24      # [m] Height of our object.
    # It's practical to describe parameters this way (see above)!
    # Especially in a default parameter file, where all parameters
    # of a model template occur.

    # Strings are quoted:
    color:  'blue'

In practice, you would use consistent formatting of your choice, to improve readability.

.. _caselists:

Caselist files
..............

A caselist is mandatory when you create a study. The caselist has one row for each
case in the study and it defines the parameter values that differ between cases in the study.

The first row is a header row, starting with the string ``CASENAME`` as the first field, followed by names
of the parameter to define.
Then follows one row for each case of the study. The first field defines the name of case,
followed by values for the parameters in the header row.
Fields in a row are white-space or comma-delimited. Extra white-space is ignored.

The following example is a valid caselist file: ::

    # Comment lines are skipped. (They start with "#" or ";")
    CASENAME  length    width    height  color
    A1        12.0      3.1      2       'blue'
    A2        12.0      3.1      4       'blue'
    B1        8.22      3.1      2       'red'
    B2        8.22      3.1      4       'red'


.. _running_scripts_executables:

Running scripts and executables
-------------------------------

The command ``psm run`` is used to run scripts or executables; for an individual case, or for all cases in a study.

The first positional argument to this command is an identifier of the target case or study.
This could be a single case or a study.
It could also be a single case within a study; if so, both study and case names are provided,
separated by a colon ":".
For example, ``s2:c1`` identifies the case "c1" of study "s2".

The second positional argument is the name of the script or executable to run.
The remainder of the command line is forwarded as arguments to the script/executable.
Unless the script or executable is given as an absolute path, it is looked for in the following locations
(in order of precedence):

#. The current working directory (where ``psm run`` is executed),

#. The ``bin`` subdirectory of the project directory (if it exists),

#. The root of the case directory,

#. The ``bin`` subdirectory of the case directory (if it exists),

#. In a subdirectory of the case directory, as specified by the option ``--sub_dir``.


The script or executable executes in the root of the case directory, or in a subdirectory
specified by the ``--sub_dir`` option.
The subprocess running the script or executable inherits the environment of the calling process (the terminal
in which ``psm run`` was called), augmented with a set of environment variables with parsim-related case information.
These extra variables correspond with the parameters in the table :ref:`table_parsim_parameters`.

.. note::

    Parsim uses the ``subprocess`` python module to execute scripts and executables.
    Sometimes a script or executable will not run, unless the subprocess is started through a shell interpreter
    (corresponds to using the ``shell`` option of the ``subprocess.Popen`` constructor).
    This behavior can be forced with the ``--shell`` option of the ``psm run`` command.


Collecting results
------------------

Results from parsim studies may be collected conveniently in tabular format using the ``psm collect`` command.
This assumes that the execution of a case produces a text file with output scalars in JSON format;
see the :ref:`tutorial examples <tutorial_section>`.