
def parse(trace_file, BIT_SIZE):
  result = []
  while True:
    line = trace_file.readline()
    tokenized_line = line.replace('\n', '').split()
    if not line: break

    HEX_SIZE = int(BIT_SIZE / 4)

    tokenized_line[1] = tokenized_line[1].replace('0x', '')
    address = ''.join(['0' for _ in range(HEX_SIZE - len(tokenized_line[1]))]) + tokenized_line[1]
    result.append({
      'type': int(tokenized_line[0]),
      'address': address,
    })
  return result
