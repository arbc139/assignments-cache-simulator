
# Command parser
def parse_commands(argv, configs):
  from optparse import OptionParser
  parser = OptionParser('"')
  for key, value in configs.items():
    parser.add_option(key, value['longInputForm'], dest=value['field'])

  options, otherjunk = parser.parse_args(argv)
  return options

# Check parsed options
def check_options(options, option_configs):
  for key, value in option_configs.items():
    if key not in options:
      raise RuntimeError('Please input proper options to file')