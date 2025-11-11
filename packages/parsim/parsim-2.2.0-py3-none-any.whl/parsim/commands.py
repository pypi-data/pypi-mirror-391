# -------------------------------------------------------------------------
# Copyright (C) 2016-2017  RISE Research Institutes of Sweden AB
#
# This file is part of parsim.
#
# Main developer: Ola Widlund, RISE Research Institutes of Sweden AB
#                 (ola.widlund@ri.se, ola.widlund@yahoo.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------
"""
Subcommands provided by Parsim tool.

Each available subcommand corresponds to a function in this module.
"""
import os.path
import argparse
from argparse import ArgumentParser
from textwrap import dedent

import parsim
from parsim.core import Project, Case, Study, ParsimError, parse_parameter_file
from parsim.loggers import logger


logger.debug("STARTING")

project_commands = ['init', 'config', 'help', 'info', 'version', 'log']
case_commands = ['case', 'study', 'doe', 'dakota', 'run', 'comment', 'collect']  # copy, archive
all_commands = project_commands + case_commands


def _get_config_parent_argparser():
    """Return parent ArgumentParser with arguments common to init and config commands."""
    pp = ArgumentParser(add_help=False)
    pp.add_argument('--description', '-m', type=str,
                    default=argparse.SUPPRESS,
                    help='Project description (text in quotes)')
    pp.add_argument('--default_executable', type=str,
                    metavar='EXECUTABLE',
                    default=argparse.SUPPRESS,
                    help='Name/path of default executable for the "run" command')
    pp.add_argument('--template_root', type=str,
                    metavar='DIRECTORY',
                    default=argparse.SUPPRESS,
                    help='Path to directory where model templates are stored')
    pp.add_argument('--default_template', type=str, metavar='DIRECTORY',
                    default=argparse.SUPPRESS,
                    help='Name of default model template to replicate (a directory). ' \
                         'A relative path is searched for in the current and in the template ' \
                         'root directory. Could also be an absolute path.')
    pp.add_argument('--default_parameter_file', type=str, metavar='FILENAME',
                    default=argparse.SUPPRESS,
                    help='Name of parameter file holding default parameter definitions. ' \
                         'The default name is "default.parameters", located in the ' \
                         'model template directory.')
    pp.add_argument('--log_level', type=str, choices=['debug', 'info', 'warning', 'error'],
                    default=argparse.SUPPRESS,
                    help='Set log-level for logging. The default is "info". ' \
                         'This value is stored in the project settings.')
    pp.add_argument('--config', '-c', type=str, action='append', metavar='PARAMETER=VALUE',
                    help='Definition of project configuration name=value pairs. Could be a ' \
                         'comma-separated list of name/value pairs. (Explicit config options ' \
                         '(above) have precedence.)')
    return pp


def _get_target_parent_argparser(mandatory=False):
    """Return parent ArgumentParser with target positional argument common to several commands."""
    pp = ArgumentParser(add_help=False)
    if mandatory:
        pp.add_argument('target', type=str, metavar='TARGET',
                        default=None,
                        help='Name of target (case or a study)')
    else:
        pp.add_argument('target', type=str, metavar='TARGET',
                        nargs='?', default=None,
                        help='Name of target (case or a study). If missing, the current project is assumed.')
    return pp


def _process_target_argument(parser, target_arg):
    """
    Process a command-line target argument and generate parser errors if invalid.
    """
    project = Project()
    try:
        target = project.find_target(target_arg)
    except ParsimError as e:
        parsim.error(e)
    return target


def _get_study_case_parent_argparser(doe=False):
    """Return parent ArgumentParser with arguments common to case, study and doe commands."""
    pp = ArgumentParser(add_help=False)
    pp.add_argument('--description', '-m', type=str,
                    help='Description of case or study (text in quotes)')
    pp.add_argument('--template', '-t', type=str, metavar='TEMPLATE',
                    help='Name of the model template. This is either an absolute directory path, ' \
                         'a path relative to the current directory, or a directory inside the template ' \
                         'root directory of the parsim project.')
    if not doe:
        pp.add_argument('--parameters', '-p', type=str, metavar='PARAMETER_FILE',
                        help='Name of a parameter file (absolute path, or relative to the current directory)')
    pp.add_argument('--define', '-D', type=str, action='append', metavar='PARAMETER=VALUE',
                    help='Definition of parameter name=value pairs. Could be a comma-separated list ' \
                         'of name/value pairs. Overrides values in a parameter file.')
    return pp


_study_case_common_description = dedent('''\
    A case is created from a model template. A template is a directory, whose
    content will be replicated recursively to form a new case. During replication, all files with extension
    ".macro" are assumed to be parameterized. These files are processed for macro expansion, in which
    parameter names are replaced by actual values. The processed files have the same name, but
    without the ".macro" extension. Parameter values can be specified on the command line directly
    (with the --define option), or in a PARAMETER_FILE. A model template usually defines default variables
    for all its parameters.''')
"""Common description string for ``psm case`` and ``psm study`` commands."""


def _process_parameter_file_option(param_option, doe=False):
    """
    Create parameter dict from parameter file.

    Returns tuple (parameter_dict, parameter_file_path).
    """
    if param_option:
        param_file = os.path.abspath(param_option)
        if os.path.isfile(param_file):
            if doe:
                param_file_dict, distr_dict = parse_parameter_file(param_file, doe=True)
            else:
                param_file_dict = parse_parameter_file(param_file)
        else:
            parsim.error('The specified parameter file "%s" is not found' % param_file)
    else:
        param_file = None
        param_file_dict = {}
        distr_dict = {}
    if doe:
        logger.debug('Processed parameter file option: param_file_dict= %s \n distr_dict= %s' %
                     (repr(param_file_dict), repr(distr_dict)))
        return param_file_dict, distr_dict, param_file
    else:
        logger.debug('Processed parameter file option: param_file_dict= %s' % repr(param_file_dict))
        return param_file_dict, param_file


def _process_parameter_definition_options(parser, parameter_option):
    """Create parameter dict from command-line definitions."""
    param_dict = {}
    if parameter_option:
        for item in parameter_option:
            itemlist = item.split(',')
            for i in itemlist:
                pair = i.split('=')
                if len(pair) != 2:
                    parser.error('Invalid parameter specification: %s' % item)
                # As in pyexpander library, execute expressions in a namespace, to retain variable types
                my_space = {}
                exec(i, my_space)
                param_dict[pair[0]] = my_space.get(pair[0])
    logger.debug('Processed parameter definition option: param_dict= %s' % repr(param_dict))
    return param_dict


def _process_doe_args(parser, args):
    args_dict = {}
    dummy_global = {}
    for a in args:
        # Check that argument is in expected form of key-value pair
        try:
            arg_key, arg_value = a.split('=')
        except (ValueError):
            parsim.error('Error processing DOE argument: "%s". Expects key-value pair.' % a)
        # Process/execute arg definition
        try:
            exec(a, dummy_global, args_dict)
        except (NameError):
            # NameError is probably because the value is an unquoted string argument...
            args_dict[arg_key] = arg_value
        except (SyntaxError):
            parsim.error('Error processing DOE argument: "%s"' % a)
        # Detect function references, so that argument value is interpreted as string instead
        if callable(args_dict[arg_key]):
            args_dict[arg_key] = arg_value
    assert len(args) == len(args_dict), 'Unexpected entries in dict of DOE arguments: %s' % (repr(args_dict))
    return args_dict


def init(argv=None):
    """Create a new Parsim project in the current directory."""
    description = "Create a new project called NAME in the current directory. " \
                  "This stores some metadata and configuration settings for the project. " \
                  "There are sensible defaults for all settings, and most of them can " \
                  "be changed later using the psm config command."
    config_parent = _get_config_parent_argparser()
    parser = ArgumentParser(parents=[config_parent], prog='psm init', description=description)
    parser.add_argument('project_name', metavar='NAME', help="a short name for the project; should not contain spaces.")

    if argv is None:
        return parser

    args = parser.parse_args(argv)
    config_dict = vars(args).copy()
    config_dict.pop('project_name')

    # Pop and process list with config key/value pairs from --config option.
    cli_config_option = config_dict.pop('config', None)
    cli_config_dict = _process_parameter_definition_options(parser, cli_config_option)

    # Explicit options (set by explicit cli arguments) have precedence over those set with the --config option
    effective_config_dict = cli_config_dict
    effective_config_dict.update(config_dict)

    project = Project()
    if project.exists:
        parsim.error("A project already exists in directory '{0}'.".format(project.path))
    else:
        project.create(name=args.project_name, **effective_config_dict)


def config(argv=None):
    """Modify the settings for the current project."""
    description = "Modify the settings for the current project."
    config_parent = _get_config_parent_argparser()
    parser = ArgumentParser(parents=[config_parent], prog='psm config', description=description)

    if argv is None:
        return parser

    args = parser.parse_args(argv)
    config_dict = vars(args).copy()

    # Pop and process list with config key/value pairs from --config option.
    cli_config_option = config_dict.pop('config', None)
    cli_config_dict = _process_parameter_definition_options(parser, cli_config_option)

    # Explicit options (set by explicit cli arguments) have precedence over those set with the --config option
    effective_config_dict = cli_config_dict
    effective_config_dict.update(config_dict)

    project = Project()
    if project.exists:
        project.modify(**effective_config_dict)
    else:
        parsim.error('There is no parsim project in this directory')


def info(argv=None):
    """Print information about project, case or study."""
    description = "Print information about the specified target (case or study), or current project (no target)."
    target_parser = _get_target_parent_argparser()
    parser = ArgumentParser(parents=[target_parser], prog='psm info', description=description)

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    target = _process_target_argument(parser, args.target)
    print((target.info()))


def log(argv=None):
    """Print logged events of project, case or study."""
    description = "Print event log of specified target (case or study), or current project (no target)."
    target_parser = _get_target_parent_argparser()
    parser = ArgumentParser(parents=[target_parser], prog='psm log', description=description)

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    target = _process_target_argument(parser, args.target)
    print((target.log()))


def comment(argv=None):
    """Write user comment to the event log of project, case or study."""
    description = "Write user comment to the event log of the specified target (case or study), \
    or current project (no target)."
    target_parser = _get_target_parent_argparser()
    parser = ArgumentParser(parents=[target_parser], prog='psm comment', description=description)
    parser.add_argument('comment', type=str, help='user comment to add to the event log')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    target = _process_target_argument(parser, args.target)
    target.add_comment(args.comment)


def help(argv=None):
    """Show command help."""
    description = dedent("""Get help on a %(prog)s command.""")
    parser = ArgumentParser(prog='psm help', description=description)
    parser.add_argument('command', metavar='COMMAND',
                        type=str, choices=parsim.commands.all_commands)
    parser.add_argument('cmd_args', metavar='...', nargs=argparse.REMAINDER,
                        help='Command arguments')

    if argv is None:
        return parser

    args = parser.parse_args(argv)
    try:
        func = globals()[args.command]
        func(['--help']+args.cmd_args)
    except KeyError:
        parser.error('"%s" is not a psm command.' % args.cmd)


def version(argv=None):
    """Show current Parsim version."""
    description = "Print the parsim version."
    parser = ArgumentParser(prog='psm version',
                            description=description)

    if argv is None:
        return parser

    args = parser.parse_args(argv)
    print((parsim.__version__))


def run(argv=None):
    """Run a script in a case, or in all cases of a study."""
    description = "Execute script or executable in specified case, or in each case of a study."
    target_parser = _get_target_parent_argparser(mandatory=True)
    parser = ArgumentParser(parents=[target_parser], prog='psm run', description=description)
    parser.add_argument('--sub_dir', '-d', metavar='SUBDIR',
                        help='Case subdirectory to run in (otherwise the case root)')
    parser.add_argument('-o', metavar='OUTFILE', type=str, default=None,
                        help='Name of file for redirection of stdout')
    parser.add_argument('-e', metavar='ERRFILE', type=str, default=None,
                        help='Name of file for redirection of stderr')
    parser.add_argument('--shell', action='store_true',
                        help='Run executable through a shell (see Python subprocess module)')
    # parser.add_argument('target', type=str, metavar='TARGET',
    #                     help='Name of target, either a case or a study')
    parser.add_argument('executable', type=str, metavar='EXECUTABLE',
                        help='Name of executable, or path to it (named executable will be searched for)')
    parser.add_argument('exec_args', metavar='...', nargs=argparse.REMAINDER,
                        help='Additional arguments forwarded to the executable command-line')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    target = _process_target_argument(parser, args.target)
    kwargs = {'args': args.exec_args,
              'sub_dir': args.sub_dir,
              'out': args.o,
              'err': args.e,
              'shell': args.shell}
    target.run(args.executable, **kwargs)


def case(argv=None):
    """Create a new case from a model template."""
    description = "Create a new case, named from CASE_ID. \n\n"
    description += _study_case_common_description
    common_parent = _get_study_case_parent_argparser()
    parser = ArgumentParser(prog='psm case', description=description, parents=[common_parent])
    parser.add_argument('name', metavar='CASE_ID',
                        help='Name used to form the case directory name.')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    # Create parameter dict from parameter file
    param_dict, param_file = _process_parameter_file_option(args.parameters)

    # Create parameter dict from command-line definitions
    param_cli_dict = _process_parameter_definition_options(parser, args.define)

    # CLI parameter definitions override those in parameter file
    param_dict.update(param_cli_dict)

    case = Case(name=args.name)
    case.create(description=args.description, template=args.template, user_parameters=param_dict)

    logger.debug('Case: %s %s %s %s' % (args.template, param_file, args.name, case.path))


def study(argv=None):
    """Create a study with multiple cases from a model template."""
    description = "Create cases in a case study, as defined by the records in the CASELIST file. \n\n"
    description += _study_case_common_description
    description += '\n\nWhen a case study is created, case-specific values ' \
                   'for the parameters are given in ' \
                   'a CASELIST_FILE. Values in the caselist override values given on the command line.'
    common_parent = _get_study_case_parent_argparser()
    parser = ArgumentParser(prog='psm study', description=description, parents=[common_parent])
    parser.add_argument('--name', '-n', type=str, metavar='STUDY_NAME',
                        help='Name used to form the study directory name. By default, the study directory ' \
                             'is named from the CASELIST file name.')
    parser.add_argument('caselist', type=str, metavar='CASELIST',
                        help='Name of the caselist file, which defines case-specific parameter values.')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    # Create parameter dict from parameter file # -- Or should we send only file name to Case/Study?
    param_dict, param_file = _process_parameter_file_option(args.parameters)

    # Create parameter dict from command-line definitions
    param_cli_dict = _process_parameter_definition_options(parser, args.define)

    # CLI parameter definitions override those in parameter file
    param_dict.update(param_cli_dict)

    caselist_file = os.path.abspath(args.caselist)
    if not os.path.isfile(caselist_file):
        parsim.error('The specified caselist file "%s" is not found' % caselist_file)

    if args.name:
        study_name = args.name
    else:
        study_name = os.path.splitext(os.path.basename(caselist_file))[0]

    study = Study(name=study_name)
    study.create(description=args.description, template=args.template, caselist_file=caselist_file,
                 user_parameters=param_dict)

    logger.debug('Study: %s %s %s %s' % (args.template, param_file, caselist_file, study_name))


def doe(argv=None):
    """Create a study with multiple cases from a model template and a sampling scheme."""
    import parsim.doe
    sphinx = argv is None
    # Help on specific sampling scheme?
    if argv and len(argv)>1 and argv[0] in ['-h', '--help']:
        scheme = argv[1]
        if not scheme in parsim.doe.schemes:
            logger.error('Unknown sampling scheme (%s). See help message below.\n' % scheme)
        else:
            print(eval('parsim.doe.%s.help_message()' % scheme))
            return
    # Normal entry...
    description = "Create cases in a case study, based on a sampling scheme and parameter definitions. \n\n"
    description += _study_case_common_description+'\n'
    description += '\n' + dedent('''\
        When a DOE (Design Of Experiments) study is created, a sampling scheme is used to
        generate the caselist for the study. Parameters are defined in a parameter file,
        where statistical distributions are specified for the uncertain variables.
        Other parameters are given constant values.''')
    description += '\n'+parsim.doe.help_message(sphinx=sphinx)
    common_parent = _get_study_case_parent_argparser(doe=True)
    parser = ArgumentParser(prog='psm doe', description=description, parents=[common_parent],
                            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--name', '-n', type=str, metavar='STUDY_NAME',
                        help='Name used to form the study directory name. By default, the \n'\
                             'study directory is named from the PARAMETER_FILE file name.')
    parser.add_argument('parameters', type=str, metavar='PARAMETER_FILE',
                        help='Name of the parameter file (absolute path, or relative to the \n' \
                             'current directory) defining constant parameter values, as well \n'\
                             'as statistical distributions for uncertain parameters.')
    parser.add_argument('doe_scheme', metavar='DOE_SCHEME',
                        help='Valid DOE sampling scheme, for example "mc" (Monte Carlo) or\n'\
                             '"lhs" (Latin Hypercube Sampling.')
    parser.add_argument('doe_args', metavar='DOE_ARGS', nargs='*',
                        help='Valid arguments for the chosen DOE sampling scheme')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    # Create parameter dict from parameter file # -- Or should we send only file name to Case/Study?
    param_dict, distr_dict, param_file = _process_parameter_file_option(args.parameters, doe=True)

    # Create parameter dict from command-line definitions
    param_cli_dict = _process_parameter_definition_options(parser, args.define)

    # CLI parameter definitions override those in parameter file
    param_dict.update(param_cli_dict)

    # Process DOE arguments (into dict)
    doe_args = _process_doe_args(parser, args.doe_args)

    if args.name:
        study_name = args.name
    else:
        basename = os.path.basename(param_file)
        study_name, ext = os.path.splitext(basename)

    study = Study(name=study_name)
    study.create(description=args.description, template=args.template, doe_scheme=args.doe_scheme, doe_args=doe_args, user_parameters=param_dict,
                 distr_dict=distr_dict)

    logger.debug('Study: %s %s %s' % (args.template, param_file, study_name))


def dakota(argv=None):
    """Create a study and run a Dakota process with it."""
    # psm dakota [---] --restart STUDY
    import parsim.dakota
    description = "Create a study and start a Dakota process in it. \n\n"
    description += _study_case_common_description+'\n'
    description += '\n' + dedent('''\
        When a Dakota study is created, an empty study is created and control is then handed over to Dakota.
        Dakota uses a built-in Parsim analysis driver interface to create, run and evaluate successive cases
        needed for the Dakota simulation task. The Dakota simulation task is configured in the Dakota
        input file supplied on the command line.''')
    common_parent = _get_study_case_parent_argparser()
    parser = ArgumentParser(prog='psm dakota', description=description, parents=[common_parent])
    parser.add_argument('--name', '-n', type=str, metavar='STUDY_NAME',
                        help='Name used to form the study directory name. By default, the \n'\
                             'study directory is named from the DAKOTA_INPUT file name.')
    parser.add_argument('dakota_inp', metavar='DAKOTA_INPUT',
                        help='Path to Dakota input file.')
    parser.add_argument('executable', type=str, metavar='EXECUTABLE',
                        help='Name of executable, or path to it (named executable will be searched for)')
    parser.add_argument('--restart', nargs='?', default=argparse.SUPPRESS, const=-1, type=int, metavar='INDEX',
                        help='Perform a restart of failed Dakota run. An extra integer index argument \n'
                             'specifies which of successive restart files to use. "0" selects the \n'
                             'orginal run; the default is to use the latest restart file created.')
    parser.add_argument('--stop_restart', metavar='N', nargs=1, type=int, default=0,
                        help='Integer -stop_restart option sent to Dakota if restart requested.')
    parser.add_argument('--pre_run', action='store_true',
                        help='Only create study with cases according to Dakota method, using \n'
                             'the Dakota -pre_run option. No script execution.')

    if argv is None:
        return parser

    args = parser.parse_args(argv)
    args_dict = vars(args)

    # Create parameter dict from parameter file # -- Or should we send only file name to Case/Study?
    param_dict, param_file = _process_parameter_file_option(args.parameters)

    # Create parameter dict from command-line definitions
    param_cli_dict = _process_parameter_definition_options(parser, args.define)

    # CLI parameter definitions override those in parameter file
    param_dict.update(param_cli_dict)

    # Check Dakota input file path
    dakota_file = os.path.abspath(args.dakota_inp)
    if not os.path.isfile(dakota_file):
        parsim.error('The specified Dakota input file "%s" is not found' % dakota_file)

    if args.name:
        study_name = args.name
    else:
        basename = os.path.basename(dakota_file)
        study_name, ext = os.path.splitext(basename)

    restart = 'restart' in args_dict
    if args.stop_restart:
        stop_restart = args.stop_restart[0]
    else:
        stop_restart = 0

    study = Study(name=study_name)

    if restart:
        study.run_dakota(restart=True, restart_index=args.restart, stop_restart=stop_restart,
                         dakota_file=dakota_file, executable=args.executable)
    else:
        study.create(description=args.description, template=args.template, user_parameters=param_dict)
        study.run_dakota(dakota_file=dakota_file, executable=args.executable, pre_run=args.pre_run)


def collect(argv=None):
    """Collect results from all cases of a study and create text table."""
    description = "Collect results (json format) from all cases of a study and create text table."
    parser = ArgumentParser(prog='psm collect', description=description)
    parser.add_argument('study', type=str, metavar='STUDY',
                        help='Name of study')
    parser.add_argument('--input', '-i', metavar='INFILE', type=str, default=None,
                        help='Name of case file(s) containing results in json format. \
                         Multiple comma-delimited file names allowed. (Default: "results.json")')
    parser.add_argument('--output', '-o', metavar='OUTFILE', type=str, default=None,
                        help='Name of output file (default derived from name of input file)')
    parser.add_argument('--delim', metavar='CHAR', type=str, default=None,
                        help='Field delimeter (default is white-space with fixed column width)')

    if argv is None:
        return parser

    args = parser.parse_args(argv)

    if args.input:
        input_files = args.input.split(',')
    else:
        input_files = None

    project = Project()
    if project.exists:
        path, type = project.find_target_path_and_type(args.study)
        if type == 'study':
            study = Study(name=args.study, project=project)
            if not study.exists:
                parsim.error('Cannot find study on disk (bug?)')
        else:
            parsim.error('Cannot find a study from the given name (%s)' % args.study)
    else:
        parsim.error('There is no parsim project in this directory')

    kwargs = {'input': input_files,
              'output': args.output,
              'delim': args.delim}
    study.collect(**kwargs)
