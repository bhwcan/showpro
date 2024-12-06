class Directive:
  def __init__(self, raw, pos):
    self.line = raw
    self.y = pos
    self.x = 0
    self.name = ""
    self.text = ""

  def process(self):
    if self.line.find("#") == 0:
      self.name = self.line[0:1]
      self.text = self.line[1:]
      return self.name, self.text
    self.x = self.line.find("{")
    colon = self.line.find(":")
    end = self.line.find("}")
    if end < 0:
      end = len(self.line)
    if colon > 0:
      self.name = self.line[self.x+1:colon].strip().lower()
      self.text = self.line[colon+1:end]
    else:
      self.name = self.line[self.x+1:end].strip().lower()
    return self.name, self.text    
  
