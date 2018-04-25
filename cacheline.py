class CacheLine:
  # Members:
  # <int> tag
  # <bool> valid

  def __init__(self, tag, valid):
    self.tag = tag
    self.valid = valid