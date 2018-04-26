
def parse(trace_file, BIT_SIZE):
  result = []
  while True:
    line = trace_file.readline()
    tokenized_line = line.replace('\n', '').split()
    if not line: break

    # Transforms "0x_7fff_381d_4ba0" to
    # "0000_0000_0000_0000_..._0000" (64bit Binary Form)
    tokenized_line[1] = bin(int(tokenized_line[1], 16)).replace('0b', '')
    prefix = ''.join(['0' for _ in range(BIT_SIZE - len(tokenized_line[1]))])
    address = prefix + tokenized_line[1]
    result.append({
      'type': int(tokenized_line[0]),
      'address': address,
    })
  return result
