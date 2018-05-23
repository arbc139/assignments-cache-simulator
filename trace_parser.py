
def parse_hex_address_to_bin(address, BIT_SIZE):
  # Transforms "0x_7fff_381d_4ba0" to
  # "0000_0000_0000_0000_..._0000" (64bit Binary Form)
  parsed_address = bin(int(address, 16)).replace('0b', '')
  prefix = ''.join(['0' for _ in range(BIT_SIZE - len(parsed_address))])
  return prefix + parsed_address

def parse_bin_address_to_int(address):
  return int(address, 2)

def parse(trace_file, BIT_SIZE):
  result = []
  while True:
    line = trace_file.readline()
    tokenized_line = line.replace('\n', '').split()
    if not line: break

    result.append({
      'type': int(tokenized_line[0]),
      'address': parse_hex_address_to_bin(tokenized_line[1], BIT_SIZE),
    })
  return result
