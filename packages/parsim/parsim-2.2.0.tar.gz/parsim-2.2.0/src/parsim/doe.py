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
import textwrap
import sys

import numpy as np
import scipy as sp
import scipy.stats as stats
import pyDOE3 as pydoe

from parsim.loggers import logger
from parsim.core import ParsimError


schemes = ['mc', 'ff2n', 'fullfact', 'fracfact', 'ccdesign', 'lhs', 'pb', 'gsd']

def docstring_first_line(obj):
    """
    Extract text from first line of object's docstring.

    Arguments:
        obj (object): Reference to object.

    Returns:
        str: Docstring text (first line).
    """
    return obj.__doc__.strip().splitlines()[0]

def help_message(sphinx=False):
    """
    Create help message for DOE sampling, listing all available samplers in this module.

    Documentation is available from sampler classes docstrings.

    Arguments:
        sphinx (bool): Set to True if called from Sphinx run.

    Returns:
        str: Help message description created from docstring.
    """
    sampler_descriptions = 'Available DOE sampling schemes:\n'
    thismodule = sys.modules[__name__]
    if sphinx:
        description = ''
        with open('doe_schemes.inc', 'w') as inc:
            for sampler in schemes:
                f = getattr(thismodule, sampler)
                if f:
                    inc.write('%s,%s\n' % (sampler, docstring_first_line(f)))
    else:
        for sampler in schemes:
            f = getattr(thismodule, sampler)
            if f:
                sampler_descriptions += "    %-10s %s\n" % (sampler, docstring_first_line(f))

        description = '\n\n' + sampler_descriptions + '\n\n'
        description += textwrap.dedent('To get help on an individual sampling scheme, search '\
                                       'help for the doe command and add name of scheme. \nFor example:\n')
        description += '   psm help doe <scheme>\n'
        description += '     or\n'
        description += '   psm doe -h <scheme>\n'

    return description


class SamplingScheme:
    """
    Baseclass for sampling schemes, used for creating parsim Study cbjects.

    Arguments:
        distr_dict (dict): Dict of distribution definitions for varying parameters.
        kwargs (dict): Dict of keyword arguments for sampling schemes.
    """

    sampling_method = None

    def __init__(self, distr_dict, **kwargs):
        assert isinstance(distr_dict, dict), 'Expected dict with distributions'
        self.args = kwargs
        self.data = {}
        self.norm_matrix = None
        self.value_matrix = None

        self.name = self.__class__.__name__
        self.description = docstring_first_line(self.__class__)
        self.parameters = kwargs.get('parameters', list(distr_dict.keys()))

        # Dicts for valid and required arguments
        self.valid_args = []
        self.required_args = []

        # Instantiate distributions from scipy.stats
        self.distr_dict = {}
        try:
            for p, d in distr_dict.items():
                self.distr_dict[p] = eval('stats.%s' % d)
        except:
            raise ParsimError('Error creating distribution %s for parameter "%s"' % (d, p))

        # Common data
        self.set('nsamples', 0)
        self.set('npar', len(self.parameters))

        # Call sub-class _init(). May set default values.
        self._init()

        # Update data with all keyword arguments
        self.data.update(kwargs)

        # Check valid and required arguments (kwargs)
        self._check_args()

        # Run pre-calc stuff
        self._pre_calc()

        # Compute sampling matrices; normalized (norm_matrix) and actual values (value_matrix)
        self._calc_norm()
        if not self.get('nsamples'):
            self.set('nsamples', self.norm_matrix.shape[0])
        assert self.norm_matrix.shape == (self.get('nsamples'), self.get('npar')), 'Wrong dimension of norm_matrix!'

        self._calc_value()
        assert self.value_matrix.shape == (self.get('nsamples'), self.get('npar')), 'Wrong dimension of value_matrix!'

    def get(self, *key):
        """
        Get value from object dictionary.

        Args:
            *key (list): List of arguments; first argument is key name, second holds optional default value.

        Returns:
            value: Value of dictionary value.
        """
        if len(key)>1:
            return self.data.get(key[0], key[1])
        else:
            return self.data.get(key[0])

    def set(self, key, value):
        """
        Sets value in object dictionary.

        Arguments:
            key (str): Name of variable.
            value: Value of variable.
        """
        self.data[key] = value

    def add_valid_args(self, args):
        """
        Add variable name to list of valid arguments for the scheme.

        Arguments:
            args (str): Name of argument.
        """
        self.valid_args.extend(args)

    def add_required_args(self, args):
        """
        Add variable name to list of required arguments for the scheme.

        Arguments:
            args (str): Name of argument.
        """
        self.required_args.extend(args)

    def _init(self):
        """
        Make scheme-specific initialization.

        This method is extended by subclasses.

        Example::

            # Add keyword information
            add_valid_args(['n', 'method'])
            add_required_args(['n'])
        """
        pass

    def _check_args(self):
        """
        Check validity of arguments.
        """
        unknown_args = set(self.args) - set(self.valid_args) - set(self.required_args)
        missing_args = set(self.required_args) - set(self.args)

        if missing_args:
            raise ParsimError('The following required DOE arguments are missing: %s'
                         % ', '.join(missing_args))
        if unknown_args:
            raise ParsimError('The following DOE arguments are unknown: %s'
                           % ', '.join(unknown_args))

    def _pre_calc(self):
        """
        Do preparations necessary before `_calc` is run.
        """
        pass

    def _calc_norm(self):
        """
        Process keyword arguments, then compute and set `norm_matrix`.

        Must be overridden by subclass!

        Example for single reference case with distribution mean values::

            npar = self.get('npar')
            self.norm_matrix = np.zeros(1, npar)
        """
        raise NotImplementedError

    def _calc_value(self):
        """
        Compute `value_matrix` from `norm_matrix`.

        Must be overridden by subclass!
        """
        raise NotImplementedError

    def write_caselist(self, filename):
        """
        Construct and write caselist to file. Not yet implemented.

        Arguments:
            filename (str): Name of caselist to write.
        """
        raise NotImplementedError

    def write_norm_matrix(self, filename):
        """
        Write `norm_matrix` to file.

        Arguments:
            filename (str): Name of output file.
        """
        with open(filename, 'w') as f:
            f.write(str(self.norm_matrix)+'\n')

    def write_value_matrix(self, filename):
        """
        Write `value_matrix` to file.

        Arguments:
            filename (str): Name of output file.
        """
        with open(filename, 'w') as f:
            f.write(str(self.value_matrix)+'\n')

    def get_case_definitions(self):
        """
        Output list of tuples (case_id, case_dict)
        """
        n = self.get('nsamples')
        p = self.get('npar')
        cases = [(str(i+1), dict([(self.parameters[j], self.value_matrix[i, j]) for j in range(p)])) for i in range(n)]
        return cases

    def log_message(self):
        """
        Return log message for the sampling operation.
        """
        return 'Empty log message for sampling operation (baseclass)'

    @classmethod
    def help_message(cls):
        """
        Return help message for this sampler class, based on subclass docstring.

        Docstring should describe sampling method and all options.
        """
        return textwrap.dedent(cls.__doc__)


class RandomSamplingScheme(SamplingScheme):
    """
    Subclass for random sampling of distributions through their Cumulative Distribution Function (CDF).
    """

    sampling_method = 'cdf'

    def _cdf_sampling(self):
        """
        Compute self.value_matrix, based on CDF of parameter distributions and random data in self.norm_matrix.
        """
        self.value_matrix = np.zeros_like(self.norm_matrix)
        for i in range(self.get('npar')):
            self.value_matrix[:, i] = self.distr_dict[self.parameters[i]].ppf(self.norm_matrix[:, i])

    def _init(self):
        super()._init()
        self.add_valid_args(['seed'])
        self.set('seed', 1234)

    def _pre_calc(self):
        # Seed random number generator (numpy)
        seed = self.get('seed')
        assert isinstance(seed, int), 'Random seed must be integer'
        np.random.seed(seed)

    def _calc_value(self):
        """
        Create sampling matrix value_matrix, assuming subclass has already calculated norm_matrix.

        Overrides baseclass method. Normalized values (`norm_matrix`) are assumed to be in interval
        [0, 1] and actual values (`value_matrix`) are drawn from the inverse of the cumulative distribution
        function (CDF) of the parameter distributions.
        """
        self._cdf_sampling()

    def log_message(self):
        """
        Return log message for the sampling operation.
        """
        return 'Empty log message for CDF sampling operation (baseclass)'


class FactorLevelScheme(SamplingScheme):
    """
    Subclass for sampling factors at certain levels.
    """

    sampling_method = 'levels'

    def _init(self):
        super()._init()
        self.add_valid_args(['mapping', 'beta'])
        self.set('mapping', 'int')
        self.set('beta', 0.9545)

    def _level_sampling(self):
        """
        Compute `value_matrix`, based on factor levels in `norm_matrix`.
        """

        # Supported methods for selecting factor levels
        mapping_methods = ['int']
        assert self.get('mapping') in mapping_methods, \
            'Expected "mapping" to be one of the methods in %s' % repr(mapping_methods)

        self.value_matrix = np.zeros_like(self.norm_matrix)

        for i in range(self.get('npar')):
            distribution = self.distr_dict[self.parameters[i]]
            if self.get('mapping') == 'int':
                high, low = distribution.interval(self.get('beta'))
            else:
                raise NotImplementedError

            self.value_matrix[:, i] = (high + low) / 2. + (high - low) / 2. * self.norm_matrix[:, i]

    def _calc_value(self):
        """
        Create sampling matrix value_matrix, assuming subclass has already calculated norm_matrix.

        Overrides baseclass method. Normalized values (norm_matrix) are assumed to be in interval
        [0, 1] and actual values (value_matrix) are drawn from the inverse of the cumulative distribution
        function (CDF) of the parameter distributions.
        """
        self._level_sampling()

    def log_message(self):
        """Return log message for the sampling operation."""
        return 'Empty log message for factor-level sampling operation (baseclass)'


class mc(RandomSamplingScheme):
    """
    Monte Carlo random sampling.

    Keyword arguments:
        n (int): Number of samples (default: 10)
    """
    def _init(self):
        super()._init()
        self.add_valid_args(['n'])

    def _calc_norm(self):
        # Default to 10 samples, if number not specified with argument 'n'
        self.set('nsamples', self.get('n', 10))

        # Compute random matrix
        self.norm_matrix = np.random.rand(self.get('nsamples'), self.get('npar'))


class lhs(RandomSamplingScheme):
    """
    Latin Hypercube sampling.

    Keyword arguments:
        n (int): Number of sample points (default: one per parameter)
        mode (str): String that tells lhs how to sample the points,

            'rand': Random within sampling interval (default),

            'center', 'c': Center within interval,

            'maximin', 'm': Maximize the minimum distance between points, but place the point in a randomized location within its interval,

            'centermaximin', 'cm': Same as 'maximin', but centered within the intervals,

            'correlation', 'corr': Minimize the maximum correlation coefficient.
        iter (int): Number of iterations (used by some modes; see pyDOE docs and code).
    """

    valid_modes = ['rand', 'center', 'c', 'maximin', 'm', 'centermaximin', 'cm', 'correlation', 'corr']

    def _init(self):
        super()._init()
        self.add_valid_args(['n', 'mode', 'iter'])
        self.set('n', self.get('npar'))
        self.set('mode', 'rand')
        self.set('iter', None)

    def _check_args(self):
        super()._check_args()
        mode = self.get('mode')
        if not mode in self.valid_modes:
            raise ParsimError('Invalid mode (%s). Must be one of: %s' % (mode, self.valid_modes))

    def _calc_norm(self):
        mode = self.get('mode')
        if mode == 'rand':
            mode = None

        # Compute random matrix
        self.norm_matrix = pydoe.lhs(self.get('npar'), samples=self.get('n'),
                                  criterion=mode, iterations=self.get('iter'))


class ff2n(FactorLevelScheme):
    """
    Two-level full factorial sampling.

    Keyword arguments:
        mapping (str): Selection of method for mapping factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
    """

    def _calc_norm(self):
        # Compute design matrix
        self.norm_matrix = pydoe.ff2n(self.get('npar'))


class fullfact(FactorLevelScheme):
    """
    General full factorial sampling (for more than two levels).

    The number of levels can be given individually for each parameters using the "levels" keyword argument.
    If a single integer is given, this is the number of levels used for all parameters.

    Keyword arguments:
        mapping (str): Selection of method for mapping high/low factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is
                   given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
        levels (str): Comma-delimited list of number of levels for each parameter. If only one integer is given,
        this number of levels will be used for all parameters. Defaults to two levels, same as ff2n.
        Example: "levels=2,2,3,3"
    """

    def _init(self):
        super()._init()
        self.add_valid_args(['levels'])
        self.set('levels', 2)

    def _check_args(self):
        super()._check_args()
        if type(self.get('levels')) == int:
            self.levels = self.get('npar') * [self.get('levels')]
        else:
            try:
                self.levels = list(self.get('levels'))
            except ValueError:
                raise ParsimError('List of parameter levels must contain only integers')
            if len(self.levels) != self.get('npar'):
                raise ParsimError('Number of levels must equal number of parameters. Found %i, expected %i' %
                             (len(self.levels), self.get('npar')))

    def _calc_norm(self):
        # Compute design matrix
        self.norm_matrix = 2*pydoe.fullfact(self.levels) / (np.array(self.levels)-1) - 1


class gsd(fullfact):
    """
    Generalized Subset Design (GSD)

    GSD is a generalization of traditional fractional factorial designs to problems, where factors can have
    more than two levels.

    In many application problems, factors can have categorical or quantitative factors on more than two levels.
    Conventional reduced designs have not been able to deal with such types of problems. Full multi-level factorial
    designs can handle such problems, but the number of samples quickly grows too large to be useful.

    The GSD method provides balanced designs in multi-level experiments, with the number of experiments reduced by a
    user-specified reduction factor. Complementary reduced designs are also provided, analogous to fold-over in
    traditional fractional factorial designs.

    The number of levels can be given individually for each parameter using the "levels" keyword argument.
    If a single integer is given, this is the number of levels used for all parameters. The "reduction" keyword
    is used to specify the reduction factor of the design; the reduction factor must be an integer larger than one
    (default is 2). The number of complementary designs is controlled by the "ncomp" keyword (default is 1, meaning
    only the original reduced design is used).

    Keyword arguments:
        mapping (str): Selection of method for mapping high/low factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is
                   given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
        levels (str): Comma-delimited list of number of levels for each parameter. If only one integer is given,
        this number of levels will be used for all parameters. Defaults to two levels, same as ff2n.
        Example: "levels=2,2,3,3"
        reduction (int): Size reduction factor, which must be an integer larger than one (default: 2)
        ncomp (int): Number of complementary designs (default: 1)
    """

    def _init(self):
        super()._init()
        self.add_valid_args(['reduction', 'ncomp'])
        self.set('reduction', 2)
        self.set('ncomp', 1)

    def _check_args(self):
        super()._check_args()
        if (type(self.get('reduction')) != int) or (self.get('reduction') < 2):
            raise ParsimError('Reduction factor must be an integer larger than 1.')
        if (type(self.get('ncomp')) != int) or (self.get('ncomp') < 1):
            raise ParsimError('ncomp parameter must be a positive integer.')

    def _calc_norm(self):
        # Compute design matrix
        self.norm_matrix = 2*pydoe.gsd(self.levels, self.get('reduction'), self.get('ncomp')) / (np.array(self.levels)-1) - 1


class pb(FactorLevelScheme):
    """
    Plackett-Burman (pbdesign).

    Another way to generate fractional-factorial designs is through the use of Plackett-Burman designs.
    These designs are unique in that the number of trial conditions (rows) expands by multiples of four
    (e.g. 4, 8, 12, etc.). The max number of factors allowed before a design increases the number of
    rows is always one less than the next higher multiple of four.

    Keyword arguments:
        mapping (str): Selection of method for mapping factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
    """

    def _calc_norm(self):
        # Compute design matrix
        self.norm_matrix = pydoe.pbdesign(self.get('npar'))


class fracfact(FactorLevelScheme):
    """
    Two-level fractional factorial sampling.

    A fractional factorial design reduces the number of runs, compared to a full factorial design, by
    confounding certain main factor effects with interaction effects. The confounding must be explicitly
    defined by the user, either by supplying a so-called *generator* expression with the "gen" keyword, or defining
    the *resolution* of the design with the "res" keyword (only one of these keywords should be used).

    In addition, the resulting design may be folded (replicated with levels switched). The keyword "fold"
    specifies if folding should be applied, either an all columns (value "all"), or by listing which parameters
    to fold (comma-delimited list of parameter4 columns; first parameter is "1"). For example, "fold=1,3" to fold
    parameters one and three, or "fold=all" to fold the whole design.

    Keyword arguments:
        mapping (str): Selection of method for mapping high/low factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is
                   given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
        gen (str): Generator pattern, for example gen='a,b,ab' for three parameters. Note that the generator expression
            must be given as a quoted string, with columns delimited by commas rather than white-space.
        res (int): Resolution of the design, defined as an integer. Common values are 3, 4 or 5, depending on
            the number of parameters in the design.
        fold (str): Specify optional folding of design. "all" to fold all columns, or a comma-delimited list of
            columns to fold (starting with 1 for first column). For example, fold='all', or fold=1,3,5.
    """

    def _init(self):
        super()._init()
        self.add_valid_args(['fold', 'gen', 'res'])
        self.set('fold', None)
        self.set('res', None)
        self.set('gen', None)

    def _check_args(self):
        super()._check_args()
        # fold
        self.fold = self.get('fold')
        if self.fold:
            if type(self.fold) == str:
                if not self.fold == 'all':
                    raise ParsimError('Unknown value for "fold": %s' % (self.fold))
            else:
                # Test validity of fold column indices
                try:
                    max_col = max(self.fold)
                except (ValueError, NameError):
                    raise ParsimError('List of fold columns invalid: %s' % str(self.fold))
                if max_col > self.get('npar'):
                    raise ParsimError('Column index larger than number of parameters')
        # Generator expression or resolution
        if self.get('gen') and self.get('res'):
            raise ParsimError('Options "res" and "gen" are mutually exclusive -- only one can be specified!')
        elif self.get('gen'):
            try:
                self.gen_list = self.get('gen').split(',')
            except:
                raise ParsimError('Error parsing generator expression: %s' % self.get('gen'))
            if len(self.gen_list) != self.get('npar'):
                    raise ParsimError('Number of columns in generator expression must equal number of parameters. Found %i, expected %i' %
                                 (len(self.gen_list), self.get('npar')))
        elif self.get('res'):
            try:
                self.res = int(self.get('res'))
            except:
                raise ParsimError('Resolution must be an integer value (found "%s")' % self.get('res'))
        else:
            raise ParsimError('Either generator expression ("gen") or design resolution ("res") must be specified.')

    def _calc_norm(self):
        # Compute design matrix, either by generator or by resolution
        if self.get('gen'):
            self.norm_matrix = pydoe.fracfact(' '.join(self.gen_list))
        else:
            try:
                self.norm_matrix = pydoe.fracfact_by_res(self.get('npar'), self.res)
            except ValueError:
                raise ParsimError('Error in pydoe2.fracfact_by_res, probably because it is not possible to create a '
                                  'design with the requested resolution (%s)' % self.get('res'))
        # Optional folding
        if self.fold == 'all':
            self.norm_matrix = pydoe.fold(self.norm_matrix)
        elif self.fold:
            self.norm_matrix = pydoe.fold(self.norm_matrix, columns=list(self.fold))


class ccdesign(FactorLevelScheme):
    """
    Central Composite Design (CCD).

    The "face" keyword can be used to select one of three combinations of facial and corner points: 'ccc' for
    circumscribed (corner points are at nominal high/low levels, while facial points are outside (!) of these);
    'cci' for inscribed (facial points are at nominal high/low levels, while corner points are inside of these);
    'ccf' for faced (both corner and facial points are at nominal high/low levels). Contrary to pyDOE standard
    behavior, the parsim default is inscribed, 'cci', such that parameter values are guaranteed not to exceed
    the nominal high/low levels. If a circumscribed ('ccc') is defined, then beware that the facial points may
    lie far outside of the nominal high/low levels -- make sure these extreme values are realistic and
    physically meaningful! This effect can be controlled to some extend by choosing a smaller value of the
    `beta` parameter, so that the nominal high/low levels are taken away from the tails/bounds of the
    parameter distributions.

    The "alpha" keyword is used to define designs that are either orthogonal (value 'o'), or rotatable (value 'r').
    Default is orthogonal, 'o'. Note that both circumscribed and inscribed designs may be rotatable, but the faced
    design ('ccf') cannot.

    The CCD method generates only one center point, since simulations are deterministic in nature. For regression
    analysis of the results, however, the center point should usually be replicated or weighted higher than the
    other points.

    Keyword arguments:
        mapping (str): Selection of method for mapping high/low factor levels to actual values in the distribution.

                   'int': (default) Use confidence interval with equal areas around the mean. Width of interval is
                   given by parameter 'beta' (default: 0.9545)
        beta (float): Width of confidence interval for 'int' method (see above). Default: 0.9545 (+/- 2*sigma)
        face (str): Specifies combination of corner and facial points: 'cci' for inscribed (default), 'ccc'
            for circumscribed or 'ccf' for faced design.
        alpha (str): Selects whether design should be orthogonal ('o') or rotatable ('r'). Default is orthogonal.
    """

    def _init(self):
        super()._init()
        self.add_valid_args(['face', 'alpha'])
        self.set('face', 'cci')
        self.set('alpha', 'o')

    def _check_args(self):
        super()._check_args()
        # face
        if not self.get('face') in ['ccc', 'cci', 'ccf']:
            raise ParsimError('Invalid value of "face" keyword: Must be one of "cci", "ccc" or "ccf"')
        if self.get('face') == 'ccc':
            logger.warning('Beware that the facial points of a circumscribed design may lie far outside of '
                           'the nominal high/low values selected by the value of the "beta" keyword.')
        # alpha
        if not self.get('alpha') in ['o', 'orthogonal', 'r', 'rotatable']:
            raise ParsimError('Invalid value of "alpha" keyword: Must be one of "o" or "r"')
        if self.get('face') == 'ccf' and self.get('alpha')[0] == 'r':
            raise ParsimError('Invalid combination of "face" and "alpha": A faced design (ccf) cannot be '
                              'rotatable (r)...')

    def _calc_norm(self):
        # Compute design matrix
        self.norm_matrix = pydoe.ccdesign(self.get('npar'), (0,1), self.get('alpha'), self.get('face'))
