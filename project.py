# Project: Advanced Cache simulation
# Design a new level-3 cache management mechanism to exploit the effectiveness
# of the overall caching structure between the cache and main memory by using
# DRAMs: one prefecth scheme + at least one new managing/configuration method
#
# We need to enhance the effective space of level-3
#
# (1) Targets
# (a) 3 level cache simulator design
#   * Expand previous L1 cache simulation result
#   * Fix
#     L1 instruction: 32KB,
#     L1 data: 32KB,
#     L2 unified: 256KB,
#     L3 unified: 2MB
#   * L1 I/D: direct mapped cache
#   * L2 U: 8-way set associative cache
#   * L3 U: 2MB unified cache
#   * Use Write buffer scheme, simple LRU for default replacement policy and,
#     64 byte cache block size for L1 & L2, but design your own method for L3
#     (Details are shown in (b))
#
# (b) A new Level-3 structure and management
#   * can design any type of L-3 structure with buffers as a new model
#   * structure and operational mechanism (to support fast accessing latency)
#     - You need to suggest your own prefetch scheme and replacement policy in
#       L3
#     - You can employ any type of L3 configuration with buffering structures
#       depending on data pattern
#   * specify design parameters and obtain optimum value
#   * analysis on this situation by given benchmarks
#   * chose best design parameter among your applied mechanisms
#   * If you need, use simulation parameters for performance evaluation in
#     Table 1.
#
#           Table 1. Access latency
#       -----------------------------------
#                           Access latency
#       -----------------------------------
#         L1 I/D            4 cycles
#         L2                16 cycles
#         L3                32 cycles
#         Main Memory       120 cycles
#       -----------------------------------
# (c) Performance analysis result
#   * for (b), provide simulation results on given benchmarks
#   * show impact on each design parameter you applied

import json

import constants
import trace_parser
from cache import Cache
from csv_manager import CsvManager
from simulator_config import CacheConfig
from utils import check_raw_config, validate_raw_configs, cartesian_dict_product

L1_CACHE_SIZE = '32KB'
L2_CACHE_SIZE = '256KB'
L3_CACHE_SIZE = '2MB'
BLOCK_SIZE = '64B'

def populate_output_file_label(config):
  return '%s_(C_%s)_(L_%s)_(K_%s)_(N_%s)_(pre_%s)_(rep_%s)_results.csv' % (
    config.input_label,
    config.C,
    config.L,
    config.K,
    config.N,
    config.prefetch_scheme,
    config.replacement_policy,
  )

def run(commands):
  # Config for L1 I/D, L2 (Fixed)
  config_L1_inst = CacheConfig(
    C=L1_CACHE_SIZE, L=BLOCK_SIZE, K=1, N=512,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=4,
    MISS_PENALTY=16,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LRU'],
  )
  config_L1_data = CacheConfig(
    C=L1_CACHE_SIZE, L=BLOCK_SIZE, K=1, N=512,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=4,
    MISS_PENALTY=16,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LRU'],
  )
  config_L2 = CacheConfig(
    C=L2_CACHE_SIZE, L=BLOCK_SIZE, K=8, N=512,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=16,
    MISS_PENALTY=32,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LRU'],
  )

  raw_configs_dicts_L3 = {}
  with open('configs/project.json', 'r') as raw_config_file:
    raw_configs_dicts_L3 = json.load(raw_config_file)
  raw_configs_L3 = [
    {
      'C': L3_CACHE_SIZE,
      'L': BLOCK_SIZE,
      'K': raw_config['K'],
      'N': raw_config['N'],
      'PREFETCH': raw_config['PREFETCH'],
      'REPLACEMENT': raw_config['REPLACEMENT'],
    }
    for raw_config in cartesian_dict_product(raw_configs_dicts_L3)
    if check_raw_config({
      'C': L3_CACHE_SIZE,
      'L': BLOCK_SIZE,
      'K': raw_config['K'],
      'N': raw_config['N'],
    })
  ]
  validate_raw_configs(raw_configs_L3)

  # TODO(totorody): Iterates variable configs to config_L3.
  # Config for L3 (Dynamic)
  raw_config_L3 = raw_configs_L3[0]
  config_L3 = CacheConfig(
    C=raw_config_L3['C'],
    L=raw_config_L3['L'],
    K=raw_config_L3['K'],
    N=raw_config_L3['N'],
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=32,
    MISS_PENALTY=120,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE[raw_config_L3['PREFETCH']],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE[raw_config_L3['REPLACEMENT']],
  )

  input_file = constants.INPUT_FOLDER_PATH + commands.input_file_label
  # Parse trace file to programmable.
  traces = []
  with open(input_file, 'r') as trace_file:
    traces = trace_parser.parse(trace_file, constants.BIT_SIZE)

  # TODO(totorody): Implements to run caches
  cache_L1_inst = Cache(config_L1_inst)
  cache_L1_data = Cache(config_L1_data)
  cache_L2 = Cache(config_L2)
  cache_L3 = Cache(config_L3)

  cache_L1_inst.set_low_cache(cache_L2)
  cache_L1_data.set_low_cache(cache_L2)
  cache_L2.set_low_cache(cache_L3)

  print('Start to run caching...')
  index = 0
  for trace in traces:
    if index % 10000 == 0:
      print('trace #:', index)
    index += 1
    if trace['type'] not in constants.ACCESS_TYPE.values():
      continue
    if trace['type'] == constants.ACCESS_TYPE['INST_READ']:
      cache_L1_inst.access(trace)
    else:
      cache_L1_data.access(trace)

  print('Prints cache simulation results...')
  inst_result = cache_L1_inst.get_result('Inst')
  data_result = cache_L1_data.get_result('Data')

  output_file = constants.OUTPUT_FOLDER_PATH \
      + populate_output_file_label(config_L1_inst)
  with open(output_file, 'w+') as csv_file:
    csv_manager = CsvManager(csv_file, inst_result.keys())
    csv_manager.write_row(inst_result)
    csv_manager.write_row(data_result)
