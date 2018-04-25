
from utils import parse_commands
from simulator_hw5 import run_hw5

def main():
  # Parse command line options...
  options = parse_commands(
    sys.argv[1:],
    {
      '-S': {
        'longInputForm': '--simulator',
        'field': 'simulator',
      },
    },
  )
  if options['simulator'] == 'hw5':
    run_hw5()
  else:
    raise RuntimeError('Invalid simulator type...')

if __name__ == '__main__':
  main()