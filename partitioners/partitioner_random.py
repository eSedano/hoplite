#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import copy
import random

class partitioner_random:
  def __init__(self):
    pass

  def get_partitions(self, graph, nodes, max_partition_size):
    pool = copy.deepcopy(nodes)
    to_return = []
    while len(pool) >= max_partition_size:
      sample = random.sample(pool, max_partition_size)
      pool = [x for x in pool if not x in sample]
      to_return.append(sample)
    if pool: to_return.append(pool)
    return to_return