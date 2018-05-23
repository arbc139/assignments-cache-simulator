
import humanfriendly
import numpy as np
import math
import random

import constants

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
      'write_miss': 0,
    }
    self.LRU_count = np.array([
      [0 for j in range(config.K)] for i in range(config.N)
    ])
    self.LFU_count = np.array([
      [0 for j in range(config.K)] for i in range(config.N)
    ])
    self.cachelines = [
      [CacheLine(0, False) for j in range(config.K)] for i in range(config.N)
    ]
    self.low_cache = None

  def set_low_cache(self, cache):
    self.low_cache = cache

  def select_victim(self, cache_index):
    victim_j = 0
    replacement_policy = self.config.replacement_policy

    if replacement_policy == constants.REPLACEMENT_POLICY_TYPE['LRU']:
      # LRU method.
      max_LRU_count = 0
      for j in range(self.config.K):
        if self.LRU_count[cache_index][j] > max_LRU_count:
          max_LRU_count = self.LRU_count[cache_index][j]
          victim_j = j
      return victim_j
    elif replacement_policy == constants.REPLACEMENT_POLICY_TYPE['MRU']:
      # MRU method.
      min_LRU_count = math.inf
      for j in range(self.config.K):
        if self.LRU_count[cache_index][j] < min_LRU_count:
          min_LRU_count = self.LRU_count[cache_index][j]
          victim_j = j
      return victim_j
    elif replacement_policy == constants.REPLACEMENT_POLICY_TYPE['RANDOM']:
      # Random method.
      for j in range(self.config.K):
        if not self.cachelines[cache_index][j].valid:
          return j
      return random.randrange(0, self.config.K)
    elif replacement_policy == constants.REPLACEMENT_POLICY_TYPE['LFU']:
      # LFU method.
      min_LFU_count = math.inf
      for j in range(self.config.K):
        if self.LFU_count[cache_index][j] < min_LFU_count:
          min_LFU_count = self.LFU_count[cache_index][j]
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
        self.LFU_count[cache_index][j] += 1
        return True

    # Miss case!
    victim_j = self.select_victim(cache_index)
    self.cachelines[cache_index][victim_j].valid = True
    self.cachelines[cache_index][victim_j].tag = cache_tag
    self.LRU_count[cache_index][victim_j] = 0
    self.LFU_count[cache_index][victim_j] = 0

    if trace['type'] == constants.ACCESS_TYPE['INST_READ']:
      self.counts['inst_miss'] += 1
    elif trace['type'] == constants.ACCESS_TYPE['DATA_READ']:
      self.counts['data_miss'] += 1
    elif trace['type'] == constants.ACCESS_TYPE['DATA_WRITE']:
      self.counts['write_miss'] += 1

    if self.low_cache:
      return self.low_cache.access(trace)

    return False

  def get_amat(self):
    total_count = self.counts['hit'] + self.counts['inst_miss'] \
        + self.counts['data_miss'] + self.counts['write_miss']
    inst_miss_ratio = self.counts['inst_miss'] / total_count
    data_miss_ratio = self.counts['data_miss'] / total_count
    write_miss_ratio = self.counts['write_miss'] / total_count

    miss_panelty = None
    if not self.low_cache:
      miss_panelty = self.config.MISS_PENALTY
    else:
      miss_panelty = self.low_cache.get_amat()

    return self.config.HIT_TIME \
        + miss_panelty * (inst_miss_ratio + data_miss_ratio + write_miss_ratio)

  def get_result(self):
    results = {}
    results['Input'] = self.config.input_label
    results['Cache-Capacity'] = humanfriendly.format_size(self.config.C,
                                                          binary=True)
    results['L'] = humanfriendly.format_size(self.config.L, binary=True)
    results['K'] = self.config.K
    results['N'] = self.config.N
    results['Prefetch'] = self.config.prefetch_scheme
    results['Replacement'] = self.config.replacement_policy
    total_count = self.counts['hit'] + self.counts['inst_miss'] \
        + self.counts['data_miss'] + self.counts['write_miss']
    results['Hit-Ratio'] = self.counts['hit'] / total_count
    results['Inst-Miss-Ratio'] = self.counts['inst_miss'] / total_count
    results['Data-Read-Miss-Ratio'] = self.counts['data_miss'] / total_count
    results['Data-Write-Miss-Ratio'] = self.counts['write_miss'] / total_count
    results['AMAT'] = self.get_amat()
    results['Hit-Count'] = self.counts['hit']
    results['Inst-Miss-Count'] = self.counts['inst_miss']
    results['Data-Read-Miss-Count'] = self.counts['data_miss']
    results['Data-Write-Miss-Count'] = self.counts['write_miss']
    results['Access-Count'] = total_count
