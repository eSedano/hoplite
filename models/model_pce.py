#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import sys
import copy
import time

import sympy
from sympy import Symbol

import os,sys
parentdir = os.path.dirname(__file__)
sys.path.insert(0,parentdir)

import hoplite_utils
from lib import c_matrix
from lib import pce_ops

class model_pce:
  def __init__(self, config, source_config, source, destination, partitioner=None):
    self.partitioner    = partitioner
    self.destination    = destination
    self.order          = config['pce_order']
    self.partition_size = config['pce_partition_size']

    self.clean_source  = source
    self.signal_inputs = source_config.get('inputs', ['i_'+str(i) for i in range(len(source['inputs']))])
    self.input_rvars   = [Symbol(vname) for vname in self.signal_inputs]
    self.input_dists   = source_config.get('distributions', {x: {1.0*x: 1.0} for x in self.input_rvars})

    self.noise_inputs   = []
    self.noise_rvars    = []
    self.noise_wlvars   = []
    self.noise_dists    = {}
    self.noised_outputs = {}

    self.noise_equivs  = {}

    self.num_noises = 0

    self.computed           = False
    self.signal_propagation = None
    self.noised_propagation = None

  def compute(self):
    # # Generate C matrix for clean system.
    # clean_c_matrix = c_matrix.c_matrix(self.input_rvars, self.order)
    # # Propagate signal values.
    # self.signal_propagation = self.propagate(self.clean_source, clean_c_matrix)

    # Generate system graphs with noises
    # We don't want to add noises to the outputs.
    nodes_to_add_noise = [x for x in self.clean_source['nodes'].keys() if not x in self.clean_source['outputs'] and not self.clean_source['nodes'][x]['op'] == 'const']

    # Generate the subsets of noises that will be introduced together.
    if not self.partitioner == None:
      noise_groups = self.partitioner.get_partitions(self.clean_source, nodes_to_add_noise, self.partition_size)
    else: 
      noise_groups = [nodes_to_add_noise]

    print noise_groups

    sys.exit()

    noise_propagations = []
    for group in noise_groups:
      group_graph = copy.deepcopy(self.clean_source)
      self.add_noises_to(group, group_graph)
      # Generate C matrix for each group of random variables.
      noised_c_matrix = c_matrix.c_matrix(self.input_rvars + [self.noise_equivs['n_' + str(v)][0] for v in group], self.order)
      # Propagate the PCE coefficients through the system.
      noise_propagations.append(self.propagate(group_graph, noised_c_matrix))
      print len(noise_propagations)

    for output in self.clean_source['outputs']:
      output_result = {}
      for result in noise_propagations:
        noised_output = result[output]
        output_result = pce_ops.add(output_result, pce_ops.sub(noised_output, self.signal_propagation[output]))
        print '-----:', noised_output
      self.noised_outputs[output] = pce_ops.add(output_result, self.signal_propagation[output])

    self.noise_inputs = sorted(self.noise_inputs, key=lambda x: int(x.split('_')[1]))
    self.noise_rvars  = [self.noise_equivs[x][0] for x in self.noise_inputs]
    self.noise_wlvars = [self.noise_equivs[x][1] for x in self.noise_inputs]

    self.num_noises = len(self.noise_rvars)
    self.computed = True

    for o in self.noised_outputs:
      print o, ':', self.noised_outputs[o]

  def get_noise_mean(self, output, wlv):
    if not self.computed:
      sys.exit("System has not been computed")
    return abs((self.signal_propagation[output][sympy.S(1.0)] - self.noised_outputs[output][sympy.S(1.0)]).subs(zip(self.noise_wlvars, wlv)))

  def get_noise_variance(self, output, wlv):
    if not self.computed:
      sys.exit("System has not been computed")
    result = 0.0
    for i in self.noised_outputs[output]:
      if not i == sympy.S(1.0):
        result += (self.signal_propagation[output].get(i, 0.0) - self.noised_outputs[output].get(i, 0.0))**2
    return (result).subs(zip(self.noise_wlvars, wlv))/3

  # -----------------------------------------------------------------
  # AUXILIAR FUNCTIONS
  # -----------------------------------------------------------------

  # -----------------------------------------------------------------
  # Propagate the PCE coefficients through the system.
  #
  def propagate(self, source, c_matrix):
    nodes = source['nodes']
    propagation = [None] * (max(source['nodes'].keys()) + 1)

    execution_order = hoplite_utils.get_execution_order(nodes)

    for elem in execution_order:
      if nodes[elem]['op'] == 'input':
        propagation[elem] = self.input_dists[self.input_rvars[elem]]
      if nodes[elem]['op'] == 'const':
        propagation[elem] = {sympy.S(1.0):float(nodes[elem]['value'])}
      if nodes[elem]['op'] == 'output':
        propagation[elem] = propagation[nodes[elem]['preds'][0]]
      if nodes[elem]['op'] == 'add':
        propagation[elem] = pce_ops.add(propagation[nodes[elem]['preds'][0]], propagation[nodes[elem]['preds'][1]])
      if nodes[elem]['op'] == 'sub':
        propagation[elem] = pce_ops.sub(propagation[nodes[elem]['preds'][0]], propagation[nodes[elem]['preds'][1]])
      if nodes[elem]['op'] == 'mul':
        propagation[elem] = pce_ops.mul(propagation[nodes[elem]['preds'][0]], propagation[nodes[elem]['preds'][1]], c_matrix)
      if nodes[elem]['op'] == 'noise':
        propagation[elem] = pce_ops.add(propagation[nodes[elem]['preds'][0]], self.noise_dists[nodes[elem]['symbol']])
      if nodes[elem]['op'] == 'div':
        print nodes[elem]
        print propagation[nodes[elem]['preds'][0]]
        print propagation[nodes[elem]['preds'][1]]
        sys.exit()

    return propagation

  def add_noises_to(self, nodes, graph):
    max_id = max(graph['nodes'].keys())
    for n in nodes:
      node_id  = n + max_id + 1
      name     = 'n_' + str(n)
      vSymbol  = Symbol(name)
      wlSymbol = Symbol('wl_' + str(n))

      self.noise_equivs.update({name: [vSymbol, wlSymbol]})

      self.noise_inputs.append(name)
      self.noise_dists.update({vSymbol: {1.0*vSymbol: (2**(-wlSymbol))/2}})

      node = {node_id: {'op': 'noise', 'preds': [n], 'succs': self.clean_source['nodes'][n]['succs'], 'symbol': vSymbol}}

      graph['nodes'].update(node)
      for i in graph['nodes'][n]['succs']:
        graph['nodes'][i]['preds'] = [p if p != n else node_id for p in graph['nodes'][i]['preds']]
      graph['nodes'][n]['succs'] = [node_id]

  def get_signal_mean(self, output):
    if not self.computed:
      sys.exit("System has not been computed")
    return (self.signal_propagation[output][sympy.S(1.0)])

  def get_signal_variance(self, output):
    if not self.computed:
      sys.exit("System has not been computed")
    result = 0.0
    for i in self.signal_propagation[output]:
      if not i == sympy.S(1.0):
        result += self.signal_propagation[output][i]**2
    return result/3
