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
import os.path
import shutil

from parsim.loggers import logger
from parsim.core import Project, Study, Case, ParsimError


def key_value(line, type=None):
    """
    Parse key-value pair from line read from Dakota input file.

    Arguments:
        line (str): Text line to parse.
        type (str): Optional string {'int', 'float', 'str'} to indicate expected value type.
        Otherwise attempts to do the right thing anyway.

    Returns:
        (str, value): Tuple of key and value (key is string, but value could be int, float or str).
    """
    fields = line.split()
    assert len(fields) == 2
    key = fields[1]
    if type == 'int':
        value = int(fields[0])
    elif type == 'float':
        value = float(fields[0])
    elif type == 'str':
        value = fields[0]
    else:
        try:
            value = float(fields[0])
        except ValueError:
            value = fields[0]
        else:
            value = eval(fields[0])
    return key, value


class DakotaVariables:
    """
    Class of Dakota variables file.

    Arguments:
        filepath (str): Path to input file to read.
    """
    def __init__(self, filepath):
        self.eval_id = None
        # Read dakota variables.in
        with open(filepath) as f:
            lines = f.readlines()
        # Process lines
        i = 0
        while i<len(lines):
            section, n = key_value(lines[i])
            if section == 'variables':
                pairs = [ key_value(line) for line in lines[i+1:i+1+n] ]
                self.var_dict = dict(pairs)
                self.variables = [ k for k, v in pairs ]
                self.var_values = [ v for k, v in pairs ]
                i += 1+n
            elif section == 'functions':
                pairs = [ key_value(line, type='int') for line in lines[i+1:i+1+n] ]
                self.asv_dict = dict(pairs)
                self.functions = [ k for k, v in pairs ]
                i += 1+n
            elif section == 'derivative_variables':
                self.derivatives = [ key_value(line, type='int') for line in lines[i+1:i+1+n] ]
                i += 1+n
            elif section == 'analysis_components':
                self.analysis_components = { key_value(line) for line in lines[i+1:i+1+n] }
                i += 1+n
            elif section == 'eval_id':
                self.eval_id = str(n)
                i += 1


def psm_dakota_driver():
    """
    Analysis driver for Dakota fork interface under parsim.
    """

    # Dakota interface files as arguments
    variables_in = sys.argv[1]
    results_out = sys.argv[2]

    cwd = os.getcwd()

    # Open Project and Study
    project = Project(path=os.path.pardir)
    study = Study(path=cwd, project=project)
    template_path = study.get('template_path')
    user_parameters = study.get('user_param_dict')

    # Read Dakota variables file
    dakota = DakotaVariables(variables_in)

    # Update study with Dakota variables info
    if not study.get('dakota_variables'):
        study.set('dakota_variables', dakota.variables)
        study.save()
        # Write header to caselist, as this is first case of the Study
        with open('dakota.caselist', 'w') as f:
            f.write('CASENAME %s\n' % ' '.join(dakota.variables))

    # Create new case
    if study.get('dakota_run'):
        case_name = dakota.eval_id+'-'+str(study.get('dakota_run'))
    else:
        case_name = dakota.eval_id
    case = Case(name=case_name, project=project, study=study)
    case.create(template=template_path, user_parameters=user_parameters, caselist_parameters=dakota.var_dict)

    # Copy Dakota variables file to case
    shutil.copy(variables_in, case.path)

    # Run simulation executable in case
    case.run(study.get('dakota_simulation_exe'))

    # Copy Dakota results
    shutil.copy(os.path.join(case.path, results_out), cwd)

    # Append case data to dakota caselist
    with open('dakota.caselist', 'a') as f:
        f.write('%s %s\n' % (dakota.eval_id, ' '.join([ str(v) for v in dakota.var_values])))

    return 0


if __name__ == "__main__":
    status = psm_dakota_driver()
    sys.exit(status)
