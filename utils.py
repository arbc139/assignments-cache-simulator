
import humanfriendly
import itertools

# Command parser
def parse_commands(argv, configs):
  from optparse import OptionParser
  parser = OptionParser('"')
  for key, value in configs.items():
    parser.add_option(key, value['longInputForm'], dest=value['field'])

  options, otherjunk = parser.parse_args(argv)
  return options

def check_raw_config(raw_config):
  C = int(humanfriendly.parse_size(raw_config['C'], binary=True))
  L = int(humanfriendly.parse_size(raw_config['L'], binary=True))
  K = int(raw_config['K'])
  N = int(raw_config['N'])

  return C == L * K * N


def validate_raw_configs(raw_configs):
  for raw_config in raw_configs:
    if not check_raw_config(raw_config):
      raise RuntimeError('Invalid matching L, K, N, C parameters')

def cartesian_dict_product(dicts):
  return [dict(zip(dicts, x)) for x in itertools.product(*dicts.values())]
