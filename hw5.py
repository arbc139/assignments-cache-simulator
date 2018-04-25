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
import json
import math
import random
import sys
from simulator_config import SimulatorConfig
from cacheline import CacheLine
import trace_parser
from csv_manager import CsvManager

# 64 bit machine
BIT_SIZE = 64
# Assumes to set '1'
HIT_TIME = 1
# Assumes to set '20'
MISS_PENALTY = 20

INPUT_FOLDER_PATH = 'trace-files/'
OUTPUT_FOLDER_PATH = 'output/' 

# Cache Access Types
ACCESS_TYPE = {
  'dataRead': 0,
  'dataWrite': 1,
  'instRead': 2,
}

def populate_output_file_label(input_label):
  return '%s_results.csv' % input_label

def check_raw_configs(raw_configs):
  for raw_config in raw_configs:
    C = int(humanfriendly.parse_size(raw_config['C'], binary=True))
    L = int(humanfriendly.parse_size(raw_config['L'], binary=True))
    K = int(raw_config['K'])
    N = int(raw_config['N'])

    if C != L * K * N:
      raise RuntimeError('Invalid matching L, K, N, C parameters')

def run_all():
  input_labels = ['Trace1']

  # TODO(totoro): Needs to parse configs JSON file.
  """
  raw_configs = [
    {
      'C': '64KB',
      'L': '64B',
      'K': '2',
      'N': '512',
    },
    {
      'C': '64KB',
      'L': '64B',
      'K': '1024',
      'N': '1',
    },
  ]
  """
  raw_configs = json.load('configs.json')
  check_raw_configs(raw_configs)

  for input_label in input_labels:
    print('INPUT:', input_label)
    input_file = INPUT_FOLDER_PATH + input_label

    # Parse trace file to programmable.
    traces = []
    with open(input_file, 'r') as trace_file:
      traces = trace_parser.parse(trace_file, BIT_SIZE)

    # Open CSV file to write...
    output_file = OUTPUT_FOLDER_PATH + populate_output_file_label(input_label)
    with open(output_file, 'w+') as csv_file:
      for raw_config in raw_configs:
        # Get Simulator Configurations...
        config = SimulatorConfig(
          C=raw_config['C'],
          L=raw_config['L'],
          K=raw_config['K'],
          N=raw_config['N'],
          BIT_SIZE=BIT_SIZE,
          input_label=input_label,
        )
        simulation_results = run(traces, config)

        # Print out result file as CSV
        csv_manager = CsvManager(csv_file, [
          'Input', 'Cache-Capacity', 'L', 'K', 'N', 'Hit-Ratio',
          'Miss-Ratio', 'AMAT', 'Hit-Count', 'Miss-Count', 'Access-Count',
        ])
        csv_manager.write_row(simulation_results)

def run(traces, config):
  print('BYTE_SELECT:', config.BYTE_SELECT)
  print('CACHE_INDEX:', config.CACHE_INDEX)
  print('CACHE_TAG:', config.CACHE_TAG)
  # Initialize cache block with [N][K] dimension.
  cache = [
    [CacheLine(0, False) for j in range(config.K)] for i in range(config.N)
  ]

  # Run simulator
  simulation_results = simulate(traces, cache, config=config)
  print('Simulation Result: ', simulation_results)

  return format_simulation_results(
    simulation_results,
    input_label=config.input_label,
    C=config.C,
    L=config.L,
    K=config.K,
    N=config.N,
  )

def simulate(traces, cache, config):
  result = {
    'hit': 0,
    'miss': 0,
    'access_count': 0,
  }
  for trace in traces:
    if trace['type'] not in ACCESS_TYPE.values():
      continue

    result['access_count'] += 1

    address = trace['address']
    cache_index = None
    # Extracts Cache Index from Address...
    if config.CACHE_INDEX == 0:
      cache_index = 0
    else:
      start = BIT_SIZE - config.CACHE_INDEX - config.BYTE_SELECT
      end = BIT_SIZE - config.BYTE_SELECT
      cache_index = int(address[start:end], 2)
    # Extracts Cache Tag from Address...
    end = BIT_SIZE - config.CACHE_INDEX - config.BYTE_SELECT
    cache_tag = int(address[:end])

    # Cache Hit
    if any(
      cacheline.valid and cacheline.tag == cache_tag
      for cacheline in cache[cache_index]):
        result['hit'] += 1
        continue

    # Cache Miss
    result['miss'] += 1

    empty_k_index = -1
    for index, cacheline in enumerate(cache[cache_index]):
      if not cacheline.valid:
        empty_k_index = index

    if empty_k_index != -1:
      cache[cache_index][empty_k_index].valid = True
      cache[cache_index][empty_k_index].tag = cache_tag
      continue

    # Evicts random victim
    victim_k_index = random.randrange(0, config.K - 1)
    cache[cache_index][victim_k_index].valid = True
    cache[cache_index][victim_k_index].tag = cache_tag

  return result

def format_simulation_results(simulation_results, input_label, C, L, K, N):
  results = {}
  results['Input'] = input_label
  results['Cache-Capacity'] = humanfriendly.format_size(C, binary=True)
  results['L'] = humanfriendly.format_size(L, binary=True)
  results['K'] = K
  results['N'] = N
  results['Hit-Ratio'] = simulation_results['hit'] / simulation_results['access_count']
  results['Miss-Ratio'] = simulation_results['miss'] / simulation_results['access_count']
  results['AMAT'] =  HIT_TIME + (results['Miss-Ratio'] * MISS_PENALTY)
  results['Hit-Count'] = simulation_results['hit']
  results['Miss-Count'] = simulation_results['miss']
  results['Access-Count'] = simulation_results['access_count']
  return results
