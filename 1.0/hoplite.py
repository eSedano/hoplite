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

class Hoplite(lib.hoplitebase.HopliteBase):
    """docstring for Hoplite"""
    def __init__(self, work_path=None, log=None):
        super(Hoplite, self).__init__('systemgraph', work_path, log)
        # Graph representing a system. There will always be one.
        self._systemgraph = lib.systemgraph.SystemGraph(work_path, log)
        self._partitioner = None
        self._iointerface = None
        self._snmodel     = None
        self._wloptimiser = None

    @property
    def systemgraph(self):
        return self._systemgraph

    @systemgraph.setter
    def systemgraph(self, value):
        pass

    @systemgraph.deleter
    def systemgraph(self):
        del self._systemgraph

    @property
    def partitioner(self):
        return self._partitioner

    @partitioner.setter
    def partitioner(self, value):
        pass

    @partitioner.deleter
    def partitioner(self):
        del self._partitioner

    @property
    def iointerface(self):
        return self._iointerface

    @iointerface.setter
    def iointerface(self, value):
        pass

    @iointerface.deleter
    def iointerface(self):
        del self._iointerface

    @property
    def snmodel(self):
        return self._snmodel

    @snmodel.setter
    def snmodel(self, value):
        pass

    @snmodel.deleter
    def snmodel(self):
        del self._snmodel

    @property
    def wloptimiser(self):
        return self._wloptimiser

    @wloptimiser.setter
    def wloptimiser(self, value):
        pass

    @wloptimiser.deleter
    def wloptimiser(self):
        del self._wloptimiser

if __name__ == "__main__":

