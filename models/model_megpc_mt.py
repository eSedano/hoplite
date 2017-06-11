#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import os
import sys
import copy
import time
import random
import scipy
import sympy
import pickle
import threading

from sympy import Symbol
from scipy import linalg

sys.dont_write_bytecode = True

parentdir = os.path.dirname(__file__)
sys.path.insert(0,parentdir)

import hoplite_utils
from lib import c_matrix
from lib import pce_ops

from itertools import product

class model_megpc_mt:
  def __init__(self, config, source_config, source, destination, partitioner=None):
    self.partitioner    = partitioner
    self.destination    = destination
    self.order          = config['megpc_order']
    self.partition_size = config['megpc_partition_size']
    self.j_lim          = config['megpc_j_lim']
    self.theta_1        = config['megpc_theta_1']
    self.theta_2        = config['megpc_theta_2']
    self.alpha          = config['megpc_alpha']

    self.original_source = source

    self.signal_inputs  = source_config.get('inputs', ['i_'+str(i) for i in range(len(source['inputs']))])
    self.input_rvars    = [Symbol(vname) for vname in self.signal_inputs]
    self.input_to_rvars = {source['inputs'][i]: self.input_rvars[i] for i in range(len(self.signal_inputs))}
    self.input_dists    = source_config.get('distributions', {x: {1.0*x: 1.0} for x in self.input_rvars})

    self.clean_c_matrix = c_matrix.c_matrix(self.input_rvars, self.order)

    self.noised_expectances = {}

    self.noise_inputs   = []
    self.noise_rvars    = []
    self.noise_wlvars   = []
    self.noise_dists    = {}

    self.noise_equivs  = {}

    self.clean_results  = []
    self.clean_mean     = []
    self.clean_variance = []

    self.noised_results = []
    self.noise_mean     = []
    self.noise_variance = []

    self.computed = False

    self.num_noises = 0
    self.outputs = source['outputs']

    self.solution_files = {}

    self.mutex = threading.Lock()

    self.dump_files = os.path.join(destination, 'dump_files')
    if not os.path.exists(self.dump_files): os.makedirs(self.dump_files)

  def compute(self):
    backup_files = [os.path.join(self.dump_files, x) for x in os.listdir(self.dump_files) if x.startswith('solution_')]

    if backup_files:
      print 'Found backup files, skipping processing.'
      self.solution_files = {x: backup_files[x] for x in range(len(backup_files))}
      with open(os.path.join(self.dump_files, 'noise_info'), 'r') as noin:
        noise_bundle = pickle.load(noin)
        self.noised_expectances = noise_bundle['expectances']
        self.noise_inputs       = noise_bundle['inputs']
        self.noise_rvars        = noise_bundle['rvars']
        self.noise_wlvars       = noise_bundle['wlvars']
        self.noise_dists        = noise_bundle['dists']
        self.noise_equivs       = noise_bundle['equivs']
        self.num_noises         = noise_bundle['num']
    else:
      execution_paths = self.get_execution_paths()
      with open(os.path.join(self.dump_files, 'execution_paths'), 'w') as exe:
        pickle.dump(execution_paths, exe)

      self.noised_results = []
      if len(execution_paths) == 1:
        domain = {'coeffs': self.input_dists,
                  'domain': {self.input_to_rvars[x]: (-1.0, 1.0) for x in execution_paths[0]['path']['inputs']},
                  'j_k': 1.0}

        domain_solutions = self.apply_model(execution_paths[0], domain)

        for solution in domain_solutions:
          pickle_file = os.path.join(self.dump_files, 'solution_0')
          with open(pickle_file, 'w') as sol:
            pickle.dump(solution, sol)
            self.solution_files.update({(0,): pickle_file})
        noise_bundle = {
          'expectances': self.noised_expectances,
          'inputs':      self.noise_inputs,
          'rvars':       self.noise_rvars,
          'wlvars':      self.noise_wlvars,
          'dists':       self.noise_dists,
          'equivs':      self.noise_equivs,
          'num':         self.num_noises,
        }
        with open(os.path.join(self.dump_files, 'noise_info'), 'w') as noin:
          pickle.dump(noise_bundle, noin)
      else:
        # subdomains_by_decisions will retain all the information on which
        #  subdomain corresponds to which chain of decisions. It will store
        #  all the necessary levels of decisions, so none is missing and
        #  each level of decisions only has to be calculated once.
        #  This loop will prepare the data structure to allow insertion later.
        subdomains_by_decisions = {}
        for path in execution_paths:
          decisions_tuple = tuple(path['decisions'].keys())
          subdomains_by_decisions[decisions_tuple] = {}
          for decision in [x for x in product([False,True], repeat=len(path['decisions']))
                            if x in [tuple(z['decisions'].values()) for z in execution_paths]]:
            subdomains_by_decisions[decisions_tuple][decision] = None

        # Process each of the execution paths. First, calculate their subdomains.
        #  Then, propagate the PCEs for clean signal, add noises and propagate for
        #  the quantized system. Finally, combine the results to get the actual 
        #  solutions.
        i = 1
        for path in execution_paths:
          self.mutex.acquire()
          print "Calculating subdomains information for partition %d out of %d" % (i, len(execution_paths))
          print "Path", path['decisions']
          self.mutex.release()
          # Step 1: Find all the partitions for the current decision tree.
          subdomains_by_decisions = self.partition_conditional(path, subdomains_by_decisions)

          # Step 2: Take the list of subdomains for the current decision and propagate
          #  the coefficients as a regular PCE.
          j = 1
          len_subdomains = len(subdomains_by_decisions[tuple(path['decisions'].keys())][tuple(path['decisions'].values())])
          for domain in subdomains_by_decisions[tuple(path['decisions'].keys())][tuple(path['decisions'].values())]:
            self.mutex.acquire()
            print "Propagating values for subdomain (%d) %d out of %d" % (i, j, len_subdomains)
            self.mutex.release()
            t = threading.Thread(target=self.apply_model, args=(path, domain, i, j))
            t.start()
            j += 1
          while threading.active_count() > 1:
            self.mutex.acquire()
            print '{} threads on flight computing ME-gPC propagations.'.format(threading.active_count() - 1)
            self.mutex.release()
            time.sleep(120)
          i += 1
        noise_bundle = {
          'expectances': self.noised_expectances,
          'inputs':      self.noise_inputs,
          'rvars':       self.noise_rvars,
          'wlvars':      self.noise_wlvars,
          'dists':       self.noise_dists,
          'equivs':      self.noise_equivs,
          'num':         self.num_noises,
        }
        with open(os.path.join(self.dump_files, 'noise_info'), 'w') as noin:
          pickle.dump(noise_bundle, noin)

    # Step 3: Compute results
    output_sum_clean_mean     = {o: sympy.S(0.0) for o in self.original_source['outputs']}
    output_sum_clean_variance = {o: sympy.S(0.0) for o in self.original_source['outputs']}
    output_sum_noised_mean    = {o: sympy.S(0.0) for o in self.original_source['outputs']}
  
    for s in self.solution_files:
      with open(self.solution_files[s], 'r') as sol:
        sol_info = pickle.load(sol)
        for o in self.original_source['outputs']:
          output_sum_clean_mean[o]     += sol_info['clean_outputs'][o].get(sympy.S(1.0), 0.0)*sol_info['j_k']
          output_sum_clean_variance[o] += sum([(sol_info['clean_outputs'][o][x]**2)*sol_info['j_k']*self.clean_c_matrix.expectances[x] for x in sol_info['clean_outputs'][o]])
          output_sum_noised_mean[o]    += sol_info['noised_outputs'][o].get(sympy.S(1.0), 0.0)*sol_info['j_k']

    print 'Calculating means and clean variance.'

    self.clean_mean     = [output_sum_clean_mean[x] for x in self.original_source['outputs']]
    self.clean_variance = [output_sum_clean_variance[x] for x in self.original_source['outputs']]
    self.noise_mean     = [output_sum_noised_mean[x] for x in self.original_source['outputs']]

    self.num_noises = len(self.noise_wlvars)
    self.computed = True

  # get_noise_mean(output, wlv)
  #
  # Computes the mean noise value for the indicated output signal
  #  for the given WordLength Vector. Caution, this function returns
  #  the mean value that doesn't include the mean of the clean signal.
  #  To get the complete mean value, the clean signal one has to be
  #  added.
  #
  def get_noise_mean(self, wlv, output=None):
    if not self.computed:
      sys.exit("System has not been computed")
    if output is None:
      return [n.subs(zip(self.noise_wlvars, wlv)) for n in self.noise_mean]
    else:
      return self.noise_mean[self.original_source['outputs'].index(output)].subs(zip(self.noise_wlvars, wlv))

  # get_noise_variance(output, wlv)
  #
  # Computes the noise variance value of the indicated output signal
  #  for the given WordLength Vector.
  #
  def get_noise_variance(self, wlv, output=None):
    if not self.computed:
      sys.exit("System has not been computed")

    print 'Requested noise variance for:'
    print wlv

    zipped = zip(self.noise_wlvars, wlv)

    if not output is None:
      output_sum_noise_variance = sympy.S(0.0)
      for s in self.solution_files:
        with open(self.solution_files[s], 'r') as sol:
          sol_info = pickle.load(sol)

          output_sum_noise_variance += sum([((sol_info['noised_outputs'][output][x]**2)*sol_info['j_k']*self.noised_expectances[x]).subs(zipped) for x in sol_info['noised_outputs'][output]])

      print 'Gonna return {}'.format(str(output_sum_noise_variance))
      return output_sum_noise_variance
    else:
      output_sum_noise_variance = {o: sympy.S(0.0) for o in self.original_source['outputs']}

      for s in self.solution_files:
        with open(self.solution_files[s], 'r') as sol:
          sol_info = pickle.load(sol)
          for o in self.original_source['outputs']:
            output_sum_noise_variance[o] += sum([((sol_info['noised_outputs'][o][x]**2)*sol_info['j_k']*self.noised_expectances[x]).subs(zipped) for x in sol_info['noised_outputs'][o]])

      print 'Gonna return:'
      print [output_sum_noise_variance[x] for x in self.original_source['outputs']]
      return [output_sum_noise_variance[x] for x in self.original_source['outputs']]

  # -----------------------------------------------------------------
  # AUXILIAR FUNCTIONS
  # -----------------------------------------------------------------

  # propagate(source, c_matrix)
  #
  # Propagates the PCE coefficients through the system.
  #
  def propagate(self, source, dists, c_matrix):
    propagation = [None] * (max(source.keys()) + 1)

    execution_order = hoplite_utils.get_execution_order(source)

    for elem in execution_order:
      if source[elem]['op'] == 'input':
        propagation[elem] = dists[self.input_rvars[elem]]
      if source[elem]['op'] == 'const':
        propagation[elem] = {sympy.S(1.0):float(source[elem]['value'])}
      if source[elem]['op'] == 'output':
        propagation[elem] = propagation[source[elem]['preds'][0]]
      if source[elem]['op'] == 'add':
        propagation[elem] = pce_ops.add(propagation[source[elem]['preds'][0]], propagation[source[elem]['preds'][1]])
      if source[elem]['op'] == 'sub':
        propagation[elem] = pce_ops.sub(propagation[source[elem]['preds'][0]], propagation[source[elem]['preds'][1]])
      if source[elem]['op'] == 'mul':
        propagation[elem] = pce_ops.mul(propagation[source[elem]['preds'][0]], propagation[source[elem]['preds'][1]], c_matrix)
      if source[elem]['op'] == 'noise':
        propagation[elem] = pce_ops.add(propagation[source[elem]['preds'][0]], self.noise_dists[source[elem]['symbol']])

    return propagation

  # add_noises_to(nodes, graph)
  #
  # Insert noise nodes in the indicated nodes of the graph. The current
  #  behaviour is to add the noises at the output of the node. That
  #  means that the optimization will not be the most optimal, but
  #  it reduces the search space and simplifies the gathering of
  #  information at the end of the process.
  #
  def add_noises_to(self, nodes, graph):
    max_id = max(graph['nodes'].keys())
    for n in nodes:
      node_id  = n + max_id + 1
      name     = 'n_' + str(n)
      vSymbol  = Symbol(name)
      wlSymbol = Symbol('wl_' + str(n))
      
      self.mutex.acquire()
      if not name in self.noise_equivs:
        self.noise_equivs.update({name: [vSymbol, wlSymbol]})
        self.noise_inputs.append(name)
        self.noise_dists.update({vSymbol: {1.0*vSymbol: (2**(-wlSymbol))/2}})
      self.mutex.release()

      node = {node_id: {'op': 'noise', 'preds': [n], 'succs': graph['nodes'][n]['succs'], 'symbol': vSymbol}}

      graph['nodes'].update(node)
      for i in graph['nodes'][n]['succs']:
        graph['nodes'][i]['preds'] = [p if p != n else node_id for p in graph['nodes'][i]['preds']]
      graph['nodes'][n]['succs'] = [node_id]

    self.mutex.acquire()
    self.noise_inputs = sorted(self.noise_inputs, key=lambda x: int(x.split('_')[1]))
    self.noise_rvars  = [self.noise_equivs[x][0] for x in self.noise_inputs]
    self.noise_wlvars = [self.noise_equivs[x][1] for x in self.noise_inputs]
    self.mutex.release()

  # get_signal_mean(output)
  #
  # Computes the mean value of the indicated output signal.
  #
  def get_signal_mean(self, output=None):
    if not self.computed:
      sys.exit("System has not been computed")
    if output is None:
      return self.clean_mean
    else:
      return self.clean_mean[self.original_source['outputs'].index(output)]

  # get_signal_variance(output)
  #
  # Computes the variance value of the indicated output signal.
  #
  def get_signal_variance(self, output=None):
    if not self.computed:
      sys.exit("System has not been computed")
    if output is None:
      return self.clean_variance
    else:
      return self.clean_variance[self.original_source['outputs'].index(output)]

  # get_execution_paths()
  #
  # Goes over the system graph several times getting the different execution
  #  paths in it. It takes care of generating the paths, elimiating the dead
  #  code and annotating the dependence chains of the different flow-control
  #  nodes so that we can later compute the probabilities of each path.
  #
  # It truly does a lot of things.
  #
  def get_execution_paths(self):
    # Get all the BBs that have a conditional branch and, thus, a fork.
    all_branches = [x for x in self.original_source['nodes'] if self.original_source['nodes'][x]['op'] == 'br']
    cond_branches = [x for x in all_branches if not self.original_source['nodes'][self.original_source['nodes'][x]['preds'][0]]['cmp'] in ['TRUE', 'FALSE']]
    cond_cmps = [self.original_source['nodes'][x]['preds'][0] for x in cond_branches]

    forks = {}
    for c in cond_branches:
      for bb in self.original_source['bbs']:
        if c in self.original_source['bbs'][bb]['nodes']: forks[bb] = self.original_source['bbs'][bb]['succs']
    
    # Generate all the possible path combinations.
    choices = product([0,1], repeat=len(forks))
    forks_list = sorted(forks.keys())

    # Generate all the possible paths, selecting only one of the two
    #  directions in each of the forks in the system graph.
    paths = []
    for c in choices:
      lc = list(c)
      new_path = copy.deepcopy(self.original_source)

      # Step 1: Transform all forks in execution paths into
      #  univocal paths by leaving every BB with just one
      #  successor.
      for f in range(len(forks_list)):
        s = new_path['bbs'][forks_list[f]]['succs'][lc[f]]
        del new_path['bbs'][forks_list[f]]['succs'][lc[f]]
        if s in new_path['bbs'][0]['succs']:
          del new_path['bbs'][0]['succs'][new_path['bbs'][0]['succs'].index(s)]

      # At this point, only Basic Block successors information is
      #  reliable. The predecessors info has to be corrected, and
      #  the branch and phi nodes will dissapear since now they
      #  will always go to and come from the same path.

      # Step 2: Clear all predecessors information from the BBs.
      for bb in new_path['bbs']:
        new_path['bbs'][bb]['preds'] = []

      # Step 3: Rebuild the precessors info with the successors one.
      for bb in new_path['bbs']:
        for bs in new_path['bbs'][bb]['succs']:
          new_path['bbs'][bs]['preds'].append(bb)

      # Step 4: Eliminate all unreachable BBs. That implies
      #  removing the BB as well as all its nodes.
      #  In the process, annotate the nodes that will
      #  be deleted afterwards.
      nodes_to_delete = []
      deleted_bbs = True
      while deleted_bbs:
        deleted_bbs = False
        bbs_to_delete = []
        for bb in [x for x in new_path['bbs'] if not new_path['bbs'][x]['preds']]:
          nodes_to_delete += new_path['bbs'][bb]['nodes']
          for bs in new_path['bbs'][bb]['succs']:
            new_path['bbs'][bs]['preds'].remove(bb)
          del new_path['bbs'][bb]
          deleted_bbs = True

      # Step 5: Transform all phi nodes in bypass nodes.
      #  Bypass nodes are a temporary concept intended to
      #  just eliminate the input pairs and the multiple
      #  possible sources.
      #  All bypass nodes have 1 pred and N succs.
      for n in [x for x in new_path['nodes'] if new_path['nodes'][x]['op'] == 'phi']:
        new_path['nodes'][n]['op'] = 'bypass'
        for p in new_path['nodes'][n]['preds']:
          if p[0] in new_path['bbs']:
            new_preds = [p[1]]
            break
        new_path['nodes'][n]['preds'] = new_preds

      # Step 6: Remove all bypass nodes.
      #  When, in the previous comment, I said "temporary"
      #  I really meant it.
      for n in [x for x in new_path['nodes'] if new_path['nodes'][x]['op'] == 'bypass']:
        # Add all successors of the node as successors of the predecessor.
        p = new_path['nodes'][n]['preds'][0]
        new_path['nodes'][p]['succs'] += new_path['nodes'][n]['succs']
        new_path['nodes'][p]['succs'].remove(n)

        # Replace the node in the predecessors lists of all its successors
        #  with its predecessor.
        for s in new_path['nodes'][n]['succs']:
          for i in range(len(new_path['nodes'][s]['preds'])):
            if new_path['nodes'][s]['preds'][i] == n:
              new_path['nodes'][s]['preds'][i] = p

        # And delete the node once and for all.
        del new_path['nodes'][n]

      # Step 7: Delete branches.
      for n in [x for x in new_path['nodes'] if new_path['nodes'][x]['op'] == 'br']:
        p = new_path['nodes'][n]['preds'][0]
        new_path['nodes'][p]['succs'].remove(n)
        del new_path['nodes'][n]

      # Step 8: Save the branch-related CMP operations for later study.
      cmp_trees = {}
      for n in [x for x in new_path['nodes']
          if (new_path['nodes'][x]['op'] == 'cmp' and
            not new_path['nodes'][x]['cmp'] in ['TRUE', 'FALSE'] and
            not new_path['nodes'][x]['succs'])]:
        cmp_trees[n] = self.get_subgraph_for(n, new_path['nodes'])

      # Step 9: Delete all hanging nodes: Those that are not outputs
      #  but have no successors. They are dead code that has to be
      #  eliminated.
      while nodes_to_delete:
        while nodes_to_delete: # Yes. A double loop. This is how I roll.
          n = nodes_to_delete.pop()
          if n in new_path['nodes']:
            del new_path['nodes'][n]
        for n in new_path['nodes']:
          new_path['nodes'][n]['succs'] = [x for x in new_path['nodes'][n]['succs'] if x in new_path['nodes']]
        nodes_to_delete += [x for x in new_path['nodes'] 
          if (not new_path['nodes'][x]['op'] == 'output' and
              not new_path['nodes'][x]['succs'])]

      # 9.2: Remove all deleted nodes from their corresponding BBs.
      for bb in new_path['bbs']:
        new_path['bbs'][bb]['nodes'] = [x for x in new_path['bbs'][bb]['nodes'] if x in new_path['nodes']]

      # 9.3: Update inputs and outputs information.
      new_path['inputs']  = [x for x in new_path['inputs']  if x in new_path['nodes']]
      new_path['outputs'] = [x for x in new_path['outputs'] if x in new_path['nodes']]

      # Step 10: Pack everything, wrap it nicely and return it.

      # 10.1: Match cmp nodes with their BBs
      cmps_for_bbs = {}
      for n in cmp_trees.keys():
        bb_list = [x for x in self.original_source['bbs'] if n in self.original_source['bbs'][x]['nodes']]
        if bb_list:
          bb = [x for x in self.original_source['bbs'] if n in self.original_source['bbs'][x]['nodes']][0]
          cmps_for_bbs[bb] = n

      # 10.2: Retrieve the information of the decision taken in
      #  each decisor.
      decisions = {}
      for i in range(len(forks)):
        if forks_list[i] in new_path['bbs']:
          # We have to invert the selections here because at the beginning of the function
          #  lc was the decision that got deleted.
          decisions[cmps_for_bbs[forks_list[i]]] = {0: False, 1: True}[lc[i]]

      # 10.3: Insert the path in the execution paths graph only if
      #  it was not there before.
      if not decisions in [x['decisions'] for x in paths]:
        paths.append({'decisions': decisions, 'path': new_path, 'cmp_trees': cmp_trees})

    return paths

  def get_subgraph_for(self, node_id, graph):
    # Generate list of all the predecessors of the node node_id
    op_preds = []
    new_preds = [node_id]
    while new_preds:
      node = new_preds.pop()
      op_preds.append(node)

      for pred in graph[node]['preds']:
          new_preds.append(pred)

    op_preds = list(set(op_preds))

    # Copy the graph and delete every node
    #  that doesn't precede node node_id
    subgraph = copy.deepcopy(graph)

    for n in [x for x in subgraph if x not in op_preds]:
      del subgraph[n]

    # Remove all successors that are not in the graph.
    for n in subgraph:
      subgraph[n]['succs'] = [x for x in subgraph[n]['succs'] if x in subgraph]

    return subgraph

  # apply_model(path, domain)
  #
  # Apply the general PCE modeling to the path indicated for the given domain.
  #  
  def apply_model(self, path, domain, in_i, in_j, j_k=1.0):

    self.mutex.acquire()

    print 'The propagated values are, indeed, i: {}, j: {}.'.format(str(in_i), str(in_j))

    local_path = copy.deepcopy(path)
    local_domain = copy.deepcopy(domain)
    self.mutex.release()

    # Generate system graphs with noises
    # We don't want to add noises to the outputs.
    nodes_to_add_noise = [x for x in local_path['path']['nodes'].keys() if not x in local_path['path']['outputs']]

    # Generate the subsets of noises that will be introduced together.
    if not self.partitioner == None:
      noise_groups = self.partitioner.get_partitions(local_path['path'], nodes_to_add_noise, self.partition_size)
    else: 
      noise_groups = [nodes_to_add_noise]

    # Partition the current path with ME-gPC and work with the
    #  returned list.
    me_gpc_partitions = self.get_me_gpc_partitions(local_path, local_domain)

    self.mutex.acquire()
    print len(me_gpc_partitions), "ME-gPC partitions found in execution path {}.".format(str(in_i))
    self.mutex.release()

    # Solve the system for each partition.
    outputs = []
    for partition in me_gpc_partitions:
      self.mutex.acquire()
      print 'Studying ME-gPC partition', str(me_gpc_partitions.index(partition) + 1), 'out of', len(me_gpc_partitions) 
      self.mutex.release()
      clean_outputs = {x: partition['propagation'][x] for x in local_path['path']['outputs']}

      noise_propagations = []
      for group in noise_groups:
        self.mutex.acquire()
        print len(me_gpc_partitions), "Execution path {}, subdomain {} - Studying group {} of {}.".format(str(in_i), str(in_j), str(noise_groups.index(group) + 1), str(len(noise_groups)))
        self.mutex.release()

        group_graph = copy.deepcopy(local_path['path'])
        self.add_noises_to(group, group_graph)
        used_inputs = [self.input_to_rvars[i] for i in local_path['path']['inputs']]
        # Generate C matrix for each group of random variables.
        noised_c_matrix = c_matrix.c_matrix(used_inputs + [self.noise_equivs['n_' + str(v)][0] for v in group], self.order)
        # Propagate the PCE coefficients through the system.
        iter_coeffs = dict(partition['distributions'].items() + self.noise_dists.items())
        noise_propagations.append(self.propagate(group_graph['nodes'], iter_coeffs, noised_c_matrix))

        # Update the expectances with the results from this iteration.
        for x in noised_c_matrix.expectances:
          self.mutex.acquire()
          self.noised_expectances[x] = noised_c_matrix.expectances[x]
          self.mutex.release()

      noised_outputs = {}
      for output in local_path['path']['outputs']:
        output_result = {}
        for result in noise_propagations:
          noised_output = result[output]
          output_result = pce_ops.add(output_result, pce_ops.sub(noised_output, partition['propagation'][output]))
        noised_outputs[output] = pce_ops.add(output_result, partition['propagation'][output])

      outputs.append({'clean_outputs': clean_outputs, 'noised_outputs': noised_outputs, 'j_k': partition['j_k']})

    k = 1
    for solution in outputs:
      pickle_file = os.path.join(self.dump_files, 'solution_{}_{}_{}'.format(str(in_i), str(j), str(k)))
      with open(pickle_file, 'w') as sol:
        pickle.dump(solution, sol)
        self.mutex.acquire()
        self.solution_files.update({(i,j, k): pickle_file})
        self.mutex.release()
      k += 1

  # partition_conditional(graph, decisions)
  #
  # This function divides the domain of the input graph (which includes information about
  #  the conditional decision trees and more)
  #
  def partition_conditional(self, graph, decisions):
    # Step 1: Check if the solution is already in subdomains_by_decisions.
    #  If it is not, calculate all the subdomains corresponding to that
    #  decision path.
    if decisions[tuple(graph['decisions'].keys())][tuple(graph['decisions'].values())] is None:
      updated_decisions = copy.deepcopy(decisions)
      updated_decisions[tuple(graph['decisions'].keys())][tuple(graph['decisions'].values())] = []

      # Configure the initial parameters of the domain: Inputs distributions (given by
      #  the designer) and domain bounds ([-1, 1]^d). 
      distributions = {self.input_to_rvars[x]: self.input_dists[self.input_to_rvars[x]] for x in graph['path']['inputs']}
      domain_bounds = {self.input_to_rvars[x]: (-1.0, 1.0) for x in graph['path']['inputs']}

      to_solution = []
      decisions_tuple = tuple([None] * len(graph['decisions']))

      # Encapsulate all the required information from the initial partition.
      partition = { 'forks': graph['decisions'].keys(),
                    'trees': graph['cmp_trees'],
                    'distributions': distributions,
                    'domain': domain_bounds,
                    'j_k': 1.0,
                    'decisions': decisions_tuple}

      to_study = [partition]
      self.mutex.acquire()
      print "Partitioning domain for conditional path"
      self.mutex.release()
      while to_study:
        p = to_study.pop()
        p = self.evaluate_partition(p)
        if not None in p['decisions']:
          to_solution.append(p)
          self.mutex.acquire()
          print len(to_solution), "valid partitions found."
          self.mutex.release()
        else:
          to_study += self.split(p)

      # Initiate all combinations of decisions.
      all_decisions = list(product([True, False], repeat=len(graph['decisions'])))
      for decision in all_decisions:
        updated_decisions[tuple(graph['decisions'].keys())][decision] = []

      # Populate each combination with the partitions that fall within them.
      for t in to_solution:
        updated_decisions[tuple(t['forks'])][t['decisions']].append({'coeffs': t['distributions'], 'domain': t['domain'], 'j_k': t['j_k']})

      return updated_decisions
    else:
      return decisions

  # generate_A_matrix(vars)
  #
  # Matrix A is a matrix of uniform random points in [-1,1]^d.
  #  It has as many rows as elements in the base, and as many
  #  columns as random variables in the input. Actually, the
  #  structure will be a dictionary.
  #
  def generate_A_matrix(self, vars):
    random.seed()
    base_length = len(self.clean_c_matrix.base)
    tuples = [(i, j) for i in range(base_length) for j in vars]
    random_points = {r: random.uniform(-1,1) for r in tuples}

    a_matrix = []
    for i in range(base_length):
      a_matrix.append(self.clean_c_matrix.base[:])

    for key in random_points:
      for elem in range(base_length):
        a_matrix[key[0]][elem] = a_matrix[key[0]][elem].subs(key[1], random_points[key])

    return a_matrix, random_points

  # evaluate_partition(partition)
  #
  # Receive the information from a partition and decides if it needs to be
  #  partitioned again or not depending on how the values in the domain behave
  #  in the presence of the conditional instruction.
  #  It returns a modified partition dictionary indicating the direction
  #  the partition takes. When the partition is small enough, we force the
  #  result to go one way or the other, depending on how many values pointed
  #  in one direction or the other.
  #
  def evaluate_partition(self, partition):
    p = copy.deepcopy(partition)
    base_length = len(self.clean_c_matrix.base)

    fork_index = partition['decisions'].index(None)
    fork = partition['forks'][fork_index]
    tree = partition['trees'][fork]
    decisions = list(partition['decisions'])

    # Get the results of expanding the coefficients through the decision tree.
    propagation = self.propagate(tree, p['distributions'], self.clean_c_matrix)
    lhs = propagation[tree[fork]['preds'][0]]
    rhs = propagation[tree[fork]['preds'][1]]

    # Generate a number of uniform random points in the domain.
    tuples = [(i, j) for i in range(base_length) for j in p['distributions'].keys()]
    random_points = {r: random.uniform(-1,1) for r in tuples}

    # Calculate the complete polynomial.
    val_lhs = sympy.S(0.0)
    val_rhs = sympy.S(0.0)
    for k in lhs: val_lhs += k*lhs[k]
    for k in rhs: val_rhs += k*rhs[k]

    # Generate the corresponding tuples for replacement.
    replacement_tuples = [[] for x in range(base_length)]
    for point in random_points:
      replacement_tuples[point[0]].append((point[1],random_points[point]))

    # Replace the random variables with its value in each random point
    #  and evaluate the outcome of the inequation in it.
    replacement_value = 0
    for t in replacement_tuples:
      s_val_lhs = val_lhs.subs(t) 
      s_val_rhs = val_rhs.subs(t)
      replacement_value += self.evaluate(s_val_lhs, s_val_rhs, tree[fork]['cmp'])

    # Determine if the direction of the fork has been established or not.
    decisions[fork_index] = {0: False, base_length: True}.get(replacement_value, None)
    # In case we reach the limit set up by system parameters, decide the
    #  fork direction strictly. This behaviour must be changed from here
    #  if needed.
    if p['j_k'] <= self.j_lim: decisions[fork_index] = replacement_value >= (base_length / 2)
    p['decisions'] = tuple(decisions)

    return p

  # split(partition[, on_vars])
  #
  # Given a partition, it generates all the subdivisions required. If
  #  a on_vars parameter is specified, it will only divide those variables.
  #  Otherwise all variables will be partitioned by half, and the partition
  #  re-escaled accordingly (input coefficients, domain bounds, J_k value).
  #  The function returs a list of the new partition, being each of them a
  #  dictionary with the same fields as the one received as an input.
  #
  def split(self, partition, on_vars = None):
    if on_vars is None:
      vars = partition['distributions'].keys()
    else:
      vars = copy.deepcopy(on_vars)

    partitions = [copy.deepcopy(partition)]

    while vars:
      v = vars.pop()
      new_partitions = []
      while partitions:
        p = partitions.pop()
        new_partitions += self.split_on(p,v)
      partitions = new_partitions
    return partitions

  # split_on(partition, var)
  #
  # This method for splitting a random variable follows the procedure
  #  explained in:
  #     Wan, X., & Karniadakis, G. E. (2005). An adaptive multi-element 
  #     generalized polynomial chaos method for stochastic differential
  #     equations. Journal of Computational Physics, 209(2), 617-642.
  #
  def split_on(self, partition, var):
    p0 = copy.deepcopy(partition)
    p1 = copy.deepcopy(partition)

    base_length = len(self.clean_c_matrix.base)
    a_matrix, random_points = self.generate_A_matrix(partition['distributions'].keys())

    # 'fork', 'tree' and 'direction' are the same as in the parent.
    # 'j_k'
    p0['j_k'] = p0['j_k'] / 2
    p1['j_k'] = p1['j_k'] / 2

    # 'domain'
    middle_point = sum(partition['domain'][var]) / 2
    p0['domain'][var] = (partition['domain'][var][0], middle_point)
    p1['domain'][var] = (middle_point, partition['domain'][var][1])

    # 'distributions'
    coeffs = partition['distributions'][var]
    upper = Symbol('upper')
    lower = Symbol('lower')
    resize_form = ((upper - lower) / 2) * var + (upper + lower) / 2;

    equation = 0.0
    for c in coeffs: equation += c*coeffs[c]
    equation = equation.subs(var, resize_form)

    u_hat_0 = []
    u_hat_1 = []

    for i in range(base_length):
      all_subs = [(v, random_points[(i,v)]) for v in partition['distributions'].keys()]
      u_hat_0.append([equation.subs([(lower,-1),(upper,0)] + all_subs)])
      u_hat_1.append([equation.subs([(lower, 0),(upper,1)] + all_subs)])

    coeffs_0 = [x[0] for x in list(linalg.lstsq(a_matrix,u_hat_0)[0])]
    coeffs_1 = [x[0] for x in list(linalg.lstsq(a_matrix,u_hat_1)[0])]

    new_coeffs_0 = {self.clean_c_matrix.base[i]: coeffs_0[i] for i in range(base_length) if abs(coeffs_0[i]) > 1e-12}
    new_coeffs_1 = {self.clean_c_matrix.base[i]: coeffs_1[i] for i in range(base_length) if abs(coeffs_1[i]) > 1e-12}

    p0['distributions'][var] = new_coeffs_0
    p1['distributions'][var] = new_coeffs_1

    return [p0, p1]

  # evaluate(lhs, rhs, op)
  #
  # Receives an inequation as left hand side, right hand side, operation,
  #  and returns its outcome in the form of 1 for True, 0 for false.
  #
  def evaluate(self, lhs, rhs, op):
    return {True: 1, False: 0}[{'LT':    lhs <  rhs,
                                'LTE':   lhs <= rhs,
                                'EQ':    lhs == rhs,
                                'NEQ':   lhs != rhs,
                                'GT':    lhs >  rhs,
                                'GTE':   lhs >= rhs,
                                'TRUE':  True,
                                'FALSE': False}[op]]
    # Because a bit of obfuscated code doesn't hurt.

  def get_me_gpc_partitions(self, path, domain):

    to_solution = []
    # Generate initial solution
    propagation = self.propagate(path['path']['nodes'], domain['coeffs'], self.clean_c_matrix)
    partition = { 'distributions': domain['coeffs'],
                  'domain':        domain['domain'],
                  'propagation':   propagation,
                  'j_k':           domain['j_k']}

    to_study = [partition]
    self.mutex.acquire()
    print "Partitioning domain for ME-gPC"
    self.mutex.release()
    while to_study:
      p = to_study.pop()
      to_split = self.evaluate_megpc_partition(p)
      if to_split:
        new_partitions = self.split(p, to_split)
        for p in range(len(new_partitions)):
          new_partitions[p]['propagation'] = self.propagate(path['path']['nodes'], new_partitions[p]['distributions'], self.clean_c_matrix)
        to_study += new_partitions
        self.mutex.acquire()
        print len(to_study), 'partitoins now pending to be studied.'
        self.mutex.release()
      else:
        to_solution.append(p)
        self.mutex.acquire()
        print len(to_solution), 'valid ME-gPC partitions found.'
        self.mutex.release()
    return to_solution

  def evaluate_megpc_partition(self, partition):
    vars = partition['domain'].keys()

    for i in [x for x in partition['propagation'] if not x is None]:
      if self.check_condition_one(i, partition['j_k']):
        max_R_i = self.get_max_R_i(i, vars)
        vars_to_split = [v for v in vars if self.check_condition_two(i, v, max_R_i)]
        self.mutex.acquire()
        print 'Partitions will be done at the following variables:', vars_to_split
        self.mutex.release()
        return vars_to_split

    return []

  def check_condition_one(self, coeffs, j_k):
    numerator   = sum([(coeffs[k]**2) * self.clean_c_matrix.expectances[k]
                        for k in coeffs if not k == sympy.S(1.0) and sum(list(sympy.degree_list(k))) == self.order])
    denominator = sum([(coeffs[k]**2) * self.clean_c_matrix.expectances[k]
                        for k in coeffs if not k == sympy.S(1.0)])

    if denominator == 0: return False # The number is a constant! No need to partition here

    eta_k = numerator / denominator
    return (eta_k**self.alpha)*j_k >= self.theta_1

  def check_condition_two(self, coeffs, var, max_R_i):
    R_i = self.get_R_i_for(coeffs, var)
    return R_i >= (max_R_i*self.theta_2)

  def get_R_i_for(self, coeffs, var):
    # TODO: Rewrite this function in a more pythonic way.
    N_p = 0
    numerator   = 0.0
    denominator = 0.0

    for k in [x for x in self.clean_c_matrix.expectances if not x == sympy.S(1.0)]:
      degree = sum(list(sympy.degree_list(k)))
      N_p = max([degree, N_p]) # Isn't this the same as 'self.order'?

    for k in [x for x in self.clean_c_matrix.expectances if not x == sympy.S(1.0)]:
      if list(sympy.degree_list(k, gens=var))[0] == N_p:
        numerator = (coeffs.get(k, 0.0)**2) * self.clean_c_matrix.expectances[k]
      if sum(list(sympy.degree_list(k))) == N_p:
        denominator += (coeffs.get(k, 0.0)**2) * self.clean_c_matrix.expectances[k]

    numerator = [(coeffs.get(x, 0.0)**2) * self.clean_c_matrix.expectances[x] for x in self.clean_c_matrix.expectances if not x == sympy.S(1.0) and list(sympy.degree_list(x, gens=var))[0] == self.order][0]

    if denominator == 0: return 0
    return numerator / denominator

  def get_max_R_i(self, coeffs, vars):
    return max([self.get_R_i_for(coeffs, v) for v in vars])