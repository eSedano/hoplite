#!/usr/bin/env python
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
Main Hoplite class. Doubles as self-executable script
"""
import os
import sys
import argparse

sys.dont_generate_bytecode = True

from inspect import getmembers, isclass

from lib import hoplitebase

class Hoplite(hoplitebase.HopliteBase):
    """docstring for Hoplite"""
    def __init__(self, work_path=None, log=None):
        super(Hoplite, self).__init__('hoplite', work_path=work_path, log=log)

        # Append the lib path to sys.path to allow for dynamic loading of libraries (see _setup())
        sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
        # Graph representing a system. There will always be one.
        self._systemgraph = self._setup('systemgraph')
        self._partitioner = None
        self._iointerface = None
        self._wloptimiser = None
        self._snmodel = None

        # Small tweak (rules are mede to be broken, right?) to add the base path
        # of the installation path to the configuration, in case other resources
        # need it.
        self._config['base_path'] = os.path.dirname(os.path.realpath(__file__))

    def run(self, source, keep=False):
        """ Main HOPLITE function. Invokes the calling sequence, including pre- and post- calls for
        each of the steps.
        """
        # I/O interface - Populate system graph.
        self.iointerface.pre()
        self.iointerface.get_graph(source)

        # Signal/Noise model - Apply the model or prepare it for execution on demand.
        self.snmodel.pre()
        self.snmodel.compute()
        self.snmodel.post()

        # Word-length optimiser - Traverse the solution space in search for an optimised WL vector.
        self.wloptimiser.pre()
        if self.wloptimiser.config.get('single_search_call', False):
            self.wloptimiser.search()
        else:
            self.wloptimiser.dynamic_range()
            self.wloptimiser.fractional_length()
        self.wloptimiser.post()

        self.iointerface.get_wl()
        self.iointerface.post()

        if not keep:
            self.snmodel.cleanup()
            self.iointerface.cleanup()
            self.wloptimiser.cleanup()
            self.partitioner.cleanup()

    # ------------------------------------------
    # System Graph (Property, Setter and Getter)
    # ------------------------------------------
    @property
    def systemgraph(self):
        return self._systemgraph

    @systemgraph.setter
    def systemgraph(self, value):
        pass

    @systemgraph.deleter
    def systemgraph(self):
        del self._systemgraph
    # ------------------------------------------

    # ------------------------------------------
    # Input/Output Interface (Property, Setter and Getter)
    # ------------------------------------------
    @property
    def iointerface(self):
        """ Input/Output Interface
        """
        return self._iointerface

    # The setter is a bit convoluted, but for a good reason. The first step is to determine
    # if the module that the user is trying to load is in the list of the permitted ones.
    # It would have been better to do this during the parseargs stage, but we don't have
    # the information of the available list at that time. Only once we have instantiated
    # the Hoplite object we have it, so we delegate the checking task to here.
    #
    # If no module was specified, we want to load the default silently.
    @iointerface.setter
    def iointerface(self, value):
        if value not in self._config['io_interface_tools']:
            if not value:
                # Raise exception silently, without triggering an error message.
                raise hoplitebase.HopliteError('Silent exception')
            self.fatal('I/O interface %s not recognised.', value)
        self._iointerface = self._setup(value)

    @iointerface.deleter
    def iointerface(self):
        del self._iointerface
    # ------------------------------------------

    # ------------------------------------------
    # Signal/Noise Model (Property, Setter and Getter)
    # ------------------------------------------
    @property
    def snmodel(self):
        """ Signal/Noise Model
        """
        return self._snmodel

    @snmodel.setter
    def snmodel(self, value):
        if value not in self._config['sn_model_tools']:
            if not value:
                # Raise exception silently, without triggering an error message.
                raise hoplitebase.HopliteError('Silent exception')
            self.fatal('Signal/Noise %s not recognised.', value)
        self._snmodel = self._setup(value)

    @snmodel.deleter
    def snmodel(self):
        del self._snmodel
    # ------------------------------------------

    # ------------------------------------------
    # Word-length Optimisation Algorithm (Property, Setter and Getter)
    # ------------------------------------------
    @property
    def wloptimiser(self):
        """ WOrd-length Optimiser
        """
        return self._wloptimiser

    @wloptimiser.setter
    def wloptimiser(self, value):
        if value not in self._config['wl_optimiser_tools']:
            if not value:
                # Raise exception silently, without triggering an error message.
                raise hoplitebase.HopliteError('Silent exception')
            self.fatal('Word-length optimiser %s not recognised.', value)
        self._wloptimiser = self._setup(value)

    @wloptimiser.deleter
    def wloptimiser(self):
        del self._wloptimiser
    # ------------------------------------------

    # ------------------------------------------
    # Partitioner algorithm (Property, Setter and Getter)
    # ------------------------------------------
    @property
    def partitioner(self):
        """ Partitioner algorithm
        """
        return self._partitioner

    @partitioner.setter
    def partitioner(self, value):
        if value not in self._config['partitioner_tools']:
            if not value:
                # Raise exception silently, without triggering an error message.
                raise hoplitebase.HopliteError('Silent exception')
            self.fatal('Partitioner %s not recognised.', value)
        self._partitioner = self._setup(value)

    @partitioner.deleter
    def partitioner(self):
        del self._partitioner
    # ------------------------------------------

    # ------------------------------------------
    # Dynamic module loader
    # ------------------------------------------
    def _setup(self, name):
        """ Dymanic module loader. It automatically looks for the appropriate module in
        the lib folder, loads the module and returns an instance of the class so that it can
        be called to instantiate the corresponding object.
        """

        # This is a powerful method that allows designers to simply include new modules in
        # the lib directory to expand the functionality of HOPLITE with new tools while, at
        # the same time, requiring minimal changes (if any) to the original codebase in order
        # to give support to it in the flow.

        # Import the module into the system
        module = __import__(name)
        #FFund the class that matches the module name
        classes = [m[0] for m in getmembers(module, isclass) if m[1].__module__ == name]
        try:
            classname = [n for n in classes if n.lower() == name][0]
        except IndexError:
            self.fatal('Module %s does not have a class to match its name.', name)
        # Return an object of the indicated module.
        return getattr(module, classname)(parent=self, work_path=self._work_path, log=self._log)

# Behaviour when HOPLITE is invoked as a script
if __name__ == "__main__":

    # -----------------------------------------------------------------
    # Parse arguments from input and configure help info.
    #
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        'source',
        type=str,
        help='Absolute path to the source definition of the function to analyze.'
    )
    PARSER.add_argument(
        '-w', '--work_path',
        type=str,
        default=os.getcwd(),
        help='Path to the work folder.'
    )
    PARSER.add_argument(
        '-k', '--keep',
        action='store_true',
        help='Keeps the intermediate generated files, if any.'
    )
    PARSER.add_argument(
        '-o', '--output',
        type=str,
        help='Path to the destination folder.'
    )
    PARSER.add_argument(
        '-i', "--iointerface",
        type=str,
        help='Input tool that will generate the system graph.'
    )
    PARSER.add_argument(
        '-m', '--snmodel',
        type=str,
        help='Analytical or simulation signal and noise model for the system.'
    )
    PARSER.add_argument(
        '-p', '--partitioner',
        type=str,
        help='Indicates the type of partitioner, if needed, the system will use.'
    )
    PARSER.add_argument(
        '-l', '--wloptimiser',
        type=str,
        help='Indicates the word-lenght optimiser for the system.'
    )
    ARGS = PARSER.parse_args()
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Instantiate HOPLITE object.
    #
    ACHILLES = Hoplite(ARGS.work_path)
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Load HOPLITE components. If the specified component fails, fall
    # back to loading the default one.
    #
    # Input/Output interface
    try:
        ACHILLES.iointerface = ARGS.iointerface
    except hoplitebase.HopliteError:
        DEFAULT = ACHILLES.config['io_interface_tools'][0]
        ACHILLES.info('Loading default I/O interface %s', DEFAULT)
        ACHILLES.iointerface = DEFAULT

    #  Signal/Noise model
    try:
        ACHILLES.snmodel = ARGS.snmodel
    except hoplitebase.HopliteError:
        DEFAULT = ACHILLES.config['sn_model_tools'][0]
        ACHILLES.info('Loading default Signal/Noise model %s', DEFAULT)
        ACHILLES.snmodel = DEFAULT

    # Word-length optimiser
    try:
        ACHILLES.wloptimiser = ARGS.wloptimiser
    except hoplitebase.HopliteError:
        DEFAULT = ACHILLES.config['wl_optimiser_tools'][0]
        ACHILLES.info('Loading default Word-length optimiser %s', DEFAULT)
        ACHILLES.wloptimiser = DEFAULT

    # Graph partitioner
    try:
        ACHILLES.partitioner = ARGS.partitioner
    except hoplitebase.HopliteError:
        DEFAULT = ACHILLES.config['partitioner_tools'][0]
        ACHILLES.info('Loading default partitioner %s', DEFAULT)
        ACHILLES.partitioner = DEFAULT
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Proceed with the calling sequence.
    #
    ACHILLES.run(ARGS.source, ARGS.keep)
    print ACHILLES.systemgraph
    # -----------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0
