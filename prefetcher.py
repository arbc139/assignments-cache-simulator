
import constants
import trace_parser

class Prefetcher():
  def __init__(self, prefetcher_type):
    self.prefetcher_type = prefetcher_type
    self.buffer = set()

  def check(self, access_type, address):
    if self.prefetcher_type == constants.PREFETCHER_TYPE['STREAM_BUFFER']:
      if access_type != constants.ACCESS_TYPE['INST_READ']:
        return False
    elif self.prefetcher_type == constants.PREFETCHER_TYPE['WRITE_BUFFER']:
      if access_type != constants.ACCESS_TYPE['DATA_READ'] or \
          access_type != constants.ACCESS_TYPE['DATA_WRITE']:
        return False
    else:
      raise RuntimeError('Wrong Prefetcher Type...')
    int_address = trace_parser.parse_bin_address_to_int(address)
    if int_address in self.buffer:
      print('Find in prefetch buffer!')
    return int_address in self.buffer

  def prefetch(self, access_type, address):
    int_address = trace_parser.parse_bin_address_to_int(address)
    if self.prefetcher_type == constants.PREFETCHER_TYPE['STREAM_BUFFER']:
      self.buffer = set(range(
        int_address,
        int_address + constants.STREAM_BUFFER_PREFETCH_AMOUNT,
      ))
    elif self.prefetcher_type == constants.PREFETCHER_TYPE['WRITE_BUFFER']:
      if access_type == constants.ACCESS_TYPE['DATA_READ']:
        return
      if access_type == constants.ACCESS_TYPE['DATA_WRITE']:
        # Prefetches on write only...
        # Removes old one...
        if len(self.buffer) >= constants.MAX_WRITE_BUFFER_PREFETCH_AMOUNT:
          self.buffer.pop()
        self.buffer.add(int_address)
    else:
      raise RuntimeError('Wrong Prefetcher Type...')
