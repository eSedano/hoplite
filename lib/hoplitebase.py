# --------------------------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Enrique Sedano
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# This file belongs to:
#     __  ______  ____  __    ________________
#    / / / / __ \/ __ \/ /   /  _/_  __/ ____/
#   / /_/ / / / / /_/ / /    / /  / / / __/
#  / __  / /_/ / ____/ /____/ /  / / / /___
# /_/ /_/\____/_/   /_____/___/ /_/ /_____/   (v0.5 . Alpha)
#
#   Module: HopliteBase
#   Description: Base class for HOPLITE objects. Defines several functionalities and functions
#                generic across all modules. Mainly logging functionalities for now.
# --------------------------------------------------------------------------------------------------

''' Defines the base class HopliteBase for HOPLITE objects.
'''
import os
import sys
import logging
# -------------------------
sys.dont_write_bytecode = True
# -------------------------

class HopliteBase(object):
    ''' Base class for HOPLITE objects. Defines several functionalities and functions
    generic across all modules. Mainly logging functionalities for now.
    '''

    def __init__(self, name, work_path=None, log=None):
        # Use current directory unless specified otherwise
        self._work_path = work_path if work_path else os.getcwd()
        # Use provided log if any, otherwise configure from scratch.
        self._log = log if log else name
        if not log:
            self._configure_log(name)
        self._logger = logging.getLogger(self._log)

    def info(self, message, *args):
        '''Shortcut for printing info messages.
        '''
        self._log.info(message, *args)

    def warning(self, message, *args):
        '''Shortcut for printing warning messages.
        '''
        self._log.warning(message, *args)

    def error(self, message, *args):
        '''Shortcut for printing error messages.
        '''
        self._log.error(message, *args)

    def debug(self, message, *args):
        '''Shortcut for printing debug messages.
        '''
        self._log.debug(message, *args)

    def fatal(self, message, *args):
        '''Shortcut for printing error messages. Additionaly, raises an exception.
        '''
        self._log.error(message, *args)
        raise RuntimeError(message % args)

    def _configure_log(self, name):
        '''Configure the log and the output format, both for file-based and shell output.
        '''
        destination = os.path.join(self._work_path, '%s.log' % self._log)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.setLevel(logging.DEBUG)
        # Configure command line logging
        handler = logging.StreamHandler()
        level = logging.INFO
        log_format = '%(name)s - %(message)s'
        self._configure_logger(logger, handler, level, log_format)
        # Configure file logging
        handler = logging.FileHandler(destination, 'w', encoding=None, delay='true')
        level = logging.DEBUG
        log_format = '[%(asctime)s] %(levelname)s - %(message)s'
        date_format = '%Y/%m/%d %H:%M:%S'
        self._configure_logger(logger, handler, level, log_format, date_format)

    @staticmethod
    def _configure_logger(logger, handler, level, log_format, date_format=None):
        """ Configure the given logger with the provided formats.

        Args:
            log (logging.Logger): Logger that is being modified.
            handler (logging.[File|Stream]Handler): Handler to be configured.
            level (logging.LEVEL): Level of verbosity for the logger.
            log_format (str): Format in which the log messages will be printed.
            date_format (str): Format in which the date will be printed in the log.

        Returns:
            Nothing.
        """
        handler.setLevel(level)
        formatter = logging.Formatter(log_format, date_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
