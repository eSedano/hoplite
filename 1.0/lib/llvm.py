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
Stub for LLVM I/O interface
"""

import hoplitebase

class LLVM(hoplitebase.HopliteBase):
    """docstring for LLVM"""
    def __init__(self, parent=None, work_path=None, log=None):
        super(LLVM, self).__init__('llvm', parent, work_path, log)
