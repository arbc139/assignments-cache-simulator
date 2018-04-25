
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

    self.BYTE_SELECT = int(math.log(self.L, 2))
    self.CACHE_INDEX = int(math.log(self.N, 2))
    self.CACHE_TAG = BIT_SIZE - self.BYTE_SELECT - self.CACHE_INDEX