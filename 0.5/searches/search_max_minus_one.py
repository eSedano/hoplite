#  @author  Enrique Sedano
#  @version  0.14.07
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
import numpy

class search_max_minus_one:

  def __init__(self, source_config, model, log=None):
    self.limits = source_config['noise_lims']
    self.model  = model
    self.log    = log

  def run(self):
    initial_wlv = self.model.num_noises * [32]
    uniform_wlv = self._search_uniform_wlv(initial_wlv)
    variable_wlv = self._search_variable_wlv(uniform_wlv)

  def _search_uniform_wlv(self, initial_wlv):
    self._log('Searching uniform WLV', 'info')
    clean_variance = self.model.get_signal_variance()
    wlv = initial_wlv

    while not [x for x in range(len(clean_variance)) if self.model.get_noise_variance(wlv)[x] - clean_variance[x] > self.limits[x]]:
      wlv = [w - 1 for w in wlv]
    
    return [w + 1 for w in wlv]

  def _search_variable_wlv(self, initial_wlv):
    self._log('Searching variable WLV', 'info')
    clean_variance = self.model.get_signal_variance()

    wlv = initial_wlv

    n_iters = 0

    while True:
      ref_variances = self.model.get_noise_variance(wlv)

      candidate_wlvs = [[wlv[y] - 1 if y == x else wlv[y] for y in range(len(wlv))] for x in range(len(wlv))]

      candidate_variances = [self.model.get_noise_variance(x) for x in candidate_wlvs]

      valid_candidates = [c for c in candidate_variances if [x for x in range(len(clean_variance)) if c[x] - clean_variance[x] <= self.limits[x]]]
      if not valid_candidates:
        self._log('Found solution after ' + str(n_iters) + ' iterations', 'info')
        return wlv

      delta_noises = [[c[x] - ref_variances[x] for x in range(len(c))] for c in valid_candidates]
      avg_delta_noises = [numpy.mean(x) for x in delta_noises]
      min_avg_delta = min(avg_delta_noises)
      delta_index = avg_delta_noises.index(min_avg_delta)
      wlv = candidate_wlvs[candidate_variances.index(valid_candidates[delta_index])]
      print wlv
      n_iters += 1

  def _log(self, message, priority):
    if self.log is None:
      print priority.upper(), '-', message
    else:
      if   priority == 'info':  self.log.info(message)
      elif priority == 'debug': self.log.debug(message)
      elif priority == 'error': self.log.error(message)
