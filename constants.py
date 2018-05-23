
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
  'INST': 1,      # Instruction prefetch scheme
  'DATA': 2,      # Data prefetch scheme
  'INST-DATA': 3, # Instruction & Data prefetch scheme (both)
  # TODO(totorody): Implements other prefetch schemes...
}

# Cache replacement scheme types
REPLACEMENT_POLICY_TYPE = {
  'LRU': 0,     # Least Recently Used
  'MRU': 1,     # Most Recently Used
  'RANDOM': 2,  # Random
  'LFU': 3,     # Least Frequently Used
  # TODO(totorody): Implements other replacement schemes...
}
