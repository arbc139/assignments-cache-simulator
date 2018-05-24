
# 64 Bit machine
BIT_SIZE = 64

# INPUT / OUTPUT folder paths
INPUT_FOLDER_PATH = 'trace-files/'
OUTPUT_FOLDER_PATH = 'output/'

# Cache read types
ACCESS_TYPE = {
  'DATA_READ': 0,
  'DATA_WRITE': 1,
  'INST_READ': 2,
}

# Prefetches 512 addresses on STREAM_BUFFER...
STREAM_BUFFER_PREFETCH_AMOUNT = 512
# Prefetches max 512 addresses on WRITE_BUFFER...
MAX_WRITE_BUFFER_PREFETCH_AMOUNT = 512
PREFETCHER_TYPE = {
  'NONE': 0,
  'STREAM_BUFFER': 1,
  'WRITE_BUFFER': 2,
}

def get_prefetcher_type_label(prefetcher_type_value):
  for key, value in PREFETCHER_TYPE.items():
    if value == prefetcher_type_value:
      return key

# Cache replacement scheme types
REPLACEMENT_POLICY_TYPE = {
  'LRU': 0,     # Least Recently Used
  'MRU': 1,     # Most Recently Used
  'RANDOM': 2,  # Random
  'LFU': 3,     # Least Frequently Used
  # TODO(totorody): Implements other replacement schemes...
}

def get_replacement_policy_label(replacement_policy_type_value):
  for key, value in REPLACEMENT_POLICY_TYPE.items():
    if value == replacement_policy_type_value:
      return key
