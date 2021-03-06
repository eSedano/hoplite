#
# --------------------------------------------------------------------------------------------------
#     __  ______  ____  __    ________________
#    / / / / __ \/ __ \/ /   /  _/_  __/ ____/
#   / /_/ / / / / /_/ / /    / /  / / / __/
#  / __  / /_/ / ____/ /____/ /  / / / /___
# /_/ /_/\____/_/   /_____/___/ /_/ /_____/   (v1.0 . Achilles)
#
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# --------------------------------------------------------------------------------------------------
"""
Base class for all Hoplite classes
"""
import os
import sys
import copy
import logging
import yaml
# -------------------------
sys.dont_write_bytecode = True
# -------------------------

# By setting the environment variable HOPLITE_DEBUG, debugging is enabled in the log.
# LOGGING_LEVEL = logging.DEBUG if os.getenv('HOPLITE_DEBUG', False) else logging.INFO
# TODO: Uncomment line above, remove line below once development is done
LOGGING_LEVEL = logging.DEBUG

class HopliteError(Exception):
    """ Custom exception for Hoplite.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class HopliteBase(object):
    """ Base class for HOPLITE objects. Defines several functionalities and functions
    generic across all modules. Mainly logging functionalities for now.
    """

    def __init__(self, name, parent=None, work_path=None, log=None):
        # Use current directory unless specified otherwise
        self._work_path = work_path if work_path else os.getcwd()
        if not os.path.exists(self._work_path):
            os.makedirs(self._work_path)
        # Use provided log if any, otherwise configure from scratch.
        self._log = log if log else name
        self._configure_log(self._log)
        self._logger = logging.getLogger(self._log)
        self._parent = parent
        self._config = self._load_config(name)

    def info(self, message, *args):
        """ Shortcut for printing info messages.
        """
        self._logger.info(message, *args)

    def warning(self, message, *args):
        """ Shortcut for printing warning messages.
        """
        self._logger.warning(message, *args)

    def error(self, message, *args):
        """ Shortcut for printing error messages.
        """
        self._logger.error(message, *args)

    def debug(self, message, *args):
        """ Shortcut for printing debug messages.
        """
        self._logger.debug(message, *args)

    def fatal(self, message, *args):
        """ Shortcut for printing error messages. Additionaly, raises an exception.
        """
        self._logger.error(message, *args)
        raise HopliteError(message % args)

    def pre(self):
        """ Pre-call step for HOPLITE modules.
        """
        pass

    def post(self):
        """ Post-call step for HOPLITE modules.
        """
        pass

    def cleanup(self):
        """ Cleanup stub for HOPLITE modules.
        """
        pass

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        pass # Writes to config are ignored.

    @config.deleter
    def config(self):
        del self._config

    def _configure_log(self, name):
        """Configure the log and the output format, both for file-based and shell output.
        """
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
        handler = logging.FileHandler(destination, 'a', encoding=None, delay='true')
        level = LOGGING_LEVEL
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
        """
        handler.setLevel(level)
        formatter = logging.Formatter(log_format, date_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def _load_config(self, name):
        """ Loads the config file of the class.
        """
        # The .hop file must be on the same folder as the source .py file. Look for it and parse
        # its contents as a YAML file.
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '%s.hop' % name)
        if not os.path.exists(config_path):
            self.debug('%s._load_config() does not have associated .hop file', name)
            return {}
        with open(config_path, 'r') as stream:
            # Beware, if something is wrong with the file (for example bad YAML formatting) this
            # will explode big time.
            config = yaml.load(stream)
        return config

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0
