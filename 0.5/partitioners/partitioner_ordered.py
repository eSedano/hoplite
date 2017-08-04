#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
class partitioner_ordered:
  def __init__(self):
    pass

  def get_partitions(self, graph, nodes, max_partition_size):
    return [nodes[i:i+max_partition_size] for i  in range(0, len(nodes), max_partition_size)]
    # Attibution of the above code of line goes to Gary Robinson: http://www.garyrobinson.net/2008/04/splitting-a-pyt.html