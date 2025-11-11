Glossary
========

.. glossary::
    :sorted:

    Parameter file
    Parameter files
        A file defining values for parameters. Each row defines one parameter. The parameter name is in the first
        column and the value is in the second. The columns can be separated by white-space, a colon ":", or a en
        equality sign "=". String values should be enclosed in quotes. A comment may follow the value, after a
        separator "#" or ";".

    Default parameter values
    Default parameter file
        It is very important that all parameters of a model have well-defined values.
        Each model template should therefor define default values for all parameters in the model template.
        This is done in the default parameter file.
        The default values usually represent a well documented and validated reference case.

    Model template
    Template directory
        A model template is a directory containing all files necessary to define a model and run a simulation of it.
        The files may be organized in subdirectories. A model template should define :term:`default parameter values`
        for all parameters in the model.

    Template root directory
        A directory for storing all model templates used in your simulation project. By default,
        this is a subdirectory :file:`modelTemplates` in the root of the project directory.
        It could also be a central location, for example if you share models with your colleagues.
        The template root directory is defined when you initialize your project directory, but can be changed later.

    Project
    Project directory
        When you use Parsim, your simulation project is represented by a project directory structure.
        The project directory must be initialized to use Parsim. This creates some basic configuration settings
        which apply to the whole project. Inside the project (directory), you create and operate on cases and studies.

    Case
    Cases
    Case directory
        A case (or rather a case directory) is a replica of a model template, where model parameters have been replaced with actual values.
        The case is where model simulation, pre- and post-processing takes place.

    Study
    Studies
    Study directory
        A study contains multiple cases, defined in a caselist. Operations, like running scripts, can be carried out
        on all cases of a study with one single command. Results from all cases of a study can be collected in a
        table for analysis and post-processing.

    Caselist
    Caselist file
    Caselist files
        A caselist is used to create multiple cases in a study.
        The caselist has one row defining each case of the study.
        The first column (with heading "CASENAME") of the caselist contains the name of case.
        Subsequent columns contain parameter values.
