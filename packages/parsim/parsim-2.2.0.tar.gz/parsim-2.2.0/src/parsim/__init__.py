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
'''
The parsim package contains all code used to implement the parsim tool.

The functionality is implemented in a number of submodules.
'''

__all__ = ['commands', 'core', 'loggers', 'expander', 'dakota', 'doe', 'cli']
__version__ = "2.2"
__release__ = __version__+".0"

import sys

_syspath_additions = []
'''List of paths added with the add_to_syspath() function.'''


def add_to_syspath(*paths):
    """Add (insert) a list of paths to sys.path."""
    for p in paths:
        if not p in _syspath_additions:
            sys.path.insert(0,p)
            _syspath_additions.insert(0,p)


def error(msg):
    """
    Print error message and exit (1).

    Called to interrupt execution, e.g. when a parsim-related exception is handled.
    """
    sys.exit("ParsimError: %s" % msg)

