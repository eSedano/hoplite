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
Interface to METIS partitioner
"""

# ------------------------------------------
# Imports section
# ------------------------------------------
import sys
# -------------------------
sys.dont_write_bytecode = True
# -------------------------
import subprocess
import hoplitebase
# ------------------------------------------

class Metis(hoplitebase.HopliteBase):
    """ SystemGraph class
    """
    def __init__(self, parent=None, work_path=None, log=None):
        super(Metis, self).__init__('metis', parent, work_path, log)
        self._check_install()
        self._sg = parent.systemgraph
        self._nodes = None
        self._edges = None

    def get_partitions(self, nodes=None):
        self.debug('metis.get_partitions start')

        self._get_nodes_edges(nodes)
        self._systemgraph_to_metis()
        self._call_metis()
        self._metis_to_systemgraph()

        self.debug('metis.get_partitions end')

    def _check_install(self):
        pass

    def _get_nodes_edges(self, nodes):
        """ Fill the class _nodes and _edges information with the data provided
        """
        nodes = self._sg.keys() if nodes is None else nodes
        self._nodes = nodes
        # Count the number of unique edges in the graph. If edges A->B and B->A appear in the
        # graph, they will be only counted as one.
        self._edges = set([[n, s].sort() for n in nodes for s in self._sg[n].get('successors', [])])

    def _systemgraph_to_metis(self, nodes):
        metis_path = os.path.join(self._work_path, self._config['input_file'])
        # Header
        with open(metis_path ,'w') as metis:
            metis.write('%% Header')
            vertices = len(self._nodes)
            edges = self._count_edges()
            metis.write('%s %s', vertices, edges)

    def _call_metis(self):
        pass

    def _metis_to_systemgraph(self):
        pass

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0