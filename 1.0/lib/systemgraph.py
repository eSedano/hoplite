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
Representation of the system to be studied, modified and optimised by the tool.

The order of the predecessors matter!
"""

# ------------------------------------------
# Imports section
# ------------------------------------------
import sys
import sympy
# -------------------------
sys.dont_write_bytecode = True
# -------------------------

import hoplitebase

# ------------------------------------------

# There are certain types of nodes that are supported by SystemGraph.
# In general, unsupported nodes will default to the first element in this list.
# So please, if you are adding new nodes, do not add them to the beginning of the list.
SUPPORTED_OPERATIONS = ['null', 'add', 'sub', 'mul', 'div', 'const', 'input', 'output']

class SystemGraph(hoplitebase.HopliteBase):
    """ SystemGraph class
    """
    def __init__(self, log='systemgraph'):
        super(SystemGraph, self).__init__(log)
        self._node_id = 0
        self._nodes = {}

    # ------------------------------------------
    # Auto-incremental ID property for new nodes
    # ------------------------------------------
    @property
    def node_id(self):
        """ node_id is an auto-incremental ID property which is polled by SystemGraph every time it
        has to assign an ID to a new node being added to the graph. Polling it from outside is
        harmless, but not recommended. Any attempts at writing a specific value to node_id will be
        ignored, as doing otherwise could cause duplicated IDs, which is forbidden by design.
        """
        old_id = self._node_id
        self.debug('systemgraph.property.node_id: %d', old_id)
        self._node_id += 1
        return old_id

    @node_id.setter
    def node_id(self, value):
        pass # Writes to node_id are ignored.

    @node_id.deleter
    def node_id(self):
        del self._node_id # Resetting the ID attribute can only be achieved by deleting it.
    # ------------------------------------------

    # ------------------------------------------
    # Public operations of SystemGraph
    # ------------------------------------------
    def insert_node(self, operation, value=None):
        """ Introduces a new node of the indicated operation in the system graph. If the
        operation is a constant, the insertion additionally requires a value to be specified.
        Any value passed to the insertion for non-constant operation will be ignored.
        """
        self.debug('systemgraph.insert_node start')

        # Request a new unique ID for the node to generate
        node_id = self.node_id

        # Check that the operation to insert is supported by the graph
        if not operation in SUPPORTED_OPERATIONS:
            self.warning('Operation type not supported, defaults to %s', SUPPORTED_OPERATIONS[0])
            operation = SUPPORTED_OPERATIONS[0]

        # Generate the dictionary that represents the node.
        # Contents of the dictionary are:
        # +===================+===============+==================================================+
        # | Field             | Type          | Comments                                         |
        # +===================+===============+==================================================+
        # | type              | String        | -                                                |
        # +-------------------+---------------+--------------------------------------------------+
        # | id                | Integer       | Unique for each node in the graph.               |
        # +-------------------+---------------+--------------------------------------------------+
        # | value             | sympy.S       | Only present for 'const' nodes.                  |
        # +-------------------+---------------+--------------------------------------------------+
        # | predecessors      | List(Integer) | Not present for 'const' or 'input' nodes.        |
        # |                   |               | Number and interpretation of the elements in the |
        # |                   |               | list are dependent on each type of node.         |
        # +-------------------+---------------+--------------------------------------------------+
        # | successors        | List(Integer) | Not present for 'output' nodes.                  |
        # +===================+===============+==================================================+
        node = {
            'type': operation,
            'id': node_id
        }
        if operation not in ['input', 'const']:
            node['predecessors'] = []
        if operation not in ['output']:
            node['successors'] = []
        if operation in ['const']:
            # Transform the value of the constant to the internal sympy representation.
            # While doing this, we check that the value argument is provided and it is valid.
            try:
                node['value'] = sympy.S(float(value))
            except ValueError:
                self.fatal('systemgraph.insert_node() argument cannot be converted to float')
            except TypeError:
                self.fatal('systemgraph.insert_node() argument is null or of an invalid type')
            except Exception, message:
                self.fatal('systemgraph.insert_node() %s', message)

        self.debug('systemgraph.insert_node: %s', str(node))
        # Add the node to the graph.
        self._nodes[node_id] = node

        self.debug('systemgraph.insert_node end')

        return node_id

    def insert_edge(self, source, destination, append=True):
        """ Connects two nodes with a directed edge. If append is set to False, the function
        will fill the first None spot in the predecessors list of the destination instead of
        adding the connection at the end of the list.
        """
        self.debug('systemgraph.insert_edge start')
        # Check that both source and destination exist in the graph
        try:
            end = 'source'
            s_node = self._nodes[source]
            end = 'destination'
            d_node = self._nodes[destination]
        except KeyError:
            self.fatal('systemgraph.insert_edge() %s node unknown', end)

        # Check that both source and destination can be used as such
        if s_node['type'] in ['output']:
            self.fatal('systemgraph.insert_edge() adding %s %d as source of an edge', s_node['type'], source)
        if d_node['type'] in ['input', 'const']:
            self.fatal('systemgraph.insert_edge() adding %s %d as destination of an edge', d_node['type'], source)

        # Connect source and destination
        s_node['successors'].append(destination)
        # If the function does not append, it searches for the first appearance of None in
        # the predecessors list of the destination. If it finds one, it connects the source
        # there. In any other case (None not present or append being true), the node is added
        # at the end of the predecessors list.
        if not append:
            try:
                d_node['predecessors'][d_node['predecessors'].index(None)] = source
            except ValueError:
                d_node['predecessors'].append(source)
        else:
            d_node['predecessors'].append(source)

        self.debug('systemgraph.insert_edge end')

    def remove_node(self, node_id):
    	""" Removes a node from the graph.
    	"""
    	self.debug('systemgraph.remove_node start')
    	# Check that the node is in the graph.
    	if node_id not in self._nodes:
    		self.fatal('systemgraph.remove_node() node %d not in the graph', node_id)

    	node = self._nodes[node_id]

    	# Remove all the edges connected to the node to remove
    	_ = [self.remove_edge(p, node_id) for p in node.get('predecessors', [])]
    	_ = [self.remove_edge(node_id, s) for s in node.get('successors', [])]

    	# Remove the node itself
    	del self._nodes[node_id]

    	self.debug('systemgraph.remove_node end')

    def remove_edge(self, source, destination):
        """ Removes the egde between two nodes.
        """
        self.debug('systemgraph.remove_edge start')
        # Check that both source and destination exist in the graph
        try:
            end = 'source'
            s_node = self._nodes[source]
            end = 'destination'
            d_node = self._nodes[destination]
        except KeyError:
            self.fatal('systemgraph.remove_edge() %s node unknown', end)

        # Check that the connection between the two nodes exists
        if not destination in s_node.get('successors', []):
            self.fatal('systemgraph.remove_edge() %d is not a successor of %d', destination, source)
        if not source in d_node.get('predecessors', []):
            self.fatal('systemgraph.remove_edge() %d is not a predecessor of %d', source ,destination)

        # The first appearance of the node in the successors list of the source is eliminated, as
        # order is irrelevant in this case.
        s_node['successors'].remove(destination)

        # The first appearance of the node in the predecessors list of the destination is replaced
        # by None, as the order in the case of the predecessors list is extremely relevant.
        d_node['predecessors'][d_node['predecessors'].index(source)] = None

        self.debug('systemgraph.remove_edge end')

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0
