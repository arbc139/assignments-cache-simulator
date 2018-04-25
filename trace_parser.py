
def parse(trace_file, BIT_SIZE):
  result = []
  while True:
    line = trace_file.readline()
    tokenized_line = line.replace('\n', '').split()
    if not line: break

    tokenized_line[1] = bin(int(tokenized_line[1], 16)).replace('0b', '')
    address = ''.join(['0' for _ in range(BIT_SIZE - len(tokenized_line[1]))]) + tokenized_line[1]
    result.append({
      'type': int(tokenized_line[0]),
      'address': address,
    })
  return result
