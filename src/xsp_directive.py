class Directive:
  def __init__(self, raw, pos):
    self.line = raw
    self.y = pos
    self.x = 0
    self.name = ""
    self.text = ""
    self.define = False
    self.chorddef = None
    
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
      self.name = self.line[self.x+1:colon].strip()
      self.text = self.line[colon+1:end].strip()
      if self.name[:6] == "define":
        self.defines(self.name, self.text)
    else:
      self.name = self.line[self.x+1:end].strip().lower()
    return self.name.lower(), self.text    
  
  def defines(self, dname, dtext):
    #print("defines:",dname, dtext)
    valid = True
    name = ""
    sp = dname.find(" ") # old style may have chord name before the colon
    if sp > 0:
      name = dname[sp+1:]
    ntext = dtext.strip() # get rid of filler stuff
    ntext = ntext.replace("base-fret", "")
    ntext = ntext.replace("base", "")
    ntext = ntext.replace("frets", "")
    ntext = ntext.replace(":", "")
    #print(ntext)
    fieldstrs = ntext.split()
    #print("fieldstrs:", fieldstrs)
    p = 1 # offset for name found already
    if not name:
      name = fieldstrs[0].strip()
      p = 0
    #print("name:", name)
    base = 1 # default base
    try:
      base = int(fieldstrs[1-p].strip())
    except:
      pass # it could be an x
    #print("base:",base)
    if base < 0 or base > 20:
      valid = False
    frets = []
    for i in range(2-p, len(fieldstrs)):
      f = -1 # default is fret muted
      try:
        f = int(fieldstrs[i].strip())
      except:
        pass # maybe x or - for mute
      #print("fret:", f, i)
      if f < -1 or f > 4:  # then not valid for diagram
        valid = False
        break
      frets.append(f)
    #print("number of frets:", len(frets))
    if len(frets) != 4 and len(frets) != 6: # can only do 4 and 6 strings for now
      valid = False
    # do a check for valid
    if valid:
      self.define = True
      self.chorddef = {"name": name, "base": base, "frets": frets}
      #print(self.chorddef)

