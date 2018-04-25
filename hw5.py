# HW5: Cache simulation

# (1) single cache simulation
# 1) Cache configuration (LKN) to simulate: 64KB, 256KB, 512 KB
#   -N=1 case (fully associative mapping): LK=64KB, 256KB, 512KB
#     (C=64KB)
#       L=64B, K=1K
#       L=128B, K=512
#     (C=256KB)
#       L=64B, K=4K
#       L=128B, K=2K
#     (C=512KB)
#       L=64B, K=8K
#       L=128B, K=4K
#
#   -K=1 case (direct mapping): LN= 64KB, 256KB, 512KB (variable: L= 64bytes)
#     (C=64KB)
#       L=64B, N=1K
#     (C=256KB)
#       L=64B, N=4K
#     (C=512KB)
#       L=64B, N=8K
#
#   -K=2, 4 case (set associative mapping, L= 64, 128bytes)
#     (C=64KB)
#       L=64B, K=2, N=512
#       L=64B, K=4, N=256
#       L=128B, K=2, N=256
#       L=128B, K=4, N=128
#     (C=256KB)
#       L=64B, K=2, N=2K
#       L=64B, K=4, N=1K
#       L=128B, K=2, N=1K
#       L=128B, K=4, N=512
#     (C=512KB)
#       L=64B, K=2, N=4K
#       L=64B, K=4, N=2K
#       L=128B, K=2, N=2K
#       L=128B, K=4, N=1K

# 2) Use these attached traces as input for cache simulation
# 3) Collect cache misses and draw graphs and decide your best configuration of various L, K, N, on 256KB and 512 KB, in terms of miss ratio and AMAT.
# 4) Submit report and source list
# 5) Due: Apr. 26.
# Two address input trace files are attached as files. These files can be used as the input of your simulator. Address format is also attached.
# * This simulator will be used later to simulate more complex structures as your next HW.
import humanfriendly
import math
import random
import sys
from utils import parse_commands
from cacheline import CacheLine
import trace_parser

options = {}
# Assumes to set '1'
HIT_TIME = 1
# Assumes to set '20'
MISS_PENALTY = 20
BYTE_SELECT = -1 # Not initialized.
CACHE_INDEX = -1 # Not initialized.
CACHE_TAG = -1 # Not initialized.

# Cache Access Types
ACCESS_TYPE = {
  'dataRead': 0,
  'dataWrite': 1,
  'instRead': 2,
}

def populate_programmable_options(options):
  options.C = humanfriendly.parse_size(options.C, binary=True)
  options.L = humanfriendly.parse_size(options.L, binary=True)
  options.C = int(options.C)
  options.L = int(options.L)
  options.K = int(options.K)
  options.N = int(options.N)
  if options.C != options.L * options.K * options.N:
    raise RuntimeError('Invalid matching L, K, N, C parameters')
  return options

def setup_global_parameters(options):
  global BYTE_SELECT
  global CACHE_INDEX
  global CACHE_TAG
  BYTE_SELECT = int(math.log(options.L, 2))
  CACHE_INDEX = int(math.log(options.N, 2))
  CACHE_TAG = 64 - BYTE_SELECT - CACHE_INDEX

def run_hw5():
  option_configs = {
    '-L': {
      'longInputForm': '--block-size',
      'field': 'L',
    },
    '-K': {
      'longInputForm': '--associative',
      'field': 'K',
    },
    '-N': {
      'longInputForm': '--cache-size',
      'field': 'N',
    },
    '-C': {
      'longInputForm': '--cache-capacity',
      'field': 'C',
    },
    '-i': {
      'longInputForm': '--input-file',
      'field': 'inputFile',
    },
    '-o': {
      'longInputForm': '--output-file',
      'field': 'outputFile',
    },
  }
  ## Step 1. Prepare to simulation
  # Parse command line options...
  options = parse_commands(sys.argv[1:], option_configs)
  # Transforms parameter options programmable.
  options = populate_programmable_options(options)
  # Initialize global parameters... (After this line, should be used as constant)
  setup_global_parameters(options)
  # Initialize cache block with [N][K] dimension.
  cache = [
    [CacheLine(0, False) for j in range(options.K)] for i in range(options.N)
  ]
  # Parse trace file to programmable.
  parsed_traces = []
  with open(options.inputFile, 'r') as trace_file:
    parsed_traces = trace_parser.parse(trace_file)
  print(parsed_traces[:10])

  ## Step 2. Run simulator
  simulation_result = simulate_hw5(parsed_traces, cache)

  ## Step 3. Print out result file as CSV
  """
  csv_writer = CsvWriter(output_file, [options...])
  for key, value in simulation_result.items():
    csv_writer.write_row({
      options...
      key: value
    })
  """

def simulate_hw5(parsed_traces, cache):
  result = {
    'hit': 0,
    'miss': 0,
    'access_count': 0,
  }
  for trace in parsed_traces:
    if trace['type'] not in ACCESS_TYPE.values():
      continue

    result['access_count'] += 1

    address = trace['address']
    cache_index = ((address << CACHE_TAG) >> (CACHE_TAG + BYTE_SELECT))
    cache_tag = (address >> (CACHE_INDEX + BYTE_SELECT))

    print('LOOP START>> cache_index:', cache_index, ', cache_tag:', cache_tag)

    # Cache Hit
    if any(
      cacheline.valid and cacheline.tag == cache_tag
      for cacheline in cache[cache_index]):
        print('hit!!!')
        print('address:', address)
        print('index:', cache_index)
        print('tag:', cache_tag)
        result['hit'] += 1
        return result # Temporary statement
        # continue

    # Cache Miss
    result['miss'] += 1

    empty_k_index = -1
    for index, cacheline in enumerate(cache[cache_index]):
      if not cacheline.valid:
        empty_k_index = index

    if empty_k_index != -1:
      cache[cache_index][empty_k_index].valid = True
      cache[cache_index][empty_k_index].tag = cache_tag
      print('Found empty k index')
      print('address:', address)
      print('index:', cache_index)
      print(empty_k_index)
      print('tag:', cache_tag)
      return result
      # continue

    # Evicts random victim
    victim_k_index = random.randrange(0, options.K - 1)
    cache[cache_index][victim_k_index].valid = True
    cache[cache_index][victim_k_index].tag = cache_tag
