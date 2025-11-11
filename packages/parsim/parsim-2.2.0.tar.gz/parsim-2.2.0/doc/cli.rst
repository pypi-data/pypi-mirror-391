Command-line reference
======================
.. program:: psm

Parsim is a command-line tool. The command-line client program is called :program:`psm`.

The general syntax is ::

    psm [-h] SUBCOMMAND [<arguments>]

The available subcommands are described in the following sections.

Use option :option:`-h` to get information about available subcommands.
You get detailed information about each subcommand using the command :program:`psm help <subcommand>`,
or :program:`psm <subcommand> -h`.

.. option:: -h, --help

    Show help message, including available subcommands, and exit.

.. option:: SUBCOMMAND [<arguments>]

    Parsim subcommand (see below), with arguments.


Project initialization and configuration
----------------------------------------

Before Parsim can be used with your project, your project directory must be *initialized* using the
:ref:`psm_init` command.
Most of the configurations settings may be changed later using the :ref:`psm_config` command.


.. _psm_init:

psm init
........

.. argparse::
    :module: parsim.commands
    :func: init
    :prog: psm init

.. note::

    When configuration settings containing strings are defined using the ``--config`` option,
    the whole option argument string must be enclosed in quotes. The string value itself must also
    be quoted. For example, the following option will correctly set the value of the ``default_executable``
    setting: ::

        psm init --config 'default_executable="myScript.sh"' myProject


.. _psm_config:

psm config
..........

.. argparse::
    :module: parsim.commands
    :func: config
    :prog: psm config


Creation of cases and studies
-----------------------------

Individual cases can be created using the :ref:`psm_case` command,
while entire case studies are created using the :ref:`psm_study` command.

Case studies can also be created with the :ref:`psm_doe` command.
The DOE (Design Of Experiments) functionality uses built-in
sampling algorithms to generate the parameter matrix, rather than reading it
from a caselist.


.. _psm_case:

psm case
........

.. argparse::
    :module: parsim.commands
    :func: case
    :prog: psm case

.. note::

    When string values are defined for parameters using the ``--define`` option,
    the whole option argument string must be enclosed in quotes. The string value itself must also
    be quoted. For example, when creating a case ``A13``, the following option will correctly set
    the value of the ``output_file`` parameter to ``out.txt``: ::

        psm case --template box --define 'output_file="out.txt"' A13


.. _psm_study:

psm study
.........

.. argparse::
    :module: parsim.commands
    :func: study
    :prog: psm study


.. _psm_doe:

psm doe
.......

.. argparse::
    :module: parsim.commands
    :func: doe
    :prog: psm doe

To get help on an individual sampling scheme, search help for the doe command and add name of scheme.
For example: ::

   psm help doe <scheme>

or ::

   psm doe -h <scheme>

The following table shows the currently implemented DOE schemes.

.. csv-table:: Available DOE schemes.
   :widths: auto
   :file: doe_schemes.inc


.. _psm_dakota:

psm dakota
..........

.. argparse::
    :module: parsim.commands
    :func: dakota
    :prog: psm dakota


Operations on cases and studies
-------------------------------

The following subcommands perform specific operations on a specified *target*,
which may be a either a case or a study.
In particular, the :ref:`psm_run` command is used to execute scripts (or other executables)
on a specific case, or on all cases of a study.

The target can be either a case or a study. Based on the name provided, the current directory is searched
for a matching case or study directory.
In case both a case and study is found, an error is issued. If this happens, please specify the full name of
the directory instead (starting with either ``case_`` or ``study_``).

It is possible to specify an individual case belonging to a study, by specifying both study and case names,
separated by a colon. For example, the following will print detailed information about the case ``A1``,  which
is part of the study ``test_matrix``: ::

    psm info test_matrix:A1

Some commands, like :ref:`psm_info` and :ref:`psm_comment`, can operate also on the project as a whole.
If no ``TARGET`` argument is specified, the current project is used as the target.


.. _psm_run:

psm run
.......

.. argparse::
    :module: parsim.commands
    :func: run
    :prog: psm run


.. _psm_collect:

psm collect
...........

.. argparse::
    :module: parsim.commands
    :func: collect
    :prog: psm collect


.. _psm_info:

psm info
........

.. argparse::
    :module: parsim.commands
    :func: info
    :prog: psm info


.. _psm_log:

psm log
.......

.. argparse::
    :module: parsim.commands
    :func: log
    :prog: psm log


.. _psm_comment:

psm comment
...........

.. argparse::
    :module: parsim.commands
    :func: comment
    :prog: psm comment
