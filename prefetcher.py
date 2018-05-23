
import constants
import trace_parser

class Prefetcher():
  def __init__(self, prefetecher_type):
    self.type = prefetcher_type
    self.buffer = set()

  def check(self, access_type, address):
    if self.prefetcher_type == constants.PREFETCHER_TYPE['INST']:
      if access_type != constants.ACCESS_TYPE['INST_READ']:
        return False
    elif self.prefetcher_type == constants.PREFETCHER_TYPE['DATA']:
      if access_type != constants.ACCESS_TYPE['DATA_READ'] or \
          access_type != constants.ACCESS_TYPE['DATA_WRITE']:
        return False
    else:
      raise RuntimeError('Wrong Prefetcher Type...')
    int_address = trace_parser.parse_bin_address_to_int(address)
    if int_address in self.buffer:
      print('Find in prefetch inst buffer!')
    return int_address in self.buffer

  def prefetch(self, address):
    self.buffer = set()
    int_address = trace_parser.parse_bin_address_to_int(address)
    if self.prefetcher_type == constants.PREFETCHER_TYPE['INST']:
      for i in range(1, constants.INST_PREFETCH_AMOUNT + 1):
        self.prefetch_inst_buffer.add(int_address + i)
    elif self.prefetcher_type == constants.PREFETCHER_TYPE['DATA']:
      # TODO(totorody): Implements prefeteches 'DATA' prefetcher
      None
    else:
      raise RuntimeError('Wrong Prefetcher Type...')