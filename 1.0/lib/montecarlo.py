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
Monte-Carlo signal and noise model.
"""

# ------------------------------------------
# Imports section
# ------------------------------------------
import os
import sys
import copy
import sympy
import graphviz
# -------------------------
sys.dont_write_bytecode = True
# -------------------------

import hoplitebase

# ------------------------------------------

class MonteCarlo(hoplitebase.HopliteBase):
    """Monte-Carlo class
    """
    def __init__(self, parent=None, work_path=None, log=None):
        super(MonteCarlo, self).__init__('montecarlo', parent, work_path, log)
        self._sg = parent.systemgraph

    def dynamic_range(self):
        pass

    def fractional_length(self):
        pass

    def search(self):
        pass

    def _calculate(self, node_id):
#        ['null', 'add', 'sub', 'mul', 'div', 'const', 'input', 'output']
        pass
