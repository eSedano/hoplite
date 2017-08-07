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
        self._systemgraph = lib.systemgraph.SystemGraph(work_path, log)
        self._partitioner = None
        self._iinterface  = None
        self._snmodel     = None
        self._wloptimiser = None

if __name__ == "__main__":

