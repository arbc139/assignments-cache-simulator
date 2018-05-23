
import humanfriendly
import numpy as np
import math
import random

import constants
import trace_parser

# Prefetches instructions 512 addresses...
INST_PREFETCH_AMOUNT = 512

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
    self.prefetch_buffer = set()   # Address list
    self.low_cache = None

  def set_low_cache(self, cache):
    self.low_cache = cache

  def check_prefetch_buffer(self, address):
    int_address = trace_parser.parse_bin_address_to_int(address)
    if int_address in self.prefetch_buffer:
      print('Find in prefetch buffer!')
    return int_address in self.prefetch_buffer

  def prefetch_inst(self, address):
    self.prefetch_buffer = set()
    int_address = trace_parser.parse_bin_address_to_int(address)
    for i in range(1, INST_PREFETCH_AMOUNT + 1):
      self.prefetch_buffer.add(int_address + i)

  def prefetch(self, access_type, address):
    if self.config.prefetch_scheme == constants.PREFETCH_SCHEME_TYPE['NONE']:
      return

    if self.config.prefetch_scheme == constants.PREFETCH_SCHEME_TYPE['INST']:
      # Prefetch on instruction mode only
      if access_type != constants.ACCESS_TYPE['INST_READ']:
        return
      self.prefetch_inst(address)
    else:
      raise RuntimeError('Other prefetch scheme is not implemented...')

  def select_victim(self, cache_index):
    victim_j = 0
    replacement_policy = self.config.replacement_policy

    # Check empty cachelines...
    for j in range(self.config.K):
      if not self.cachelines[cache_index][j].valid:
        return j

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

  def evict(self, cache_index, cache_tag, victim_j):
    self.cachelines[cache_index][victim_j].valid = True
    self.cachelines[cache_index][victim_j].tag = cache_tag
    self.LRU_count[cache_index][victim_j] = 0
    self.LFU_count[cache_index][victim_j] = 0

  def hit(self, cache_index, j):
    self.counts['hit'] += 1
    self.LRU_count[cache_index][j] = 0
    self.LFU_count[cache_index][j] += 1

  def access(self, trace):
    masked = self.config.masking(trace['address'])
    cache_index = masked[0]
    cache_tag = masked[1]

    self.LRU_count = self.LRU_count + 1

    # Check prefetch buffer
    if self.check_prefetch_buffer(trace['address']):
      victim_j = self.select_victim(cache_index)
      self.evict(cache_index, cache_tag, victim_j)
      self.hit(cache_index, victim_j)
      return True

    # Hit case!
    for j in range(self.config.K):
      if self.cachelines[cache_index][j].tag == cache_tag:
        self.hit(cache_index, j)
        return True

    # Miss case!
    # Apply prefetches schemes...
    self.prefetch(trace['type'], trace['address'])

    # Apply replacement strategy...
    victim_j = self.select_victim(cache_index)
    self.evict(cache_index, cache_tag, victim_j)

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

  def get_result(self, cache_type=None):
    results = {}
    results['Input'] = self.config.input_label
    results['Type'] = cache_type  # 'Data' or 'Inst'
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
    return results
