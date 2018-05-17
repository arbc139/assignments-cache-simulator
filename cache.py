
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

  def access(self, type, address):
    # TODO(totorody): Implements access method.
    masked = self.config.masking(address)
    cache_index = masked[0]
    cache_tag = masked[1]