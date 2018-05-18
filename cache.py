
import numpy as np
import time
from multiprocessing import Pool

# CACHE READ TYPE
ACCESS_TYPE = {
  'DATA_READ': 0,
  'DATA_WRITE': 1,
  'INST_READ': 2,
}

# Cache prefetch scheme types
PREFETCH_SCHEME_TYPE = {
  'NONE': 0,
  # TODO(totorody): Implements other prefetch schemes...
}

# Cache replacement scheme types
REPLACEMENT_POLICY_TYPE = {
  'LRU': 0,
  # TODO(totorody): Implements other replacement schemes...
}

# Number of processors (To improve performance)
NUM_OF_PROCESSORS = 4

class CacheLine:
  # Members:
  # <int> tag
  # <bool> valid
  def __init__(self, tag, valid):
    self.tag = tag
    self.valid = valid

  def __repr__(self):
    return '(%d:%d)' % (self.valid, self.tag)

  def __str__(self):
    return '(%d:%d)' % (self.valid, self.tag)

class Cache:
  def __init__(self, config):
    self.config = config
    self.counts = {
      'hit': 0,
      'data_miss': 0,
      'inst_miss': 0,
      'write': 0,
    }
    LRU_count = [
      [0 for j in range(config.K)] for i in range(config.N)
    ]
    self.LRU_count = np.array(LRU_count)
    self.cachelines = [
      [CacheLine(0, False) for j in range(config.K)] for i in range(config.N)
    ]
    self.low_cache = None

  def set_low_cache(self, cache):
    self.low_cache = cache

  def select_victim(self, cache_index):
    victim_j = 0

    if (self.config.replacement_policy == REPLACEMENT_POLICY_TYPE['LRU']):
      # LRU method.
      max_LRU_count = 0
      for j in range(self.config.K):
        if self.LRU_count[cache_index][j] > max_LRU_count:
          max_LRU_count = self.LRU_count[cache_index][j]
          victim_j = j
      return victim_j
    else:
      raise RuntimeError('Other replacement policy is not implemented...')

  def access(self, trace):
    masked = self.config.masking(trace['address'])
    cache_index = masked[0]
    cache_tag = masked[1]

    self.LRU_count = self.LRU_count + 1

    # Hit case!
    for j in range(self.config.K):
      if self.cachelines[cache_index][j].tag == cache_tag:
        self.counts['hit'] += 1
        self.LRU_count[cache_index][j] = 0
        return True

    # Miss case!
    victim_j = self.select_victim(cache_index)
    self.cachelines[cache_index][victim_j].tag = cache_tag
    self.LRU_count[cache_index][victim_j] = 0

    if trace['type'] == ACCESS_TYPE['INST_READ']:
      self.counts['inst_miss'] += 1
    elif trace['type'] == ACCESS_TYPE['DATA_READ']:
      self.counts['data_miss'] += 1
    elif trace['type'] == ACCESS_TYPE['DATA_WRITE']:
      self.counts['write'] += 1

    if self.low_cache:
      return self.low_cache.access(trace)

    return False
