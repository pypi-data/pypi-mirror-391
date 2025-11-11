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
Main parsim classes and utility functions.
"""
import json
import textwrap
import os
import sys
import shutil
import logging
import re
import importlib
import datetime
import subprocess
import shlex

import pandas as pd

import parsim
import parsim.expander
import parsim.loggers
from parsim.loggers import logger, TIMESTAMP_FORMAT


DEFAULT_PARSIM_DIRECTORY = '.psm'
DEFAULT_DATA_FILE = dict(project='project', case='case', study='study')

DEFAULT_PROJECT_CONFIG = {
    'default_executable': None,
    'python_exe': 'python',
    'dakota_exe': 'dakota',
    'template_root': 'modelTemplates',
    'default_template': 'default',
    'default_parameter_file': 'default.parameters',
    'log_level': 'info',
    'psm_ignore_file': '.psmignore',
    'psm_ignore_patterns': ['default.parameters', '.psm*', '.git*', '.svn*', '*~'],
    'case_prefix': 'case_',
    'study_prefix': 'study_',
    'default_results_file': 'results.json'
}
"""
Default config settings for Parsim projects.
"""

def _remove_left_margin(s):  # replace this by textwrap.dedent?
    lines = s.strip().split('\n')
    return "\n".join(line.strip() for line in lines)


def find_file_path(filename, *places):
    """
    Search for filename in list of possible paths and return full path to the file.

    Args:
        filename (str): Name of file to search for.
        *places (str): Variable length argument list of paths to search.

    Returns:
        str: Full path to file.
    """
    for loc in places:
        path = os.path.join(loc, filename)
        logger.debug('Looking for %s' % path)
        if os.path.isfile(path):
            break
    else:
        path = None
    return path


def parse_parameter_file(file_path, get_comments=False, doe=False):
    """
    Parse parameter file and return dict with parameters (and perhaps comments).

    If called with the `doe` flag set, tries to interpret un-resolved parameter definitions
    as distributions.

    Args:
        file_path (str): Path to parameter file.
        get_comments (bool): If True, return also comments at end of lines.
        doe (bool): If True, try to interpret un-resolved parameter definitions as
            distributions of uncertain parameters.

    Returns: Returns dict of parameter values. If `doe` is True, return tuple with dict of
    parameter distributions as second item. If `get_comments` is True, returns tuple with
    dict of comments as last item.
    """
    # Original: '(\w+):?\s*({.+?}|".+?"|\'.+?\'|.+?)[;#](.+)?|(\w+):?\s*(.+)'
    param_pattern = r'(\w+)\s*[=:]?\s*({.+?}|".+?"|\'.+?\'|.+?)\s*[;#]\s*(.+)?|(\w+)\s*[:=]?\s*(.+)'
    params = {}
    comments = {}
    distr = {}
    try:
        with open(file_path, 'r') as f:
            for rawline in f:
                line = rawline.strip()
                # Avoid processing comment lines (starts with #, * or ;)
                if len(line) > 0 and not (line[0] in '#*;'):
                    m = re.match(param_pattern, line)
                    if m:
                        if m.group(1):
                            par_name, par_value, par_comment = m.groups()[0:3]
                            if not par_comment:
                                par_comment = ' '
                        else:
                            par_name, par_value = m.groups()[3:5]
                            par_comment = None
                        par_name = par_name.strip()
                        par_value = par_value.strip()
                        # Strip values from recognized string delimiters {}, "" and ''
                        if par_value[0] in r'{\"\'':
                            par_value = par_value[1:-1]
                            params[par_name] = par_value
                        else:
                            try:
                                # As in pyexpander library, execute expressions in a namespace, to retain variable types
                                my_space = {}
                                exec('%s=%s' % (par_name, par_value), my_space)
                                params[par_name] = my_space.get(par_name)  # To avoid extra entries added by Python
                            except NameError:
                                if doe and re.match(r'(\w+)\(.+\)', par_value):
                                    # Interpret non-resolved expression as distribution, since it fits pattern
                                    distr[par_name] = par_value
                                else:
                                    raise
                        if par_comment:
                            comments[par_name] = par_comment
                    else:
                        raise ParsimError('Invalid parameter definition in line: "%s"' % line)
    except FileNotFoundError:
        raise ParsimError('Parameter file not found (%s)' % file_path)
    if doe:
        if get_comments:
            return params, distr, comments
        else:
            return params, distr
    else:
        if get_comments:
            return params, comments
        else:
            return params


def parse_caselist_file(file_name):
    """
    Parse a caselist file (or Dakota annotated file) and return case definitions.

    Returns case definitions as a list of tuples.
    The first tuple element is the case name, and the second is a dictionary of parameters.

    Args:
        file_name (str): Path to input file.
        
    Returns:
        list((str, dict)): Case definitions as a list of tuples. 
        First tuple element is case name and the second a dict of parameters.
    """
    cases = []
    with open(file_name, 'r') as f:
        # Skip initial comment lines, if any
        while True:
            line = f.readline()
            if not line[0] in '#/;':
                break
        # Get parameter keys from header line
        # Note for Dakota: A leading "%" is munched by this re pattern, leaving an empty first element...
        fields = re.split(r'\W+', line)
        if fields[0].upper() == 'CASENAME':
            # Parsim CASELIST format
            dakota = False
            start_col = 1
        elif fields[1] == 'eval_id':
            # Dakota standard annotated format, assuming first parameter in 3rd column
            dakota = True
            fields = fields[1:]
            start_col = 2
        else:
            raise ParsimError('Error parsing caselist file. '
                              + 'Invalid first line: %s' % line)
        # Handle possible empty string in last elem
        if fields[-1]:
            par_names = fields[start_col:]
        else:
            par_names = fields[start_col:-1]
        npar = len(par_names)
        logger.debug('Caselist parameters: %s' % repr(par_names))
        # Process case records in rest of file
        while True:
            line = f.readline()
            if not line:
                break
            if line[0] in '#/;':
                return
            fields = re.findall(r'(".+?"|\'.+?\'|{.+?}|\S+)', line)
            logger.debug('Caselist record has fields: %s' % repr(fields))
            if dakota:
                # Use number of value columns to determine number of parameters...
                npar = len(fields) - 2
                par_names = par_names[:npar]
            elif len(fields) != start_col + npar:
                raise ParsimError('Error parsing caselist file. '
                                  + 'Wrong number of fields in line: %s'
                                  % line)
            case_id = fields[0]
            case_dict = {}
            for i, value in enumerate(fields[start_col:]):
                param = par_names[i]
                if value[0] in r'{\"\'':
                    # String value
                    case_dict[param] = value[1:-1]
                else:
                    # As in pyexpander library, execute expressions in a namespace, to retain variable types
                    my_space = {}
                    exec ('%s=%s' % (param, value), my_space)
                    case_dict[param] = my_space.get(param)  # To avoid extra entries added by Python
            cases.append((case_id, case_dict))
    return cases


def create_caselist_file(output_path, case_names, column_dict=None, case_dicts=None, parameter_names=None, csv=None):
    """
    Create and write a case list to a specified file (`output_path`).

    Case names are supplied in a separate list (`case_names`). Parameter names may optionally be supplied in
    a list (`parameter_names`), to control the order of the parameter columns, or to output only a subset of
    the available parameters; default is to output all available parameters, in arbitrary order.

    Case parameter data are specified in one of two ways: Either `column_dict` is a dict from parameter name to
    list (vector) of values (one value per case), or `case_dicts` is a list of dicts from parameter name to value
    (one dict per case).

    Args:
        output_path (str): Path to output file.
        case_names (list): List of case names (output in first column, "CASENAME")
        column_dict (dict): Dict from parameter name to list of values (one value per case).
        case_dicts (list): List of dicts from parameter name to value (one dict per case).
            Arguments column_dict and case_dicts are mutually exclusive.
        parameter_names (:obj:`list`, optional): List of parameter names to output.
        csv (:obj:`bool`, optional): Flag to request output in CSV format.
        
            Default (False) is to output in fixed-width whitespace-separated columns. 
            If `csv` is one of the characters ",;%|#", this will be used as separator. 
            If `csv` is any other boolean "True" value, ";" is used as separator.
    """
    # Check input arguments
    if column_dict and case_dicts:
        raise ValueError('Only one of the arguments column_dict or case_dicts should be used')
    if not (column_dict or case_dicts):
        raise ValueError('Parameter data missing; column_dict or case_dicts must be specified')
    if column_dict:
        assert isinstance(column_dict, dict)
    else:
        assert isinstance(case_dicts, list)
        assert isinstance(case_dicts[0], dict)

    if csv:
        if csv in ',;%|#':
            delim = csv[0]
        else:
            delim = ';'

    column_keys = ['CASENAME']
    if isinstance(parameter_names, list):
        column_keys.extend(parameter_names)
    else:
        if column_dict:
            column_keys.extend(list(column_dict.keys()))
        else:
            column_keys.extend(list(case_dicts[0].keys()))

    # Create data structures containing 'CASENAME'
    if column_dict:
        # dict of columns
        caselist_columns = {'CASENAME': case_names}
        caselist_columns.update({name: [repr(x) for x in vect] for name, vect in column_dict.items()})
    else:
        # list of rows, one dict per row (copy needed...)
        caselist_rows = [dict([(p, repr(v)) for p, v in d.items()], CASENAME=name) for d, name in
                         zip(case_dicts, case_names)]
        # Check for missing entries...
        column_key_set = set(column_keys)
        for row_dict in caselist_rows:
            missing = column_key_set - row_dict.keys()
            if missing:
                raise ParsimError('Failure writing caselist file: Case "%s" has missing column keys: %s'
                                  % (row_dict['CASENAME'], missing))

    # Compute max width of each column (=1 for csv)
    maxlen = dict.fromkeys(column_keys, 1)
    if not csv:
        for col in column_keys:
            if column_dict:
                maxlen[col] = max([len(x) for x in caselist_columns[col]])
            else:
                maxlen[col] = max([len(x[col]) for x in caselist_rows])
            maxlen[col] = max(maxlen[col], len(col))

    # Create output fromat strings
    if csv:
        col_header = delim.join(column_keys) + '\n'
        row_fmt = delim.join(['%%(%s)s' % x for x in column_keys]) + '\n'
    else:
        col_header = '  '.join([x.ljust(maxlen[x]) for x in column_keys]) + '\n'
        row_fmt = '  '.join(['%%(%s)-%ds' % (x, maxlen[x]) for x in column_keys]) + '\n'

    with open(output_path, 'w') as f:
        f.write(col_header)
        if column_dict:
            for i in range(len(case_names)):
                f.write(row_fmt % {x: caselist_columns[x][i] for x in column_keys})
        else:
            f.writelines([row_fmt % d for d in caselist_rows])


def create_parameter_file(output_path, parameters, parameter_names=None):
    """
    Create and write a parameter file to a specified file (`output_path`).

    Parameter definitions are specified as dictionary (`parameters`).

    Parameter names may optionally be supplied in a list (`parameter_names`), to control the order
    of the parameters in the output, or to output only a subset of the available parameters; default
    is to output all available parameters, in arbitrary order.

    Args:
        output_path (str): Path to output file.
        parameters (dict): Dictionary with parameter/value pairs.
        parameter_names (list): List of parameter names, to control order of parameters in output.
    """
    assert isinstance(parameters, dict)

    if parameter_names:
        assert isinstance(parameter_names, list)
    else:
        parameter_names = list(parameters.keys())

    if parameter_names:
        maxlen = max([len(x) for x in parameter_names])
    else:
        maxlen = 15

    fmt = '%%-%ds : %%s\n' % maxlen

    with open(output_path, 'w') as f:
        for name, value in parameters.items():
            if name in parameter_names:
                f.write(fmt % (name, repr(value)))


class ParsimError(Exception):
    """
    Baseclass for Parsim exceptions.
    
    The keyword argument `handled` may be set, if the the error has already been handled,
    in the sense that information has been given to the user. This is to avoid duplicate output
    if the exception is captured and handled by outer handler.
    
    Arguments:
        handled (bool): Set to true if exception already reported to user. Defaults to False.
        
    Attributes:
        handled (bool): Flag to show if exception already reported to user.
    """

    def __init__(self, *args, **kwargs):
        self.handled = kwargs.pop('handled', False)
        super().__init__(*args, **kwargs)


class ParsimCaseError(ParsimError):
    """
    Error in operation on case, which may affect only this particular case.

    Raising this exception, rather than `ParsimError`, would allow an outer exception handler
    to continue. For example, the `Study.collect()` method would like to process all cases of the
    study, even if the result file is missing for a particular case (raising `ParsimCaseError`).
    Other cases may still be ok!
    """
    pass


class ParsimExpanderError(ParsimError):
    """Exception raised inside `pyExpander` library."""
    pass


class ParsimObject:
    """
    Baseclass for all Parsim objects (projects, cases and studies).
    
    A `ParsimObject` is uniquely identified by its path on disk. Unless the path is
    given with the `path` argument, a path can be constructed from an object name.
    
    If the object exists on disk, its data will be automatically loaded from the 
    object data file (with the `load` method). Otherwise an empty object is created by
    the constructor, but its data will have to be initialized by a separate call to 
    the `create` method.
    
    Args:
        path (str): Path to object directory. Mandatory, unless the `path` attribute 
            has already been set by the subclass constructor before calling the 
            baseclass constructor.
        name (str): Name of object. Used for `name` value in `data` dict attribute, if given.
        registry (list): List of names of attributes to store on disk (by default,
            only the `data` and `registry` attributes are stored.

    Attributes:
        path (str): Path to object directory.
        _parent_object_path (str): Path to parent object (`Study` or `Project`).
        _parent_object_type (str): Type of parent object
        _psm_path (str): Path to object storage subdirectory (inside object directory).
        _data_file (str): Name of data file for object data storage.
        _logger (logging.Logger): Logger instance of this object.
        _logger_name (str): Name of object logger instance.
        _logger_file (str): File used by logger file handler.
        exists (bool): Flag is True is object exists on disk.
        open (bool): Flag is True if logger file is open and/or (?) object data not saved.
        registry (list): List of object attributes to save to and load from disk storage.
        data (dict): Dict for storage of object data.
    """
    _type = 'generic'
    """Type object, derived from baseclass."""
    _valid_name_pattern = r'(?P<project>\w+[\w\- ]*)'
    """regexp pattern for validation of object names."""
    _ok_to_create_in_existing_path = False
    """Can the object be created in an existing directory path, or only as a new subdirectory?"""

    def __init__(self, name=None, path=None, **kwargs):
        # Initialize settings dictionary (self.data)
        self.data = {}
        if name:
            self.set('name', self._validated_name(name))
        if path:
            self.path = path
        # Make sure the object has a valid path now!
        assert isinstance(self.path, str), 'ParsimObject should have a path set at this point (self.path missing)'
        self._parent_object_path, self._parent_object_type = self.find_parent_object_path()
        logger.debug('myself: %s, %s' % (self.path, self._type))
        logger.debug('parent_object: %s, %s' % (self._parent_object_path, self._parent_object_type))
        # Object storage on disk
        self._data_file = self._get_data_file_path(self.path)
        self._psm_path = os.path.dirname(self._data_file)
        # Registry for instance data structures to store on disk (self._data_file)
        self.registry = ['registry', 'data']
        registry = kwargs.pop('registry', None)
        if registry:
            assert isinstance(registry, list)
            self.registry.extend(registry)
        # Empty logger variables
        self._logger = None
        self._logger_name = None
        self._logger_file = None
        # Check if object exists already, or if it's new
        self.exists = os.path.isfile(self._data_file)
        self.open = False
        # Load an existing object from disk
        if self.exists:
            self.load()
            self._init_logger()

    def create(self, name=None, description=None, noSave=False, onlySave=False):
        """
        Create new object.
        
        `ParsimObject` creation is made separate from the object instantiation. The object
        is complete only when this creation step is done, and this is when the object is
        written to disk.

        Args:
            name (str): Sets `name` value in dict attribute `data`, if provided.
            description (str): Optional description of the object. 
        """
        logger.debug('ParsimObject.create: type=%s path=%s' % (self._type, self.path))
        if name:
            self.set('name', self._validated_name(name))
        if description:
            self.set('description', description)
        else:
            if not self.get('description'):
                self.set('description', '')
        self.set('parsim_version', parsim.__release__)
        date = datetime.datetime.today()
        self.set('creation_date', date.strftime(TIMESTAMP_FORMAT))
        if self.exists or os.path.exists(self._data_file):
            raise ParsimError('%s already exists. Abort create.' % self._type)
        if not self._ok_to_create_in_existing_path:
            if os.path.exists(self.path):
                raise ParsimError('%s path already exists: %s. Abort create.' % (self._type, self.path))
            else:
                os.mkdir(self.path)
        if not os.path.exists(self._psm_path):
            os.mkdir(self._psm_path)
        self._init_logger()
        # Save complete object to disk
        self.save()

    def load(self):
        """
        Loads object data from an object data file on disk. 
        
        The object must, of course, already exist on disk.
        """
        if not self.exists:
            raise ValueError('No %s exists, cannot load...' % self._type)
        with open(self._data_file, 'r') as f:
            data = json.load(f)
        for key, value in data.items():
            if key == 'data':
                setattr(self, key, value)
            elif isinstance(value, dict) and "type" in value:
                parts = str(value["type"]).split(
                    ".")  # make sure not unicode, see http://stackoverflow.com/questions/1971356/haystack-whoosh-index-generation-error/2683624#2683624
                module_name = ".".join(parts[:-1])
                class_name = parts[-1]
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                args = {}
                for k, v in value.items():
                    if k != 'type':
                        args[str(k)] = v  # need to use str() as json module uses all unicode
                setattr(self, key, cls(**args))
            else:
                setattr(self, key, value)

    def close(self):
        """
        Closes the object.
        
        Closing the object means its data is written to the object data file
        on disk and the object logger is closed.
        """
        try:
            self.save()
        except:
            print("ParsimObject.close(): Error when saving object")
            raise
        self._close_logger_file()
        self.open = False

    def _init_logger(self):
        """
        initialize the object logger and starts logging.
        """
        assert self.get('name')
        assert os.path.exists(self._psm_path)
        # Construct logger name for this object
        if self._type == 'project':
            self._logger_name = 'parsim.project'
        elif self._type == 'study':
            self._logger_name = 'parsim.project.study_' + self.get('name')
        else: # case
            if self.study:
                self._logger_name = 'parsim.project.study_' + self.study.get('name') + '.case_' + self.get('name')
            else:
                self._logger_name = 'parsim.project.case_' + self.get('name')
        self._logger = logging.getLogger(self._logger_name)
        self._logger_file = os.path.join(self._psm_path, 'log')
        h = logging.FileHandler(self._logger_file)
        h.setFormatter(parsim.loggers.ParsimLogFormatter(fmt='%(asctime)s - %(levelname)s: %(message)s',
                                                         fmt_child='%(asctime)s - %(levelname)s: [%(child_path)s] %(message_digest)s',
                                                         datefmt=parsim.loggers.TIMESTAMP_FORMAT))
        h.addFilter(parsim.loggers.ParsimLogFilter(self._logger_name, scope=1))
        self._logger.addHandler(h)
        self._logger_fileHandler = h
        self.open = True
        return

    def _close_logger_file(self):
        """
        Close the object logger.
        """
        try:
            self._logger_fileHandler.close()
        except NameError:
            return False
        return True

    def save(self, silent=False):
        """
        Save the object to its object data file on disk.
        
        The object attributes to save are those named in the object's `registry` attribute.
        """
        state = {}
        for name in self.registry:
            try:
                attr = getattr(self, name)
            except:
                # Default value for unrecognised parameters
                attr = None
            if hasattr(attr, "__getstate__") and attr.__getstate__(): # Only if object has __getstate__ method which does not return "None"
                state[name] = {'type': attr.__class__.__module__ + "." + attr.__class__.__name__}
                for key, value in attr.__getstate__().items():
                    state[name][key] = value
            else:
                state[name] = attr
        with open(self._data_file, 'w') as f:  # should check if file exists?
            json.dump(state, f, indent=2)
        if not self.exists:
            # First time object is saved, so it must be new
            self.exists = True
            if not silent:
                self._logger.info('Parsim %s "%s" successfully created' % (self._type, self.get('name')))

    def delete(self, force=False, logging=True):
        """
        Delete the object's directory from disk, including all its contents.

        Args:
            force (bool): Forces deletion without interactive query, also if the object
                actually exists and seems to correctly created. Default is to ask for
                confirmation if the the object's `exist` attribute is True.
            logging (bool): Argument currently not used... 

        Returns:
            bool: Returns True if delete is successful. Returns False if the object's
            directory path does not exist, or if an error occurred.
        """
        # Quit if path does not exist
        if not os.path.exists(self.path):
            return False
        # Force if incomplete create operation
        force = force or (not self.exists)
        name = self.get('name')
        # Check force flag, console confirmation if False
        if not force:
            prompt = '-- Are you SURE you want to delete the %s named %s? (no/[yes]' % (self._type, name)
            inp = input(prompt)
            if not inp.lower() in ['y', 'yes']:
                return False
        # Remove from disk
        try:
            self.close()
            shutil.rmtree(self.path)
        except (OSError, WindowsError) as e:
            print('Fatal error when deleting %s "%s": %s.\nABORTED. You will have to clean up manually...'
                  % (self._type, name, e))
            return False
        return True

    def info(self):
        """
        Create text with basic object information.
        
        Returns:
            str: Line-wrapped text with object information.
        """
        # ToDo: Make generic, for example take msg string from overriding method
        template = """\
            Project name        : %(name)s
            Parsim version      : %(parsim_version)s"""
        return textwrap.dedent(template % self.data)

    def log(self):
        """
        Return contents of event log.
        
        Returns:
            str: Contents of logger file.
        """
        if not self.exists:
            return 'Object does not exists on disk -- no log data available'
        with open(self._logger_file) as f:
            logtext = ''.join(f.readlines())
        return logtext

    def get(self, key):
        """
        Get a value from the object data attribute dictionary.
        
        Args:
            key (str): Dictionary key. 

        Returns:
            Dictionary value.
        """
        return self.data.get(key)

    def set(self, key, value):
        """
        Set a key-value pair in the object `data` attribute dictionary.
        
        Args:
            key (str): Dictionary key. 
            value: Dictionary value.
        """
        self.data[key] = value

    def _validated_name(self, name):
        """
        Check if the provided name is a valid `ParsimObject` name.
        
        Args:
            name (str): Text string to check.

        Returns:
            bool: True if the provided name is valid; False otherwise.
        """
        if re.match(ParsimObject._valid_name_pattern, name):
            return name
        else:
            raise ValueError("Invalid %s name. Names may only contain letters, numbers, spaces and hyphens" % self._type)

    def add_comment(self, msg):
        """
        Add user comment to object event log.
        
        Args:
            msg (str): Comment text string for event log.
        """
        self._logger.log(parsim.loggers.USER_LOG_LEVEL, msg)

    @classmethod
    def _get_data_file_path(cls, path):
        """
        Get path to object's data file on disk.
        
        Args:
            path (str): Path to object directory on disk. 

        Returns:
            str: Path to object's data file.
        """
        return os.path.join(path, DEFAULT_PARSIM_DIRECTORY, DEFAULT_DATA_FILE[cls._type])

    def find_parent_object_path(self, p=None, project=False):
        """
        Find path to an object's parent object, if any.
        
        Most `ParsimObjects` live in the directory of a parent object. For example,
        a Study lives in a Project directory, and a Case lives either in a Project
        directory, or it is part of a Study.
        
        This function will move back up through the directory tree, until a parent
        `ParsimObject` is found. The `project` argument can be set if we want to find the
        Parsim Project.
        
        Args:
            p (str): Optional path to the child object, whose parent we seek. By default,
                the present object is the child.
            project: If True, the function will look for the Project to which the object belongs.

        Returns:
            (str, str): If a parent is found, returns tuple of `path` of parent object and
            its `type` attribute. If not no parent is found, returns ``(None, None)``.
        """
        if not p:
            p = os.path.dirname(self.path)
        exists = True
        object_type = None
        while True:
            psm_path = os.path.join(p, DEFAULT_PARSIM_DIRECTORY)
            if os.path.isdir(psm_path):
                files = os.listdir(psm_path)
                object_stores = {'project', 'study', 'case'} & set(files)
                if len(object_stores) > 1:
                    raise ParsimError('Corrupt parsim object directory (%s): '
                                      'Found more than one object store: %s', (psm_path, list(object_stores)))
                elif len(object_stores) < 1:
                    raise ParsimError('Corrupt parsim object directory (%s): '
                                      'Object store is missing', psm_path)
                object_type = object_stores.pop()
                if project:
                    exists = object_type == 'project'
                else:
                    exists = True
                if exists:
                    break
            oldp, p = p, os.path.dirname(p)
            if p == oldp:
                object_type = None
                exists = False
                break
        if exists:
            return (p, object_type)
        else:
            return (None, None)


class Project(ParsimObject):
    """
    Parsim Project class.
    
    A `Project` instance holds information about the Project and the project directory.
    The project directory is the root directory for all cases and studies of the project.
    
    The constructor extends the baseclass constructor.
    
    Args:
        path (str): Path to project directory. If not provided, the current directory is used.
        
    Attributes:
        config (dict): Dictionary containing configuration settings for the project.
    """
    _type = 'project'
    _ok_to_create_in_existing_path = True
    """A Project is usually created in an existing directory..."""

    def __init__(self, name=None, path=None, **kwargs):
        if not path:
            p = os.getcwd()
        else:
            p = os.path.abspath(path)
        if not os.path.isdir(p):
            raise ParsimError('Given directory path does not exist: %s' % p)
        # Look for existing project
        existing_path, t = self.find_parent_object_path(p, project=True)
        if existing_path:
            p = existing_path
        self.config = {}
        super().__init__(name=name, path=p, registry=['config'])

    def load(self):
        """
        Loads object data from object data file on disk.

        Extends baseclass `ParsimObject` method by setting a log level according to
        Project config settings.
        """
        super().load()
        if self.config.get('log_level'):
            parsim.loggers.set_log_level(self.config.get('log_level'))

    def create(self, name=None, description=None, **config_dict):
        """
        Create new `Project` object.
        
        Extends baseclass `ParsimObject` method. Sets description, if given as keyword argument.
        The `config` dict attribute is initialized with values from `DEFAULT_PROJECT_CONFIG`, and then
        modified by remaining keyword arguments (in `config_dict`). Creates directories for template 
        root and default template, if missing.
        
        Args:
            name (str): Mandatory name of project.
            description (str): Description of project
            **config_dict: Dict of keyword arguments.
        """
        self.config.update(DEFAULT_PROJECT_CONFIG)
        self.config.update(config_dict)
        # Template directory settings
        template_root = self.config.get('template_root')
        default_template = self.config.get('default_template')
        if not os.path.exists(template_root):
            os.mkdir(template_root)
        if not os.path.exists(os.path.join(template_root, default_template)):
            os.mkdir(os.path.join(template_root, default_template))
        super().create(name=name, description=description)

    def delete(self, force=False, logging=True):
        """
        Delete the object's directory from disk, including all its contents.

        Projects can only be deleted manually -- ABORT...

        Args:
            force (bool): Forces deletion without interactive query, also if the object
                actually exists and seems to correctly created. Default is to ask for
                confirmation if the the object's `exist` attribute is True.
            logging (bool): Argument currently not used...

        Returns:
            bool: Returns True if delete is successful. Returns False if the object's
            directory path does not exist, if the object is a `ParsimProject`, or if
            an error occurred.
        """
        print('-- Deletion of Project is not supported. Abort.')
        return False

    def modify(self, **config_dict):
        """
        Modify project config settings.
        
        Keyword arguments will update project `config` attribute.
        
        Args:
            **config_dict: Dict of keyword arguments.
        """
        if not self.exists:
            raise ValueError('No %s exists, cannot modify...' % self.type)
        self.config.update(config_dict)
        self.save()

    def info(self):
        """
        Show some basic information about the project.
        """
        if not self.exists:
            return 'Project does not exists on disk -- no info available'
        template = """\
            Project name        : %(name)s
            Creation date       : %(creation_date)s
            Description         : %(description)s
            Parsim version      : %(parsim_version)s
            -------------------------------------------------------------
            Project config settings
            -------------------------------------------------------------
            """
        info_str = textwrap.dedent(template % self.data)
        for key, value in self.config.items():
            info_str += '%-25s : %s\n' % (key, str(value))
        return info_str

    def get_template_path(self, template):
        """
        Search several locations for a valid model template.

        Several locations are searched, in the following order:
        
            1. Current directory (only if `template` name is provided)
            2. Project template directory
            3. Default template, inside project template directory
            
        Args:
            template (str): Name of model template
            
        Returns:
            str: Path to model template directory.
        """
        template_dir = None
        # Look in current directory, if template name provided
        if template:
            t = os.path.abspath(template)
            if os.path.isdir(t):
                template_dir = t
                logger.info('Found template as absolute or relative path: %s' % t)
        if not template_dir:
            # Look in project template directory, if it exists
            template_root = self.config.get("template_root")
            if template_root:
                if not os.path.isabs(template_root):
                    # Assuming path given relative to project directory...
                    template_root = os.path.join(self.path, template_root)
                if template:
                    # Look for named template
                    t = os.path.abspath(os.path.join(template_root, template))
                    if os.path.isdir(t):
                        template_dir = t
                        logger.info('Found template in project template directory: %s' % t)
                else:
                    # Look for default template
                    default_template = self.config.get('default_template')
                    if default_template:
                        t = os.path.abspath(os.path.join(template_root, default_template))
                        if os.path.isdir(t):
                            template_dir = t
                            logger.info('Found default template: %s' % t)
                    else:
                        logger.warning('Project has no default template')
            else:
                logger.warning('Project has no template root directory')
        return template_dir

    def get_case_path(self, case_id, study=None, only_existing=False):
        """
        Construct path to case directory, based on a `case_id` (the name of the case).
        
        Args:
            case_id (str): Case ID, i.e. the name of the case. 
            study (ParsimStudy): Reference to parent `Study` instance. 
            only_existing (bool): If set, return path only if the case exists. 

        Returns:
            str: Path to case directory. Return None if `only_existing` argument is set
            and the case does not exist.
        """
        if study:
            study_path = study.path
        else:
            study_path = ''
        if case_id.startswith(self.config.get('case_prefix')):
            path = os.path.abspath(os.path.join(study_path, case_id))
        else:
            path = os.path.abspath(os.path.join(study_path, self.config.get('case_prefix') + case_id))
        if only_existing and not os.path.isfile(Case._get_data_file_path(path)):
            return None
        else:
            return path

    def get_study_path(self, name, only_existing=False):
        """
        Construct path to study directory, based on `name` of study.

        Args:
            name (str): Name of the study. 
            only_existing (bool): If set, return path only if the study exists. 

        Returns:
            str: Path to study directory. Return None if `only_existing` argument is set
            and the study does not exist.
        """
        # Later on, STUDY_PREFIX will be a property of the Project
        if name.startswith(self.config.get('study_prefix')):
            path = os.path.abspath(name)
        else:
            path = os.path.abspath(self.config.get('study_prefix') + name)
        if only_existing and not os.path.isfile(Study._get_data_file_path(path)):
            return None
        else:
            return path

    def find_target_path_and_type(self, name):
        """
        Find an existing case or study directory path, based on given `name`.
        
        The target could be either a case, or a study. Returns both path and type,
        if it finds a unique target.
        
        Args:
            name (str): Name of target to look for, which could be a case or a study. 

        Returns:
            (str, str): If a unique target (case or study) is found, returns tuple (`path`, `type`) with
            both path and object type string ('case' or 'study'). If both a case and study exists 
            with the given name, return `None` path and type 'both'. Returns ``(None, None)`` if no target
            is found.
        """
        case = self.get_case_path(name, only_existing=True)
        study = self.get_study_path(name, only_existing=True)
        if case and study:
            return None, 'both'
        elif case:
            return case, 'case'
        elif study:
            return study, 'study'
        else:
            return None, None

    def find_target(self, target_arg):
        """
        Process a command-line target argument and generate `ParsimError` if invalid.
        
        Args:
            target_arg (str): A string identifying a "target". This could be a single case or a study. 
                It could also be a single case within a study; if so, both study and case names are provided, 
                separated by a colon ":". For example, ``s2:c1`` identifies the case "c1" of study "s2".
        Returns:
            ParsimObject: Reference to target `Study` or `Case`. Returns reference to `Project`, if 
            `target_arg` is empty.
        """
        if self.exists:
            if target_arg:
                parts = target_arg.split(':')
                if len(parts) > 2:
                    raise ParsimError('Invalid target syntax (%s)' % target_arg)
                main_target = parts[0]
                sub_target = None
                if len(parts) == 2:
                    sub_target = parts[1]
                path, type = self.find_target_path_and_type(main_target)
                logger.debug('project.find_target: %s %s %s' % (main_target, repr(path), type))
                if type == 'case':
                    target = Case(name=main_target)
                elif type == 'study':
                    study = Study(name=main_target)
                    if study.exists:
                        if sub_target:
                            target = Case(name=sub_target, study=study)
                            if not target.exists:
                                raise ParsimError('Cannot find target case (%s) inside study (%s)'
                                                  % (sub_target, main_target))
                        else:
                            target = study
                    else:
                        raise ParsimError('Cannot find study on disk (bug?)')
                elif not type:
                    raise ParsimError('Cannot find a target case or study from the given name (%s)' % main_target)
                else:
                    raise ParsimError('Error: The given name matches both existing case and study. '
                                      'Include the case or study prefix to select a unique target.')
                if (not target) or (not target.exists):
                    raise ParsimError('Cannot find target on disk (bug?)')
            else:
                target = self
                type = 'project'
        else:
            raise ParsimError('There is no parsim project in this directory')
        return target


class Study(ParsimObject):
    """
    Parsim Study class.
    
    A `Study` instance holds information about a parameter study and contains one or more
    Cases. The `Study` has a dict of parameters common to all cases (can be represented
    as a Parsim parameter file). It will also have a caselist defining the parameter values 
    that vary between cases of the Study.
    
    A `Study` is usually identified by its name, and the `path` to its storage on disk will 
    then be constructed from the `name` argument.
    
    The constructor extends the baseclass constructor.
    
    Args:
        project (Project): Reference to parent `Project` instance.
        name (str): Name of the parameter study.
        path (str): Path to the `Study` on disk. If absent (common), the path is constructed from
            the `name` argument.
        
    Attributes:
        project (Project): Reference to parent `Project` instance.
    """
    _type = 'study'

    def __init__(self, name=None, path=None, **kwargs):
        self.project = kwargs.pop('project', Project())
        if not self.project.exists:
            raise ParsimError('There is no valid parent Project for this Study object')
        if not (path or name):
            raise ParsimError('Must have either name, or path to initialize a Study object')
        if not path:
            path = self.project.get_study_path(name)
            if not path:
                raise ParsimError('Cannot construct valid path from the given name (%s)' % name)
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        self._parameters = None
        self._caselist = None
        self._results = None
        super().__init__(name=name, path=path)

    def create(self, description=None, template=None, user_parameters=None, caselist_file=None, doe_scheme=None, doe_args=None,
               distr_dict=None):
        """
        Create a new `Study` object.

        
        Extends the baseclass method. This method provides two ways to generate Cases for Study;
        either the path of a caselist file is provided with the `caselist_file` option, or
        a DOE scheme is defined with the `doe_scheme` option. These two options are mutually
        exclusive. If none of them are provided, an empty Study (without cases) will be created,
        and the information about model template and user parameters is stored. (An empty Study
        is used when Parsim is run as an interface to Dakota.)

        If a DOE scheme is given, a dict with additional DOE options can be provided with
        the `doe_args` argument. The `distr_dict` argument should then be a dict defining
        statistical distributions for all uncertain parameters.

        Args:
            description (str): Optional description of parameter study.
            template (str): Name of (or path to) model template used for Cases of the Study.
            user_parameters (dict): Dict of parameters common to all cases.
            caselist_file (str): Path to caselist file with case and parameter definitions. 
            doe_scheme (str): Name of DOE scheme to use for case creation.
            doe_args (dict): Dict of arguments to the DOE scheme. 
            distr_dict (dict): Dict of distributions for uncertain parameters. 
        """
        # No case sources means empty Study, for example using Dakota. Otherwise caselist or doe.
        assert not (caselist_file and doe_scheme), 'Cannot have both CASELIST and DOE_SCHEME'
        if doe_scheme:
            assert isinstance(doe_args, dict), \
                'Expects DOE args to be dict with commandline arguments'
        # Create missing parameter dicts
        if not user_parameters:
            user_parameters = {}
        self.set('project_path', self.project.path)
        self.set('project_name', self.project.get('name'))
        # Determine full template path and verify
        template_path = self.project.get_template_path(template)
        if not template_path:
            raise ParsimError("Can't find a model template to use (default invalid, or not defined)")
        if template_path in self.path:
            raise ParsimError('Cannot create study inside the template directory!')
        self.set('template_path', template_path)
        self.set('caselist_file', caselist_file)
        self.set('doe_scheme', doe_scheme)
        self.set('doe_args', doe_args)
        self.set('distr_dict', distr_dict)
        try:
            super().create(description=description)
            if doe_scheme:
                import parsim.doe as pd
                # Create sampler object (doe_scheme)
                try:
                    sampler = eval('pd.%s(distr_dict, **doe_args)' % doe_scheme)
                except Exception as err:
                    logger.error('Failed creation of sampler object: %s' % err)
                    raise ParsimError('Failed creation of sampler object: %s' % err, handled=True)
                cases = sampler.get_case_definitions()  # list of tuples (case_id, case_dict)
                sampler.write_norm_matrix(os.path.join(self.path, 'doe.norm_matrix'))
                sampler.write_value_matrix(os.path.join(self.path, 'doe.value_matrix'))
            elif caselist_file:
                # Parse caselist file
                cases = parse_caselist_file(caselist_file)
            else:
                # Create empty Study (for use with Dakota, for example)
                cases = []
            # Create cases inside study
            self._create_cases(template_path, user_parameters, cases)
            self.save()
        except:
            self.delete(force=True)
            raise

    def _create_cases(self, template_path, user_parameters, cases):
        """
        Create cases inside study.

        This private function is used by methods `create` and `run_dakota`.
        The `cases` argument is a list, where each item is a tuple defining a case. This
        tuple is a case name (case ID) and a dict of parameter values for the case.
        Parameters common to all cases are given with the `user_parameters` argument.

        Args:
            template_path (str): Path to valid model template.
            user_parameters (dict): Dict with parameters specified by user on the
                commandline or in parameter file.
            cases (list): List of (`case_id`, `case_dict`) tuples, as returned
                by `parse_caselist_file` function.
        """
        # Parse default data file in template
        default_parameter_path = os.path.abspath(os.path.join(template_path,
                                                              self.project.config.get('default_parameter_file')))
        try:
            default_parameters = parse_parameter_file(default_parameter_path)
        except IOError as err:
            raise ParsimError('Error parsing default parameter file: %s' % err)

        # Create all cases!
        case_id_list = []
        case_dict = {}
        for case_id, case_dict in cases:
            case_id_list.append(case_id)
            case_description = case_dict.get('DESCRIPTION')
            case = Case(name=case_id, project=self.project, study=self)
            case.create(description=case_description, template=template_path, user_parameters=user_parameters, caselist_parameters=case_dict,
                        default_parameters=default_parameters)

        # Store case ids and sets of caselist and user parameters
        caselist_param_set = set(case_dict.keys())
        user_param_set = set(user_parameters.keys()) - caselist_param_set
        user_param_dict = dict([(k, user_parameters[k]) for k in user_param_set])
        default_param_set = set(default_parameters.keys()) - user_param_set - caselist_param_set
        self.set('case_id_list', case_id_list)
        self.set('caselist_param_list', list(caselist_param_set))
        self.set('user_param_list', list(user_param_set))
        self.set('user_param_dict', user_param_dict)
        # Store also in param_keys, for compatibility with Case data
        param_keys = {'caselist': self.get('caselist_param_list'),
                      'user': self.get('user_param_list'),
                      'default': list(default_param_set)}
        self.set('param_keys', param_keys)
        # Assemble dict with common Study parameters
        parameters = default_parameters.copy()
        parameters.update(user_parameters)
        self.set('parameters', parameters)

        # Write in study store: caselist file and user_parameter file
        caselist_path = os.path.join(self.path, 'study.caselist')
        paramfile_path = os.path.join(self.path, 'study.parameterfile')
        param_defaults_path = os.path.join(self.path, 'study.param_defaults')
        if cases:
            create_caselist_file(caselist_path, case_id_list, case_dicts=[d for n, d in cases],
                                 parameter_names=self.get('caselist_param_list'))
        create_parameter_file(paramfile_path, self.get('user_param_dict'))
        create_parameter_file(param_defaults_path,
                              dict([(k, v) for k, v in default_parameters.items() if k in default_param_set]))

    def __iter__(self):
        # Make a copy of the id list, in case it changes during iteration... (deletions, for example)
        self._iter_ids = list(self.get('case_id_list'))
        self._iter_index = 0
        self._iter_len = len(self._iter_ids)
        return self

    def next(self):
        """
        Iterator function (proxy for `__next__`, for Python 3 compatibility).
        """
        return self.__next__()

    def __next__(self):
        if self._iter_index == self._iter_len:
            raise StopIteration
        case = Case(name=self._iter_ids[self._iter_index], project=self.project, study=self)
        # Abort if case does not exist (should not happen)
        assert case.exists
        self._iter_index += 1
        return case

    def run(self, executable, **kwargs):
        """
        Run `executable` on all cases of the study.

        Iterates over all cases of the study and calls the `Case.run` method of each.

        Args:
            executable (str): Name or path of executable to run.
            **kwargs (dict): Dict of keyword arguments to forward.
        """
        self._logger.info('Starts RUN operation on cases (executable: %s)...' % executable)
        failed_cases = []
        for case in self:
            try:
                case.run(executable, **kwargs)
            except ParsimCaseError as err:
                failed_cases.append((case.get('name'), err))
        if failed_cases:
            self._logger.warning('Finished RUN operation: Failure for %d out of %d cases.' %
                                 (len(failed_cases), len(self.get('case_id_list'))))
        else:
            self._logger.info('Successfully finished RUN operation!')

    def run_dakota(self, dakota_file=None, executable=None, pre_run=False,
                   restart=False, restart_index=-1, stop_restart=0, shell=False):
        """
        Run Dakota in this Study.

        Runs Dakota inside the study (already created with the `create` method).
        The Dakota input file...

        Args:
            dakota_file (str):
            executable (str):
            pre_run (bool):
            restart:
            restart_index (int):
            stop_restart (int):
            shell (bool):
        """
        # Dakota executable starts command-line string
        cmd_string = self.project.config.get('dakota_exe', 'dakota')

        # Restart options ignored if pre_run requested
        if restart and not pre_run:
            if not self.exists:
                raise ParsimError('Cannot find existing Study to restart. Abort. (%s)' % self.path)

            # Counter of restarts
            dakota_run = self.get('dakota_run')
            dakota_run += 1

            if restart_index < 0:
                # Use latest restart
                read_index = dakota_run - 1
            elif restart_index < dakota_run:
                # Use selected index
                read_index = restart_index
            else:
                raise ParsimError('The selected restart index (%i) does not exist. Latest index: %i.'
                                  % (restart_index, dakota_run - 1))
            restart_file = 'dakota.restart.%i' % read_index
            cmd_string += ' -read_restart %s ' % restart_file
            if stop_restart:
                cmd_string += ' -stop_restart %i' % stop_restart

        else:
            dakota_run = 0
            self.set('dakota_variables', None)

            if pre_run:
                cmd_string += ' -pre_run ::dakota.pre_run'

        # Explicitly name Dakota restart file
        if not pre_run:
            cmd_string += ' -write_restart dakota.restart.%i' % dakota_run

        # Dakota input file
        dakota_input_path = os.path.abspath(dakota_file)
        shutil.copyfile(dakota_input_path, os.path.join(self.path, 'dakota.input.%i' % dakota_run))

        # Complete command-line string
        cmd_string += ' -o dakota.out -e dakota.err dakota.input.%i' % dakota_run

        # Write Dakota control data to Study
        self.set('dakota_run', dakota_run)
        self.set('dakota_simulation_exe', executable)
        self.set('dakota_input_file', dakota_input_path)
        self.save()

        # Log start message
        msg = 'Starts DAKOTA subprocess... (executable: %s)\n' \
              ' - Dakota input file: %s\n' \
              ' - Dakota run index: %i' \
              % (executable, dakota_input_path, dakota_run)
        if restart:
            msg += '\n - Restart file: %s' % restart_file
        if stop_restart:
            msg += '\n - Stop restart: %i' % stop_restart
        self._logger.info(msg)

        # Open output files and run
        output_to_console = True
        if output_to_console:
            fout = None
            ferr = None
        else:
            fout = open(os.path.join(self.path, 'psm_out.tmp'), 'w')
            ferr = open(os.path.join(self.path, 'psm_err.tmp'), 'w')

        start_time = datetime.datetime.now()

        wrk_dir = self.path

        print('dakota_cmd: '+cmd_string)

        try:
            # Provide for time-out?
            if shell or os.name == 'nt':
                subprocess.check_call(cmd_string, stdout=fout, stderr=ferr, cwd=wrk_dir, shell=shell)
            else:
                cmd_list = shlex.split(cmd_string)
                subprocess.check_call(cmd_list, stdout=fout, stderr=ferr, cwd=wrk_dir, shell=shell)
        except IOError as err:
            raise ParsimError(err)
        except subprocess.CalledProcessError as err:
            if err.returncode < 0:
                self._logger.warning('Dakota terminated with signal %s'
                                     % str(-err.returncode))
            else:
                self._logger.error('Dakota crashed: %s' % err)
                raise ParsimError(err)
        except KeyboardInterrupt:
            raise ParsimError('*** Interrupted by user ***')
        else:
            run_time = datetime.datetime.now() - start_time
            self._logger.info('Dakota finished successfully (runtime: %s)' % run_time)
        finally:
            try:
                ferr.close()
                fout.close()
            except AttributeError:
                pass

        # If pre-run, we create cases from the Dakota-generated caselist. Other process cases created by Dakota.
        if pre_run:
            # Read caselist generated by Dakota
            cases = parse_caselist_file(os.path.join(self.path, 'dakota.pre_run'))
            # Create cases
            template_path = self.get('template_path')
            user_parameters = self.get('user_param_dict')
            self._create_cases(template_path, user_parameters, cases)
            self.set('dakota_variables', self.get('caselist_param_list'))
        else:
            # Reload study data store, as psm Dakota drive will write Dakota variable names to it
            self.load()

            # Update Study data store...
            # - caselist parameters
            caselist_param_list = self.get('dakota_variables')
            self.set('caselist_param_list', caselist_param_list)
            caselist_param_set = set(caselist_param_list)
            # - User parameters
            user_param_set = set(self.get('user_param_list')) - caselist_param_set
            user_parameters = self.get('user_param_dict')
            user_param_dict = dict([(k, user_parameters[k]) for k in user_param_set])
            self.set('user_param_list', list(user_param_set))
            self.set('user_param_dict', user_param_dict)
            # - Default parameters
            param_keys = self.get('param_keys')
            default_param_set = set(param_keys['default']) - user_param_set - caselist_param_set
            # - Store also in param_keys, for compatibility with Case data
            param_keys = {'caselist': self.get('caselist_param_list'),
                          'user': self.get('user_param_list'),
                          'default': list(default_param_set)}
            self.set('param_keys', param_keys)
            # - Info on dakota cases
            cases = parse_caselist_file(os.path.join(self.path, 'dakota.caselist'))
            case_ids, case_dicts = zip(*cases)
            case_id_list = list(case_ids)
            self.set('case_id_list', case_id_list)
            # - Write Study caselist
            caselist_path = os.path.join(self.path, 'study.caselist')
            create_caselist_file(caselist_path, case_id_list, case_dicts=list(case_dicts),
                                 parameter_names=caselist_param_list)

        self.save()

    def collect(self, **kwargs):
        """
        Collect results from all cases of the study.

        Iterates over all cases of the study and calls the `Case.collect` method of each.

        Args:
            **kwargs (dict): Dict of keyword arguments to forward.
        """
        input = kwargs.get('input', None)
        if not isinstance(input, list):
            input_files = [input or self.project.config.get('default_results_file')]
        else:
            input_files = input

        # Parameter list could be sent from command-line... For now only contents of caselist.
        param_list = self.get('caselist_param_list')

        delim = kwargs['delim'] or ''
        if delim:
            extension = '.csv'
            csv = delim
        else:
            extension = '.txt'
            csv = False

        # Default output filename based on name of _first_ input file...
        output_file = kwargs.get('output', None) or os.path.splitext(input_files[0])[0] + extension
        if os.path.isabs(output_file):
            output_path = output_file
        else:
            output_path = os.path.join(self.path, output_file)

        self._logger.info('Start collecting case results...\n'
                         'Case results files (input)   : %s\n'
                         'Study results file (output) : %s' % (input_files, output_file))

        output_keys_set = None
        failed_cases = []
        cases = []
        results = []
        results_series = []
        # Read existing study.results as DataFrame, or create empty (new)
        if isinstance(self.results, pd.DataFrame):
            results_df = self.results.copy()
        else:
            results_df = None
        # Loop over all cases to collect results
        for case in self:
            name = case.get('name')
            try:
                output, params = case.collect(input=input_files, parameters=param_list)
            except ParsimCaseError as err:
                failed_cases.append((name, err))
                results_series.append(pd.Series({}, name=name))
            else:
                case_data = dict(output)
                # Check for unexpected number of output items
                if not output_keys_set: # First case is reference...
                    output_keys_set = set(case_data.keys())
                else:
                    missing = output_keys_set - case_data.keys()
                    if missing:
                        case._logger.error('Missing output fields: %s' % missing)
                    extra = case_data.keys() - output_keys_set
                    if extra:
                        case._logger.error('More output fields than the previous cases: %s' % extra)
                    if missing or extra:
                        failed_cases.append((name, None))
                        continue
                # Store if all is well
                results_series.append(pd.Series(case_data, name=name))
                # Add input parameters for complete CSV output
                case_data.update(params)
                results.append(case_data)
                cases.append(name)

        # Use last case data to create list of column labels, in order
        column_keys = sorted(output.keys())
        column_keys.extend(param_list)
        column_dict = dict(response_list=list(output.keys()), param_list=param_list)

        try:
            # File requested by user
            create_caselist_file(output_path, cases, case_dicts=results, parameter_names=column_keys, csv=csv)
            # Always output standard csv file "collect.csv" (for internal use, e.g. statistics)
            create_caselist_file(os.path.join(self.path, 'collect.csv'), cases, case_dicts=results,
                                 parameter_names=column_keys, csv=';')
            # Write json files with names of response variables and parameters
            with open(os.path.splitext(output_path)[0]+'.json', 'w') as f:
                json.dump(column_dict, f)
            with open(os.path.join(self.path, 'collect.json'), 'w') as f:
                json.dump(column_dict, f)
            # Write results DataFrame, both new and old data
            if isinstance(results_df, pd.DataFrame):
                # Combine new and old data
                new_df = pd.DataFrame(results_series)
                print(new_df.index)
                print(results_df.index)
                results_df = results_df.combine_first(new_df)
            else:
                results_df = pd.DataFrame(results_series)
            results_df.insert(loc=0, column='CASENAME', value=results_df.index)
            with open(os.path.join(self.path, 'study.results'), 'w') as f:
                f.write(results_df.to_string(index=False))
        except ParsimError as err:
            self._logger.error('Failed writing output file (with collected results)\n%s' % err)
            err.handled = True
            raise

        if failed_cases:
            self._logger.warning('Finished collecing results: Failure for %d out of %d cases.' %
                                 (len(failed_cases), len(self.get('case_id_list'))))
        else:
            self._logger.info('Successfully finished collecting case results!')

    def info(self, create_log=False):
        """
        Show some basic information about the study.
        """
        if not self.exists:
            return 'Study does not exists on disk -- no info available'
        # The string '\#' represents optional comment markers. They are removed unless create_log=True.
        template = textwrap.dedent("""\
            \\#Study name            : %(name)s
            \\#Creation date         : %(creation_date)s
            \\#Description           : %(description)s
            \\#Project name          : %(project_name)s
            \\#Template path         : %(template_path)s
            \\#Parsim version        : %(parsim_version)s
            \\#Project path          : %(project_path)s
            \\#Caselist/DOE params   : %(caselist_param_list)s
            \\#DOE scheme            : %(doe_scheme)s
            \\#DOE arguments         : %(doe_args)s
            """)
        msg = ''
        msg += template % self.data
        # Write parameter sources
        header = textwrap.dedent("""\
            \\#--------------------------------------------------------
            \\#%s
            \\#--------------------------------------------------------
            """)
        param_line = "%-22s: %s\n"
        if self.get('doe_scheme'):
            distr_dict = self.get('distr_dict')
            if len(distr_dict) > 0:
                msg += header % 'Variable parameter distributions (DOE)'
                for key, value in distr_dict.items():
                    msg += param_line % (key, value)
        if self.get('dakota_variables'):
            template = textwrap.dedent("""\
                \\#--------------------------------------------------------
                \\#dakota_run            : %(dakota_run)s
                \\#dakota_variables      : %(dakota_variables)s
                \\#dakota_input_file     : %(dakota_input_file)s
                \\#dakota_simulation_exe : %(dakota_simulation_exe)s
                """)
            msg += template % self.data

        sources = [('user', 'User parameters (command-line or parameter file)'),
                   ('default', 'Default parameters (defined in template)')]
        param_keys = self.get('param_keys')
        parameters = self.get('parameters')
        for src, title in sources:
            if len(param_keys[src]) > 0:
                msg += header % title
                for key in param_keys[src]:
                    msg += param_line % (key, parameters[key])
        # Write list of cases, with descriptions
        header = textwrap.dedent("""\
            \\#-------------------------------------------------------------------------
            \\# Case#  Case_ID           Description
            \\#-------------------------------------------------------------------------
            """)
        msg += header
        case_line = "\\# %-5d  %-17s %s\n"
        i = 0
        case_id_list = self.get('case_id_list')
        for case_id in case_id_list:
            i += 1
            case = Case(name=case_id, project=self.project, study=self)
            msg += case_line % (i, case_id, case.get('description'))
        msg += '\\#-------------------------------------------------------------------------\n'
        if create_log:
            return msg.replace('\\#', '# ').replace('  :', ':')
        else:
            return msg.replace('\\#', '')

    @property
    def parameters(self):
        """
        Getter returning pandas DataFrame containing value and source of all parameters.
        """
        if self.exists and not isinstance(self._parameters, pd.Series):
            param_keys = self.get('param_keys')
            parameters = self.get('parameters')
            p = pd.DataFrame(pd.Series(parameters, name='value'))
            p['source'] = 'default'
            p.loc[param_keys['caselist'], 'source'] = 'caselist'
            p.loc[param_keys['user'], 'source'] = 'user'
            self._parameters = p[p.source != 'caselist']
        return self._parameters

    @property
    def caselist(self):
        """
        Getter returning pandas DataFrame with the Study caselist (all varying parameters).
        """
        if self.exists and not isinstance(self._caselist, pd.DataFrame):
            try:
                self._caselist = pd.read_csv(os.path.join(self.path, 'study.caselist'),
                                             index_col='CASENAME', delim_whitespace=True)
                self._caselist.index = self._caselist.index.map(str)

            except FileNotFoundError:
                pass
        return self._caselist

    @property
    def results(self):
        """
        Getter returning pandas DataFrame with the last collected results of the Study.
        """
        if self.exists and not isinstance(self._results, pd.DataFrame):
            try:
                self._results = pd.read_csv(os.path.join(self.path, 'study.results'),
                                            index_col='CASENAME', delim_whitespace=True)
                self._results.index = self._results.index.map(str)
            except FileNotFoundError:
                pass
        return self._results


class Case(ParsimObject):
    """
    Parsim Case class.

    A `Case` instance holds information about a case, created from a model template.

    A `Case` is usually identified by its name, and the `path` to its storage on disk will
    then be constructed from the `name` argument.

    The constructor extends the baseclass constructor.

    Args:
        project (Project): Reference to parent `Project` instance.
        name (str): Name of the case.
        study (Study): Reference to parent `Study` instance, if any (otherwise None).

    Attributes:
        project (Project): Reference to parent `Project` instance.
        study (Study): Reference to parent `Study` instance (if any).
    """
    _type = 'case'

    def __init__(self, name=None, path=None, **kwargs):
        self.project = kwargs.pop('project', Project())
        if not self.project.exists:
            raise ParsimError('There is no valid parent Project for this Case object')
        self.study = kwargs.pop('study', None)
        if not (path or name):
            raise ParsimError('Must have either name, or path to initialize a Case object')
        if not path:
            if ':' in name:
                # Must find existing Case name on the form <study>:<case>
                try:
                    study_name, case_name = name.split(':')
                except ValueError as err:
                    raise ParsimError('Error processing colon-delimited study/case name (%s)' % err)
                self.study = Study(name=study_name)
                if not self.study.exists:
                    raise ParsimError('Cannot find existing Study with the given name (%s)' % study_name)
                path = self.project.get_case_path(case_name, study=self.study, only_existing=True)
            else:
                path = self.project.get_case_path(name, study=self.study)
            if not path:
                raise ParsimError('Cannot construct valid path from the given name (%s)' % name)
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        logger.debug('Case.init: path=%s' % path)
        self._parameters = None
        self._results = None
        super().__init__(name=name, path=path)

    def load(self):
        super().load()
        # Load parent study, if not already available
        if self._parent_object_type == 'study' and not self.study:
            if os.path.basename(self.get('study_path')) != os.path.basename(self._parent_object_path):
                raise ParsimError('Mismatch between stored study_path (%s) and parent_object_path (%s)' %
                                  (os.path.basename(self.get('study_path')), os.path.basename(self._parent_object_path)))
            logger.debug('Case.load() loads study: study_path (%s) and parent_object_path (%s)' \
                         % (os.path.basename(self.get('study_path')), os.path.basename(self._parent_object_path)))
            self.study = Study(path=self._parent_object_path, project=self.project)

    def create(self, description=None, template=None, user_parameters=None, caselist_parameters=None, default_parameters=None):
        """
        Create a new `Case` object.

        Args:
            description (str): Optional description of case.
            template (str): Name of (or path to) model template used for Cases of the Study.
            user_parameters (dict): Dict of parameters common to all cases.
            caselist_parameters (dict): Dict of parameters read from Study caselist.
            default_parameters (dict): Dict of default parameters (constructed here, if not provided
                by parent `Study`).
        """
        # Abort if creation inside existing study or another case
        if self._parent_object_type == 'case':
            raise ParsimError('Cannot create new case inside an existing case...')
        if self._parent_object_type == 'study' and not self.study:
            raise ParsimError('You are not allowed to create a new case inside an existing study...')
        self.set('project_path', self.project.path)
        self.set('project_name', self.project.get('name'))
        if self.study:
            self.set('study_path', self.study.path)
            self.set('study_name', self.study.get('name'))
        else:
            self.set('study_path', '')
            self.set('study_name', '')
        # Determine full template path and verify
        template_path = self.project.get_template_path(template)
        if not template_path:
            raise ParsimError("Can't find a model template to use (default invalid, or not defined)")
        if template_path in self.path:
            raise ParsimError('Cannot create case inside the template directory!')
        self.set('template_path', template_path)
        # Store empty results dict
        self.set('results', {})
        # Create missing parameter dicts
        if not user_parameters:
            user_parameters = {}
        if not caselist_parameters:
            caselist_parameters = {}
        # Default parameter dict may be forwarded by Study object, otherwise it's created here
        if not default_parameters:
            # Parse default data file in template
            default_parameter_path = os.path.abspath(
                os.path.join(template_path, self.project.config.get('default_parameter_file')))
            default_parameters = parse_parameter_file(default_parameter_path)
        # Trace parameter sources, no overlap!
        default_view = default_parameters.keys()
        user_view = user_parameters.keys()
        caselist_view = caselist_parameters.keys()
        src_keys_user = user_view - caselist_view
        src_keys_default = default_view - user_view - caselist_view
        # Store parameter keys per source (sorted lists)
        param_keys = {'caselist': list(caselist_view), 'user': list(src_keys_user), 'default': list(src_keys_default)}
        for src in iter(param_keys):
            param_keys[src].sort()
        self.set('param_keys', param_keys)
        # Assemble case parameter dict from sources
        parameters = default_parameters.copy()
        parameters.update(user_parameters)
        parameters.update(caselist_parameters)
        self.set('parameters', parameters)
        # Names for log and error files
        self.set('create_log', os.path.join(self._psm_path, 'create.log'))
        # Process template to create case
        current_directory = os.getcwd()
        try:
            super().create(description=description)
            self._create_case_from_template(template_path, parameters)
            self.save()  # Probably not necessary...
        except:
            os.chdir(current_directory)
            self.delete(force=True)
            raise
        finally:
            os.chdir(current_directory)

    def _create_case_from_template(self, template_path, param_dict):
        """
        Create case directory from template directory in template_path.

        Args:
            template_path (str): Path to model template directory.
            param_dict (dict): Dict of parameters, from all sources.
        """
        # Augment parameter list with parsim-related case information
        parameters = self.get_env()
        parameters.update(param_dict)
        # Global (project-level) ignore pattern function
        global_ignore_function = shutil.ignore_patterns(*self.project.config.get('psm_ignore_patterns'))
        # Update sys.path, so that Python modules will be found.
        parsim.add_to_syspath(os.path.join(self.project.path, 'bin'),
                              template_path,
                              os.path.join(template_path, 'bin'))
        # Process template directory
        for src_dir, dirs, files in os.walk(template_path):
            rel_src_dir = os.path.relpath(src_dir, template_path)
            dest_dir = os.path.join(self.path, rel_src_dir)
            # Create subdirectory in case, and go there!
            logger.debug('Dir: src_dir=%s rel_src_dir=%s dest_dir=%s' % (src_dir, rel_src_dir, dest_dir))
            if not rel_src_dir in ['.']:  # Case root directory already created...
                os.mkdir(dest_dir)
            os.chdir(dest_dir)
            # Global ignore of directory entries
            ignored_entries = global_ignore_function(src_dir, dirs + files)
            # Collect local ignore patterns for current directory
            if self.project.config.get('psm_ignore_file') in files:
                with open(os.path.join(src_dir, self.project.config.get('psm_ignore_file'))) as f:
                    lines = f.readlines()
                local_ignore_patterns = ' '.join(lines).split()
                local_ignore_function = shutil.ignore_patterns(*local_ignore_patterns)
                local_ignore = local_ignore_function(src_dir, dirs + files)
                if local_ignore:
                    ignored_entries |= local_ignore  # Union of the two sets...
            # Source directory and template path in pyexpander include path
            include_paths = [src_dir, template_path]
            # Process all files
            for entry in files:
                # In ignore list?
                if not entry in ignored_entries:
                    src_file = os.path.join(src_dir, entry)
                    (head, ext) = os.path.splitext(entry)
                    # Link?
                    pass
                    # Copy or expand file into case
                    if ext in ['.macro', '.pyexp']:
                        dest_file = os.path.join(dest_dir, head)
                        logger.debug('Expand file: src=%s dest=%s' % (src_file, dest_file))
                        # (try/except implemented in expandFileToFile, raising ParsimExpanderError on error)
                        parsim.expander.expandFileToFile(src_file, dest_file, parameters, include=include_paths)
                    else:
                        dest_file = os.path.join(dest_dir, entry)
                        logger.debug('Copy file: src=%s dest=%s' % (src_file, dest_file))
                        shutil.copyfile(src_file, dest_file)
                    shutil.copymode(src_file, dest_file)
            for entry in dirs:
                # Drop sub-directories matching ignore patterns
                if entry in ignored_entries:
                    dirs.remove(entry)
        with open(self.get('create_log'), 'w') as f:
            f.write(self.info(create_log=True))

    # Todo: Override load method? Should we instantiate study, if there is one and it's not loaded?

    def run(self, executable, args='', sub_dir=None, out=None, err=None, shell=False):
        """
        Run `executable` on the case.

        Args:
            executable (str): Name or path of executable to run.
            args (list): List of string arguments to executable.
            sub_dir (str): Relative path to Case subdirectory in which to run the executable (default
                is to run the in the root of the Case directory).
            out (str): Optional custom name of output file.
            err (str): Optional custom name of error file.
            shell (bool): Flag used by the subprocess call (whether to run executable in OS shell, or directly).
        """
        def create_out_err_path(out_err, default_path):
            if out_err:
                if os.path.isabs(out_err):
                    if self.study:
                        raise ParsimError('Error: Absolute path to out/err file not allowed with a Study, '
                                          'as all cases would overwrite the same file')
                path = os.path.join(self.path, out_err)
            else:
                path = os.path.join(self.path, default_path)
            (head, tail) = os.path.split(path)
            if not os.path.isdir(head):
                logger.debug('create_out_err_path: Creates parent directories for out/err file path (%s)' % head)
                os.makedirs(head)
            return path

        # Find path to executable (search order: abspath, cwd, projdir/bin, casedir, casedir/bin, casedir/sub_dir)
        logger.debug('Subdir: %s' % sub_dir)
        if os.path.isabs(executable):
            if os.path.isfile(executable):
                exepath = executable
            else:
                raise ParsimError('Cannot find executable by absolute path (%s)' % executable)
        else:
            exepath = find_file_path(executable,
                                     os.getcwd(),
                                     os.path.join(self.project.path, 'bin'),
                                     self.path,
                                     os.path.join(self.path, 'bin'),
                                     os.path.join(self.path, sub_dir or ''))
        if not exepath:
            raise ParsimError('Cannot find executable (%s)' % executable)
        (head, tail) = os.path.split(exepath)
        (exe_name, ext) = os.path.splitext(tail)
        logger.debug('Case.run: Found executable %s' % exepath)
        # Check for file types which need to run in an interpreter, e.g. Python scripts
        if ext in ['.py', '.pyc']:
            interpreter = self.project.config.get('python_exe')
        else:
            interpreter = ''
        # Prepare executable and arguments, depending on shell or not (string or list)
        cmd_string = '%s %s %s' % (interpreter, exepath, ' '.join(args))
        # Look at subdir, and create path to temporary working directory
        if sub_dir:
            wrk_dir = os.path.join(self.path, sub_dir)
        else:
            wrk_dir = self.path
        # Create full paths to out and err files
        outfile = create_out_err_path(out, exe_name + '.out')
        errfile = create_out_err_path(out, exe_name + '.err')
        loginfo = '   Executable : %s \n' \
                  '   stdout     : %s \n' \
                  '   stderr     : %s' % (exepath, outfile, errfile)
        # Start log message:
        self._logger.info('Executing command/script/executable: %s %s' % (tail, ' '.join(args)))
        # Experimental writing of what is happening... Will be overwritten by log message!
        print('%s: Running executable...' % self.get('name'), end='\r')
        sys.stdout.flush()
        start_time = datetime.datetime.now()
        # Open output files and run
        with open(outfile, 'w') as fout, open(errfile, 'w') as ferr:
            cwd = os.getcwd()
            # Augment subprocess environment with parsim-related case information
            environ = dict(os.environ)
            environ.update(self.get_env())
            try:
                # Provide for time-out?
                if shell or os.name == 'nt':
                    subprocess.check_call(cmd_string, stdout=fout, stderr=ferr, env=environ, cwd=wrk_dir, shell=shell)
                else:
                    cmd_list = shlex.split(cmd_string)
                    subprocess.check_call(cmd_list, stdout=fout, stderr=ferr, env=environ, cwd=wrk_dir, shell=shell)
            except IOError as err:
                raise ParsimError(err)
            except subprocess.CalledProcessError as err:
                if err.returncode < 0:
                    self._logger.warning('Executable was terminated with signal %s \n%s'
                                         % (str(-err.returncode), loginfo))
                else:
                    self._logger.error('Executable crashed: %s\n%s' % (err, loginfo))
                    raise ParsimCaseError(err)
            except KeyboardInterrupt:
                raise ParsimError('*** Interrupted by user ***')
            else:
                run_time = datetime.datetime.now() - start_time
                self._logger.info('Executable finished successfully (runtime: %s)\n%s' % (run_time, loginfo))
        # Remove empty out/err file
        for f in [outfile, errfile]:
            if not os.stat(f).st_size:
                os.remove(f)

    def collect(self, input=None, parameters=None):
        """
        Collect results from the case.

        Args:
            input (list): List of names of results files to process (could also be string of single file name).
            parameters (list): List of input parameter columns to include in output table.

        Returns:
            (dict, dict): Tuple containing dict of name and value of result variables (output_dict) and
            dict of name and value of input parameters to include in output table (param_dict).
        """
        param_dict = dict([(x, self.get('parameters')[x]) for x in parameters])
        if not isinstance(input, list):
            input_files = [input or self.project.config.get('default_results_file')]
        else:
            input_files = input
        output_dict = {}
        for filename in input_files:
            input_path = os.path.join(self.path, filename)
            try:
                with open(input_path, 'r') as f:
                    output_dict.update(json.load(f))
            except Exception as err:
                self._logger.error('Failure reading JSON results file (%s)\n%s' % (filename, err))
                raise ParsimCaseError('Failure reading JSON results file \n%s' % err)
        # Store/update all collected case results in case.results file (cumulative)
        try:
            with open(os.path.join(self.path, 'case.results'), 'r') as f:
                case_results = json.load(f)
                case_results.update(output_dict)
        except FileNotFoundError:
            case_results = output_dict
        with open(os.path.join(self.path, 'case.results'), 'w') as f:
            json.dump(case_results, f, indent=2)
        return output_dict, param_dict

    def info(self, create_log=False):
        """
        Show some basic information about the case.
        """
        if not self.exists:
            return 'Case does not exists on disk -- no info available'
        # The string '\#' represents optional comment markers. They are removed unless create_log=True.
        template = textwrap.dedent("""\
            \\#Case ID             : %(name)s
            \\#Creation date       : %(creation_date)s
            \\#Description         : %(description)s
            \\#Project name        : %(project_name)s
            \\#Study name          : %(study_name)s
            \\#Template path       : %(template_path)s
            \\#Creation log file   : %(create_log)s
            \\#Parsim version      : %(parsim_version)s
            \\#Project path        : %(project_path)s
            \\#Study path          : %(study_path)s
            """)
        header = textwrap.dedent("""\
            \\#--------------------------------------------------------
            \\#%s
            \\#--------------------------------------------------------
            """)
        param_line = "%-22s: %s\n"
        param_keys = self.get('param_keys')
        sources = [('caselist', 'Caselist parameters (defined in study)'),
                   ('user', 'User parameters (command-line or parameter file)'),
                   ('default', 'Default parameters (defined in template)')]
        msg = ''
        msg += template % self.data
        parameters = self.get('parameters')
        for src, title in sources:
            if len(param_keys[src]) > 0:
                msg += header % title
                for key in param_keys[src]:
                    msg += param_line % (key, parameters[key])
        if create_log:
            return msg.replace('\\#', '# ')
        else:
            return msg.replace('\\#', '')

    def get_env(self):
        """
        Create and return dict with parsim-related information about the case.

        These key-value pairs can be sent along as extra parameters on case creation, or
        injected into "run" subprocess as environment variables.

        Returns:
              dict: parsim-related case information
        """
        if self.get('study_name'):
            case_id = ':'.join([self.get('study_name'), self.get('name')])
        else:
            case_id = self.get('name')
        return {
            'PARSIM_VERSION': self.get('parsim_version'),
            'PARSIM_PROJECT_PATH': self.get('project_path'),
            'PARSIM_TEMPLATE_PATH': self.get('template_path'),
            'PARSIM_CASE_ID': case_id,
            'PARSIM_CASE_NAME': self.get('name'),
            'PARSIM_STUDY_NAME': self.get('study_name'),
            'PARSIM_PROJECT_NAME': self.get('project_name')
        }

    @property
    def parameters(self):
        """
        Getter returning pandas DataFrame containing value and source of all parameters.
        """
        if self.exists and not isinstance(self._parameters, pd.DataFrame):
            param_keys = self.get('param_keys')
            parameters = self.get('parameters')
            p = pd.DataFrame(pd.Series(parameters, name='value'))
            p['source'] = 'default'
            p.loc[param_keys['caselist'], 'source'] = 'caselist'
            p.loc[param_keys['user'], 'source'] = 'user'
            self._parameters = p
        return self._parameters

    @property
    def results(self):
        """
        Getter returning pandas Series containing all results collected for the case
        """
        if self.exists and not isinstance(self._results, pd.Series):
            try:
                with open(os.path.join(self.path, 'case.results')) as f:
                    case_results = json.load(f)
                    self._results = pd.Series(case_results, name='results')
            except FileNotFoundError:
                pass
        return self._results
