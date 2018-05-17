
# CACHE READ TYPE
ACCESS_TYPE = {
  'data_read': 0,
  'data_write': 1,
  'inst_read': 2,
}

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
    self.LRU_count = [
      [0 for j in range(config.K)] for i in range(config.N)
    ]
    self.cachelines = [
      [CacheLine(0, False) for j in range(config.K)] for i in range(config.N)
    ]

  def set_low_cache(self, cache):
    self.low_cache = cache

  def access(self, trace):
    masked = self.config.masking(trace['address'])
    cache_index = masked[0]
    cache_tag = masked[1]

    max_LRU_count = 0
    max_LRU_j = 0
    for i in range(self.config.N):
      for j in range(self.config.K):
        self.LRU_count[i][j] += 1
        if i == cache_index and self.LRU_count[i][j] > max_LRU_count:
          max_LRU_count = self.LRU_count[i][j]
          max_LRU_j = j

    for j in range(self.config.K):
      if self.cachelines[cache_index][j].tag == cache_tag:
        self.counts['hit'] += 1
        self.LRU_count[cache_index][j] = 0
        return True

    if trace['type'] == ACCESS_TYPE['inst_read']:
      self.counts['inst_miss'] += 1

    if trace['type'] == ACCESS_TYPE['data_read']:
      self.counts['data_miss'] += 1

    self.cachelines[cache_index][max_LRU_j] = cache_tag
    self.LRU_count[cache_index][max_LRU_j] = 0

    if trace['type'] == ACCESS_TYPE['data_write']:
      self.counts['write'] += 1

    if self.low_cache:
      return self.low_cache.access(trace)

    return False
