
import sys

import hw5
import project
from utils import parse_commands

def main():
  command_configs = {
    '-t': {
      'longInputForm': '--target',
      'field': 'target',
    },
    '-i': {
      'longInputForm': '--input-file-label',
      'field': 'input_file_label',
    },
  }
  commands = parse_commands(sys.argv[1:], command_configs)
  if commands.target == 'hw5':
    hw5.run_all(commands)
  elif commands.target == 'project':
    project.run(commands)
  else:
    target_list = ['hw5', 'project']
    raise RuntimeError(
      'Please select "target" among these list: ' + target_list)

if __name__ == '__main__':
  main()
