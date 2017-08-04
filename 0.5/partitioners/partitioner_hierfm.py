#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import copy
import numpy
import random

class partitioner_hierfm:

  final_partitions = []
  study_partitions = []
  max_gain = 3

  strongly_non_linear = ['abs', 'sqrt']

  # Fixed elements through the partitioning.
  graph    = None
  max_size = None

  # Elements that will change in each FM run.
  nets         = {}
  node_to_nets = {}
  # Bucket list structure
  bucket_list = {}
  nodes_list  = {}

  def __init__(self):
    pass

  def get_partitions(self, graph, all_nodes, max_partition_size):
    self.graph = graph
    self.max_size = max_partition_size

    self._stage_one(all_nodes)
    self._stage_two()
    
    return self.final_partitions

  def _stage_one(self, nodes):
    self.final_partitions = [[n] for n in nodes if self.graph['nodes'][n]['op'] in self.strongly_non_linear]
    self.study_partitions = [[n for n in nodes if not self.graph['nodes'][n]['op'] in self.strongly_non_linear]]

  def _stage_two(self):
    while self.study_partitions:
      studied = self.study_partitions.pop()
      cutsize = len(studied)
      p_one = None
      p_two = None
      for x in range(256):
        tmp_p_one, tmp_p_two, tmp_cutsize = self.__fiduccia_mattheyses(studied)
        if tmp_cutsize < cutsize:
          p_one   = tmp_p_one
          p_two   = tmp_p_two
          cutsize = tmp_cutsize

      if self.__stop_criterion(p_one): self.final_partitions.append(p_one)
      else: self.study_partitions.append(p_one)
      if self.__stop_criterion(p_two): self.final_partitions.append(p_two)
      else: self.study_partitions.append(p_two)
      print self.final_partitions
      print self.study_partitions

  def __stop_criterion(self, nodes):
    return True if len(nodes) <= self.max_size else False

  def __fiduccia_mattheyses(self, nodes):
    self.__compute_nets(nodes)
    part_a, part_b = self.__get_initial_partitions(nodes)
    self.__compute_bucket_list(part_a, part_b)
    while True:
      movements = self.__evaluate_movements(part_a, part_b)
      
      if not movements:
        cutsize = self.__get_cutsize(part_a, part_b)
        return part_a, part_b, cutsize
      part_a, part_b = self.__apply_movements(movements, part_a, part_b)
      self.__compute_bucket_list(part_a, part_b)

  def __compute_nets(self, nodes):
    self.nets = {}
    self.node_to_nets = {n: [] for n in nodes}

    for n in nodes:
      self.nets[n] = list(set([n] + [x for x in self.graph['nodes'][n]['succs'] if x in nodes]))
      for node in self.nets[n]:
        self.node_to_nets[node].append(n)

  def __compute_bucket_list(self, part_a, part_b):
    nodes = part_a + part_b
    self.bucket_list = {x: [] for x in range(-self.max_gain, self.max_gain + 1)}
    self.nodes_list  = {x: None for x in nodes}
    
    for n in nodes:
      gain = self.__get_gain(n, part_a, part_b)
      self.bucket_list[gain] = list(set(self.bucket_list[gain] + [n]))
      self.nodes_list[n]     = gain

  def __get_initial_partitions(self, nodes):
    while True:
      part_a = random.sample(nodes, random.randrange(len(nodes)))
      part_b = [x for x in nodes if not x in part_a]
      if self.__is_balanced(part_a, part_b): return part_a, part_b

  def __is_balanced(self, part_a, part_b):
    if (len(part_a) > self.max_gain) and (not part_b): return False
    if (len(part_b) > self.max_gain) and (not part_a): return False
    mean_subs = numpy.mean([len(part_a), len(part_b)]) * 0.2
    return abs(len(part_a) - len(part_b)) <= max([self.max_gain, mean_subs])

  def __get_gain(self, node, part_a, part_b):
    gain = 0
    for net in self.node_to_nets[node]:
      if self.__is_node_from(part_a, part_b, node, self.nets[net]): gain += 1
      if self.__is_node_to(part_a, part_b, node, self.nets[net]):   gain -= 1
    return gain

  def __is_node_to(self, part_a, part_b, node, net):
    if node in part_a: return False if [x for x in net if x in part_b] else True
    if node in part_b: return False if [x for x in net if x in part_a] else True

  def __is_node_from(self, part_a, part_b, node, net):
    if node in part_a: return True if not [x for x in net if (not x == node) and x in part_a] else False
    if node in part_b: return True if not [x for x in net if (not x == node) and x in part_b] else False

  def __get_cutsize(self, part_a, part_b):
    cutsize = 0
    nodes = part_a + part_b
    for n in nodes:
      if n in part_a and [x for x in [y for y in self.graph['nodes'][n]['succs'] if y in nodes] if x in part_b]: cutsize += 1
      if n in part_b and [x for x in [y for y in self.graph['nodes'][n]['succs'] if y in nodes] if x in part_a]: cutsize += 1
    return cutsize

  def __evaluate_movements(self, ref_part_a, ref_part_b):
    bucket_list = copy.deepcopy(self.bucket_list)
    nodes_list  = copy.deepcopy(self.nodes_list)

    part_a = copy.deepcopy(ref_part_a)
    part_b = copy.deepcopy(ref_part_b)

    total_gain = 0
    move_nodes = []
    move_gains = []

    while True:
      to_move, bucket = self.__get_node_to_move(bucket_list, part_a, part_b)
      if to_move is None: break

      part_a, part_b = self.__move_node(to_move, bucket_list, nodes_list, part_a, part_b)
      total_gain += bucket
      move_nodes.append(to_move)
      move_gains.append(total_gain)
      bucket_list, nodes_list = self.__recompute_after_move(bucket_list, nodes_list, part_a, part_b)

    if not move_gains: return None
    max_gain = max(move_gains)
    if max_gain <= 0: return None
    return move_nodes[:move_gains.index(max_gain) + 1]

  def __get_node_to_move(self, bucket_list, part_a, part_b):
    for gain in range(-self.max_gain, self.max_gain + 1):
      for node in bucket_list[gain]:
        if node in part_a:
         new_part_a = [x for x in part_a if not x == node]
         new_part_b = part_b + [node]
        if node in part_b:
         new_part_b = [x for x in part_b if not x == node]
         new_part_a = part_a + [node]
        if self.__is_balanced(new_part_a, new_part_b): return node, gain
    return None, None

  def __move_node(self, node, bucket_list, nodes_list, part_a, part_b):
    bucket = nodes_list.pop(node)
    bucket_list[bucket].pop(bucket_list[bucket].index(node))

    if node in part_a:
      new_part_a = [x for x in part_a if not x == node]
      new_part_b = part_b + [node]
    elif node in part_b:
      new_part_b = [x for x in part_b if not x == node]
      new_part_a = part_a + [node]

    return new_part_a, new_part_b

  # TODO: Optimise this.
  def __recompute_after_move(self, bucket_list, nodes_list, part_a, part_b):
    nodes = [x for x in part_a + part_b if x in nodes_list]
    new_bucket_list = {x: [] for x in range(-self.max_gain, self.max_gain + 1)}
    new_nodes_list  = {x: None for x in nodes}
    
    for n in nodes:
      gain = self.__get_gain(n, part_a, part_b)
      new_bucket_list[gain] = list(set(new_bucket_list[gain] + [n]))
      new_nodes_list[n]     = gain

    return new_bucket_list, new_nodes_list

  def __apply_movements(self, movements, part_a, part_b):
    for m in movements:
      if m in part_a:
        new_part_a = [x for x in part_a if not x == m]
        new_part_b = part_b + [m]
      elif m in part_b:
        new_part_b = [x for x in part_b if not x == m]
        new_part_a = part_a + [m]

    return new_part_a, new_part_b