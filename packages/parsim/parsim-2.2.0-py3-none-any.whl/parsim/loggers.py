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
import logging

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
USER_LOG_LEVEL = 25
DEFAULT_LOG_LEVEL = logging.INFO
ROOT_LOGGER_NAME = 'parsim'
CONSOLE_FMT = '%(levelname)s: %(message)s'
CONSOLE_FMT_CHILD = '%(levelname)s: [%(child_name)s] %(message_digest)s'
CONSOLE_FILTER_SCOPE = 1000

logger = None
_log_level = DEFAULT_LOG_LEVEL
_force_debug_log_level = None

_log_level_dict = {'DEBUG': logging.DEBUG,
                   'INFO': logging.INFO,
                   'WARNING': logging.WARNING,
                   'ERROR': logging.ERROR,
                   'CRITICAL': logging.CRITICAL}


class ParsimLogFilter(logging.Filter):

    def __init__(self, name='', scope=1):
        super().__init__(name)
        self.rank = len(name.split('.'))
        self.scope = scope

    def filter(self, record):
        name_parts = record.name.split('.')
        record_rank = len(name_parts)
        record.child_path = ''
        record.child_name = ''
        if self.nlen == 0:
            accept = True
        elif self.name == record.name:
            accept = True
        elif record.name.find(self.name, 0, self.nlen) != 0:
            accept = False
        elif (record.name[self.nlen] != "."):
            accept = False
        elif record_rank - self.rank > self.scope:
            accept = False
        else:
            accept = True
            record.child_path = '.'.join(name_parts[self.rank:])
            record.child_name = name_parts[-1]
        return accept


class ParsimLogFormatter(logging.Formatter):

    def __init__(self, fmt=None, fmt_child=None, datefmt=None):
        self._fmt_standard = fmt
        self._fmt_child = fmt_child
        super().__init__(fmt=fmt, datefmt=datefmt)

    def uses_message_digest(self):
        return self._fmt.find("%(message_digest)") >= 0

    def format(self, record):
        if record.child_path:
            self._fmt = self._fmt_child
        else:
            self._fmt = self._fmt_standard
        if self.uses_message_digest():
            record.message_digest = record.getMessage().split('\n')[0]
        return super().format(record)


def init_root_logger(fmt=CONSOLE_FMT, fmt_child=CONSOLE_FMT_CHILD,
                     datefmt=TIMESTAMP_FORMAT, log_level=DEFAULT_LOG_LEVEL,
                     filter_scope=CONSOLE_FILTER_SCOPE):
    global logger
    logging.addLevelName(USER_LOG_LEVEL, 'USER')
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(log_level)
    h = logging.StreamHandler()
    h.setFormatter(ParsimLogFormatter(fmt=fmt, fmt_child=fmt_child, datefmt=datefmt))
    h.addFilter(ParsimLogFilter(ROOT_LOGGER_NAME, scope=filter_scope))
    logger.addHandler(h)


def set_log_level(level):
    global _log_level
    assert level.upper() in _log_level_dict
    _log_level = level.upper()
    if logger and not _force_debug_log_level:
        logger.setLevel(_log_level_dict[level.upper()])


def force_debug_log_level():
    global _force_debug_log_level
    if logger:
        _force_debug_log_level = True
        logger.setLevel(_log_level_dict['DEBUG'])


init_root_logger(log_level=_log_level)
