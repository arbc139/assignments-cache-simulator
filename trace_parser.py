
def parse(trace_file):
  result = []
  while True:
    line = trace_file.readline()
    line = line.replace('\n', "")
    if not line: break
    result.append(line)
  return result
