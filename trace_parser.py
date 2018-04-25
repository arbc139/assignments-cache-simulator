
def parse(trace_file):
  result = []
  while True:
    line = trace_file.readline()
    tokenized_line = line.replace('\n', '').split()
    if not line: break

    result.append({
      'type': int(tokenized_line[0]),
      'address': int(tokenized_line[1], 16),
    })
  return result
