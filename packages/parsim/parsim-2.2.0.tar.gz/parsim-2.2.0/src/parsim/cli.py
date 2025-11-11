#! /usr/bin/env python
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
Command-line interface to the parsim parameterized simulation management tool.
"""
import sys
import argparse
import textwrap

from parsim import commands
import parsim.loggers
from parsim.core import ParsimError


def psm_command():
    """
    Script entry-point (see setup.py) for psm main command.
    """
    # Generate subcommand descriptions from docstrings
    subcommand_description = 'Available subcommands:\n'
    for cmd in commands.all_commands:
        f = getattr(commands, cmd)
        if f:
            subcommand_description += "    %-10s %s\n" % (cmd, f.__doc__)

    description = textwrap.dedent("""\
        Parsim (psm) is a command-line tool for working with parameterized
        simulation models.

        Inside a project directory, Parsim creates individual cases, or studies
        of multiple cases, from model templates. A model template is a directory
        containing all input files and scripts needed to perform a simulation of
        a parameterized model. Text files (even scripts) can be parameterized
        by replacing numerical parameter values, or string keywords, by
        parameter names.

        When a case is created, the whole model template is replicated into a
        case directory, and parameterized files are processed so that actual
        values replaces parameter names.

        A model templates usually defines default values for all its parameters
        in a specific parameter file. When creating a case or a study, custom
        parameter values can be defined on the command line, in a separate
        parameter file, or in a caselist defining multiple cases of study.""")

    description += '\n\n' + subcommand_description

    epilog = textwrap.dedent("""\
        Run "psm help <command>" to see detailed help for each subcommand.""")

    parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--debug', '--dbg', '-d', action='store_true',
                        help='Force "DEBUG" log-level, to help bug tracing')
    parser.add_argument('command', type=str, help='Parsim (psm) subcommand (see above)')
    parser.add_argument('command_args', nargs=argparse.REMAINDER, help='subcommand arguments')

    # todo: Argparse epilog: additional help topics: Model templates, Study and caselists, parameter files, Example usage
    args = parser.parse_args()

    # Forced debug log-level?
    if args.debug:
        parsim.loggers.force_debug_log_level()

    # Check if valid subcommand
    if not args.command in commands.all_commands:
        parser.print_help()
        parser.error('%s is not a valid psm subcommand. See help.' % args.command)

    try:
        subcommand = getattr(commands, args.command)
    except AttributeError:
        parser.error('Missing implementation of %s command' % args.command)
        return 1

    try:
        subcommand(args.command_args)
    except ParsimError as e:
        if args.debug:
            raise
        else:
            if not e.handled:
                parsim.loggers.logger.error('%s' % e)
        return 1

    return 0


if __name__ == "__main__":
    status = psm_command()
    sys.exit(status)
