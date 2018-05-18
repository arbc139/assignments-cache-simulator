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
from simulator_config import CacheConfig
from utils import check_raw_configs

def run(commands):
  # Config for L1 I/D, L2 (Fixed)
  config_L1_inst = CacheConfig(
    C='32KB', L='64B', K=1, N=512,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=4,
    MISS_PENALTY=16,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LRU'],
  )
  config_L1_data = CacheConfig(
    C='32KB', L='64B', K=1, N=512,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=4,
    MISS_PENALTY=16,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LRU'],
  )
  config_L2 = CacheConfig(
    C='256KB', L='64B', K=8, N=512,
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
      'C': '2MB',
      'L': '64B',
      'K': raw_config['K'],
      'N': raw_config['N'],
      'PREFETCH': raw_config['PREFETCH'],
      'REPLACEMENT': raw_config['REPLACEMENT'],
    }
    if (raw_config['K'] * raw_config['N']) == 32768
    for raw_config in cartesian_dict_product(raw_configs_dicts_L3)
  ]
  print(raw_configs_L3)
  raise RuntimeError('break')
  check_raw_configs([
    {
      'C': '2MB',
      'L': '64B',
      'K': raw_config['K'],
      'N': raw_config['N'],
    }
    for raw_config in raw_configs_L3
  ])

  # TODO(totorody): Iterates variable configs to config_L3.
  # Config for L3 (Dynamic)
  config_L3 = CacheConfig(
    C='2MB', L='64B', K=16, N=2048,
    BIT_SIZE=constants.BIT_SIZE,
    input_label=commands.input_file_label,
    HIT_TIME=32,
    MISS_PENALTY=120,
    prefetch_scheme=constants.PREFETCH_SCHEME_TYPE['NONE'],
    replacement_policy=constants.REPLACEMENT_POLICY_TYPE['LFU'],
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

  print('Start to run caching')
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

  print('Caching result')
  print('L1 inst cache')
  print('hit: [%d], data miss: [%d], inst_miss: [%d], write: [%d]' % (
    cache_L1_inst.counts['hit'],
    cache_L1_inst.counts['data_miss'],
    cache_L1_inst.counts['inst_miss'],
    cache_L1_inst.counts['write']))
  print('L1 data cache')
  print('hit: [%d], data miss: [%d], inst_miss: [%d], write: [%d]' % (
    cache_L1_data.counts['hit'],
    cache_L1_data.counts['data_miss'],
    cache_L1_data.counts['inst_miss'],
    cache_L1_data.counts['write']))
  print('L2 cache')
  print('hit: [%d], data miss: [%d], inst_miss: [%d], write: [%d]' % (
    cache_L2.counts['hit'],
    cache_L2.counts['data_miss'],
    cache_L2.counts['inst_miss'],
    cache_L2.counts['write']))
  print('L3 cache')
  print('hit: [%d], data miss: [%d], inst_miss: [%d], write: [%d]' % (
    cache_L3.counts['hit'],
    cache_L3.counts['data_miss'],
    cache_L3.counts['inst_miss'],
    cache_L3.counts['write']))
  print('END')
