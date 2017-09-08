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
Polynomial Chaos Expansions signal and noise model.
"""

# ------------------------------------------
# Imports section
# ------------------------------------------
import os
import sys
import copy
import sympy
# -------------------------
sys.dont_write_bytecode = True
# -------------------------

import hoplitebase

# ------------------------------------------

class Cmatrix(hoplitebase.HopliteBase):
    """ C matrix
    """
    def __init__(self, parent=None, work_path=None, log=None):
        super(Cmatrix, self).__init__('cmatrix', parent, work_path, log)

    def legendre(self, order, symbol):
        return [self._legendre_order(o, symbol) for o in xrange(order)]

    def _legendre_order(self, order, symbol):
        num = [[1], [0, 1], [-1, 0, 3], [0, -3, 0, 5], [3, 0, -30, 0, 35],
            [0, 15, 0, -70, 0, 63], [-5, 0, 105, 0, -315, 0, 231],
            [0, -35, 0, 315, 0, -693, 0, 429],
            [35, 0, -1260, 0, 6930, 0, -12012, 0, 6435],
            [0, 315, 0, -4620, 0, 18018, 0, -25740, 0, 12155],
            [-63, 0, 3465, 0, -30030, 0, 90090, 0, -109395, 0, 46189]]
        div = [1, 1, 2, 2, 8, 8, 16, 16, 128, 128, 256]
        coeffs = [sympy.S(float(n)/div[order]) for n in num[order]]

        return sum([val*(symbol**idx) for idx, val in enumerate(coeffs)])

class PolynomialChaos(hoplitebase.HopliteBase):
    """ PolynomialChaos class
    """
    def __init__(self, parent=None, work_path=None, log=None):
        super(PolynomialChaos, self).__init__('polynomialchaos', parent, work_path, log)
        self._polynomials = {}
        self._systemgraph = None

    def compute(self):
        """ Study and compute the polynomials for each node in the system.
        """
        self.debug('polynomialchaos.compute start')

        self._systemgraph = self._parent.systemgraph
        partitions = self._parent.partitioner.get_partitions()
        results = [self._compute(p) for p in partitions]
        self._combine(results)

        self.debug('polynomialchaos.compute end')

    def _compute(self, noises):
        """ Calculates the propagation of polynomials through the nodes adding noise sources to the
        ones listed in the 'noises' parameter.
        """
        pass

    def _combine(self, partials):
        pass

    def _get(self, node_id):
        """ Retrieves the polynomial for a given node, including forcing the computation of
        non-calculated polynomials.
        """

        # If a predecessor was instantiated and then removed, the predecessor slot remains but
        # the ID is set to Null. We need to take that into account when invoking _get(), otherwise
        # we could be getting into some big trouble. Ideally, by the time compute() is called, any
        # empty slot should have been corrected already, but it's just best to cover against the
        # possibility of such an error happening.
        if node_id is None:
            self.fatal('polynomialchaos._get() tried to access a null predecessor.')

        # Every time the polynomial of a node is computed, we store it in the _polynomials
        # dictionary, so that we don't recompute the same elements over and over again.
        if not node_id in self._polynomials:
            # The value of the polynomial is not calculated yet, so calculate i t.
            node = self._systemgraph.node(node_id)
            # A bit of a hack in order to call the appropriate function for the node type.
            self._polynomials[node_id] = {
                'add': self._pce_add,
                'sub': self._pce_sub,
                'const': self._pce_const,
                'mul': self._pce_mul,
                'div': self._pce_div,
                'input': self._pce_input,
                'output': self._pce_output,
                'null': self._pce_null
            }[node['type']](node_id)

        return self._polynomials[node_id]

    def _pce_add(self, node_id):
        """ Compute C = A + B.
        """
        node = self._systemgraph.node(node_id)

        if len(node['predecessors']) == 2:
            # Get the two operands of the ADD function
            op_a = self._get(node['predecessors'][0])
            op_b = self._get(node['predecessors'][1])
            # Define the ADD function as a lambda for simplicity
            add = lambda x: op_a.get(x, sympy.S(0.0)) + op_b.get(x, sympy.S(0.0))
            # Calculate the result of the ADD
            polynomial = {t: add(t) for t in op_a.keys() + op_b.keys()}

            return polynomial

        # If the number of operands is incorrect, give a shout.
        self.fatal('polynomialchaos._pce_add() operation %d does not have two operands.', node_id)

    def _pce_sub(self, node_id):
        """ Compute C = A - B.
        """
        node = self._systemgraph.node(node_id)

        if len(node['predecessors']) == 2:
            # Get the two operands of the SUB function
            op_a = self._get(node['predecessors'][0])
            op_b = self._get(node['predecessors'][1])
            # Define the SUB function as a lambda for simplicity
            sub = lambda x: op_a.get(x, sympy.S(0.0)) - op_b.get(x, sympy.S(0.0))
            # Calculate the result of the SUB
            return {t: sub(t) for t in op_a.keys() + op_b.keys()}

        # If the number of operands is incorrect, give a shout.
        self.fatal('polynomialchaos._pce_sub() operation %d does not have two operands.', node_id)

    def _pce_const(self, node_id):
        """ Generate the PCE format of a constant.
        """
        node = self._systemgraph.node(node_id)

        # Returns the value of the node.
        return {sympy.S(1.0): node['value']}

    def _pce_mul(self, node_id):
        """ Compute C = A x B.
        """
        self.fatal('polynomialchaos._pce_mul() still not implemented.')

    def _pce_div(self, node_id):
        """ Compute C = A / B.
        """
        self.fatal('polynomialchaos._pce_div() still not implemented.')

    def _pce_input(self, node_id):
        """ Generate the PCE format of an input.
        """
        self.fatal('polynomialchaos._pce_input() still not implemented.')

    def _pce_output(self, node_id):
        """ Forward the contents of a single predecessor to the output.
        """
        node = self._systemgraph.node(node_id)

        if len(node['predecessors']) == 1:
            # Get the operand feeding into the output
            return self._get(node['predecessors'][0])

        # If the number of operands is incorrect, give a shout.
        self.fatal('polynomialchaos._pce_output() operation %d does not have only one operand.', node_id)


    def _pce_null(self, node_id):
        """ Forward the contents of a single predecessor to the successor.
        """
        node = self._systemgraph.node(node_id)

        if len(node['predecessors']) == 1:
            # Get the operand feeding into the successor
            return self._get(node['predecessors'][0])

        # If the number of operands is incorrect, give a shout.
        self.fatal('polynomialchaos._pce_null() operation %d does not have only one operand.', node_id)

# --------------------------------------------------------------------------------------------------
#   0    1    1    2    2    3    3    4    4    5    5    6    6    7    7    8    8    9    9    0
#   5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0    5    0
