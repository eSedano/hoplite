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
Stub for Random graph partitioner
"""

import hoplitebase

class Random(hoplitebase.HopliteBase):
    """docstring for XML"""
    def __init__(self, parent=None, work_path=None, log=None):
        super(Random, self).__init__('random', parent, work_path, log)
