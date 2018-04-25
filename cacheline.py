class CacheLine:
  # Members:
  # <int> tag
  # <bool> valid

  def __init__(self, tag, valid):
    self.tag = tag
    self.valid = valid
  
  def __repr__(self):
    return '(%d:%d)' % (self.valid, self.tag)

  def __str__(self):
    return '(%d:%d)' % (self.valid, self.tag)
