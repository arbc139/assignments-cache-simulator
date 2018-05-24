
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

# Cache prefetch scheme types
PREFETCH_SCHEME_TYPE = {
  'NONE': 0,
  'INST_ONLY': 1,      # Instruction prefetch scheme
  'DATA_ONLY': 2,      # Data prefetch scheme
  'INST_DATA_BOTH': 3, # Instruction & Data prefetch scheme (both)
  # TODO(totorody): Implements other prefetch schemes...
}

# Prefetches instructions 512 inst addresses...
INST_PREFETCH_AMOUNT = 512

PREFETCHER_TYPE = {
  'STREAM_BUFFER': 0,
  'DATA': 1,
}

def get_prefetch_scheme_label(prefetch_scheme_type_value):
  for key, value in PREFETCH_SCHEME_TYPE.items():
    if value == prefetch_scheme_type_value:
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
