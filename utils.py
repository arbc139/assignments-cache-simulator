
import humanfriendly

# Command parser
def parse_commands(argv, configs):
  from optparse import OptionParser
  parser = OptionParser('"')
  for key, value in configs.items():
    parser.add_option(key, value['longInputForm'], dest=value['field'])

  options, otherjunk = parser.parse_args(argv)
  return options

def check_raw_configs(raw_configs):
  for raw_config in raw_configs:
    C = int(humanfriendly.parse_size(raw_config['C'], binary=True))
    L = int(humanfriendly.parse_size(raw_config['L'], binary=True))
    K = int(raw_config['K'])
    N = int(raw_config['N'])

    if C != L * K * N:
      raise RuntimeError('Invalid matching L, K, N, C parameters')
