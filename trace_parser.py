
def parse(trace_file):
  result = []
  while True:
    line = trace_file.readline()
    if not line: break
    result.append(line)
  return result

