
import humanfriendly
import math

class SimulatorConfig:
  def __init__(self, C, L, K, N, BIT_SIZE, input_label):
    self.C = int(humanfriendly.parse_size(C, binary=True))
    self.L = int(humanfriendly.parse_size(L, binary=True))
    self.K = int(K)
    self.N = int(N)

    if self.C != self.L * self.K * self.N:
      raise RuntimeError('Invalid matching L, K, N, C parameters')

    self.input_label = input_label

    self.BIT_SIZE = BIT_SIZE
    self.BYTE_SELECT = int(math.log(self.L, 2))
    self.CACHE_INDEX = int(math.log(self.N, 2))
    self.CACHE_TAG = self.BIT_SIZE - self.BYTE_SELECT - self.CACHE_INDEX

  def masking(self, address):
    # Extracts Cache Index from Address...
    cache_index = None
    if (self.CACHE_INDEX == 0):
      cache_index = 0
    else:
      start = self.BIT_SIZE - self.CACHE_INDEX - self.BYTE_SELECT
      end = self.BIT_SIZE - self.BYTE_SELECT
      cache_index = int(address[start:end], 2)
    # Extracts Cache Tag from Address...
    end = self.BIT_SIZE - self.CACHE_INDEX - self.BYTE_SELECT
    cache_tag = int(address[:end], 2)

    if cache_index >= self.N or cache_index < 0:
      raise RuntimeError(
        'Index error, cache index overflows out of range: cache_index[%d] index[%d]' % (
          cache_index, self.N))

    return (cache_index, cache_tag)

class CacheConfig(SimulatorConfig):
  def __init__(self, C, L, K, N, BIT_SIZE, input_label, HIT_TIME, MISS_PENALTY,
               prefetch_scheme, replacement_policy):
    SimulatorConfig.__init__(self, C, L, K, N, BIT_SIZE, input_label)
    self.HIT_TIME = HIT_TIME
    self.MISS_PENALTY = MISS_PENALTY
    self.prefetch_scheme = prefetch_scheme
    self.replacement_policy = replacement_policy
