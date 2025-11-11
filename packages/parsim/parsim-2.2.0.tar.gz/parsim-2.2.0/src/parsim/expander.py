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
import sys

try:
    import pyexpander.lib
except ImportError:
    import pyexpander3.lib

import parsim.core


def expandFileToFile(in_file, out_file, my_globals, simple_vars=False, include=None):
    with open(out_file, 'w') as fout:
        sys.stdout = fout
        try:
            pyexpander.lib.expandFile(in_file, external_definitions=my_globals, 
                                      allow_nobracket_vars=simple_vars, include_paths=include)
        except ImportError as e:
            raise parsim.core.ParsimExpanderError('Error parsing/expanding file %s: %s' % (in_file, e))
        finally:
            sys.stdout = sys.__stdout__
