import wx
from xsp_directive import Directive

class Song:
  def __init__(self, parent, textsize, chordcolor, raw):
    self.mx = parent
    self.data = raw
    self.lines = []
    self.lyrics = []
    self.directives = []
    self.title = ""
    self.subtitle = ""
    self.width = 0
    self.textsize = textsize
    self.chordcolor = chordcolor
    self.chords = []
    self.instrument = "undefined"
    self.tab = "    "
    self.guitardefs = []
    self.ukuleledefs = []
    self.scalelookup = [ \
                         { "chord": "A#", "index": 2 }, 
                         { "chord": "Bb", "index": 2 }, 
                         { "chord": "C#", "index": 5 },
                         { "chord": "Db", "index": 5 },
                         { "chord": "D#", "index": 7 }, 
                         { "chord": "Eb", "index": 7 }, 
                         { "chord": "F#", "index": 10 }, 
                         { "chord": "Gb", "index": 10 }, 
                         { "chord": "G#", "index": 12 }, 
                         { "chord": "Ab", "index": 12 }, 
                         { "chord": "A", "index": 1 }, 
                         { "chord": "B", "index": 3 }, 
                         { "chord": "C", "index": 4 }, 
                         { "chord": "D", "index": 6 }, 
                         { "chord": "E", "index": 8 }, 
                         { "chord": "F", "index": 9 }, 
                         { "chord": "G", "index": 11 } ]
    self.scale = [ "NC", "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "F#", "G", "G#" ]  

  def transposeChord(self, inchord, value):
    newchords = []
    split = ""
    if inchord.find("add") > 0: # if it is 0 invalid
      split = "add"
      oldchords = inchord.split("add")
    elif inchord.find("/") > 0:
      split = "/"
      oldchords = inchord.split("/")
    else:
      oldchords = []
      oldchords.append(inchord)
    for oldchord in oldchords:
      newchord = ""
      for look in self.scalelookup:
        if oldchord.find(look["chord"]) == 0:
          oldlen = len(look["chord"])
          oldidx = look["index"]
          newidx = oldidx + value
          if newidx < 1:
            newidx = 12
          if newidx > 12:
            newidx = 1
          newchord = self.scale[newidx] + oldchord[oldlen:]
          newchords.append(newchord)
          break
    outchord = split.join(newchords)
    #print("transpose:", inchord, outchord)
    return outchord
  
  def transform(self, value):
    self.chords = []
    newlyrics = []
    for lyric in self.lyrics:
      newlyric = ""
      s = 0
      while True:
        cs = lyric.find('[',s)
        if cs < 0:
          newlyric += lyric[s:]
          break
        else:
          ce = lyric.find(']',s)
          if ce < 0:
            newlyric += lyric[s:]
            break
          newlyric += lyric[s:cs+1] # include brace
          oldchord = lyric[cs+1:ce]
          newchord = self.transposeChord(oldchord, value)
          if newchord:
            newlyric += newchord
            self.setchord(newchord)
          else:
            newlyric += oldchord
            #self.setchord(newchord) it the transpose didn't work not valid chord
          newlyric += "]" # add back the brace
          s = ce + 1
          if s >= len(lyric):
            break
      newlyrics.append(newlyric)
    self.lyrics = newlyrics
    self.display()

  def save(self): # rebuild the original with new lyrics
    output = ""
    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      output += self.directives[cd].line
      cd += 1
    l = 0
    for lyric in self.lyrics:
      while cd < len(self.directives) and self.directives[cd].y == l:
        output += self.directives[cd].line
        cd += 1
      output += lyric
      l += 1
    while cd < len(self.directives):
      output += self.directives[cd].line
      cd += 1
    return(output)
    
  def command(self, line, lineno):
    dtive = Directive(line, lineno)
    name, text = dtive.process()
    if name == "t" or name == "title":
      self.title = text
    if name == "st" or name == "subtitle":
      self.subtitle = text
    if name == "instrument":
      self.instrument = text.strip()
    if dtive.define:
      if len(dtive.chorddef["frets"]) == 4:
        self.ukuleledefs.append(dtive.chorddef)
      else:
        self.guitardefs.append(dtive.chorddef)
    self.directives.append(dtive)
    
  def process(self):
    rvalue = True
    lineno = 0 # before lyrics
    self.lines = self.data.splitlines(True)
    for line in self.lines:
      #print(line)
      if line.find("#") == 0 or line.find("{") >= 0:
        self.command(line, lineno)
      else:
        lineno += 1
        if len(line) > self.width:
          self.width = len(line)
        line = line.replace("", "↓")  # down arrows
        line = line.replace("’", "\'") # fancy quotes
        self.lyrics.append(line)
      if lineno > 10 and self.title == "":
        self.lyrics = []
        rvalue = False
        break
    #print("process:", rvalue)
    return rvalue

  def zoom(self, value):
    self.textsize += value
    if self.textsize < 16:
      self.textsize = 16
    if self.textsize > 52:
      self.textsize = 52
    #print (self.textsize)
    self.display()
    return self.textsize    

  def setchordcolor(self, value):
    self.chordcolor = value
    self.display()

  def display(self):
    face = "Monospace"
    if wx.Platform == "__WXMSW__":
      face = "Lucida Console"
    if wx.Platform == "__WXMAC__":
      face = "Menlo"
    choruson = False
    highlighton = False
    cordattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    if self.chordcolor == 1:
      cordattr = wx.TextAttr(wx.Colour(180,0,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 2:
      cordattr = wx.TextAttr(wx.Colour(0,0,180), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 3:
      cordattr = wx.TextAttr(wx.Colour(0,180,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    boldattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    fontattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    itlcattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_NORMAL, False, face))
    boldattr.SetBackgroundColour(wx.WHITE)
    highlight = wx.Colour(200,200,200) #grey

    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      cd += 1
    rtc = self.mx.control
    #if wx.Platform == "__WXMSW__":
    rtc.Hide()
    rtc.Clear()
    rtc.SetDefaultStyle(boldattr)
    rtc.WriteText(self.tab + self.title.center(self.width) + "\n" + self.tab + self.subtitle.center(self.width) + "\n")
    rtc.SetDefaultStyle(fontattr)
    self.mx.SetTitle(self.title + " - " + self.subtitle);
    l = 0
    for lyric in self.lyrics:
      #print(l,";",lyric[:-1])
      #print("cd < len:", cd, len(self.directives))
      while cd < len(self.directives) and self.directives[cd].y == l:
        #print("y == l:", cd, self.directives[cd].y, l)
        d = self.directives[cd]
        if d.name == "start_of_chorus" or d.name == "soc":
          #print("start_of_chorus");
          choruson = True
        if d.name == "end_of_chorus" or d.name == "eoc":
          choruson = False
          #print("end_of_chorus");
        if d.name == "start_of_bridge" or d.name == "sob":
          highlighton = True
          #print("start_of_chorus");
          #cordattr.SetBackgroundColour(highlight)
          #fontattr.SetBackgroundColour(highlight)
        if d.name == "end_of_bridge" or d.name == "eob":
          highlighton = False
          #cordattr.SetBackgroundColour(wx.WHITE)
          #fontattr.SetBackgroundColour(wx.WHITE)
          #choruson = False
          #print("end_of_chorus");
        if d.name == "comment" or d.name == "c":
          rtc.SetDefaultStyle(boldattr)
          if choruson:
            rtc.WriteText(self.tab)
          rtc.WriteText(self.tab + d.text + "\n")
          rtc.SetDefaultStyle(fontattr)       
        if d.name == "comment_italic" or d.name == "ci":
          #print("comment:", d.text)
          rtc.SetDefaultStyle(itlcattr)
          if choruson:
            rtc.WriteText(self.tab)
          rtc.WriteText(self.tab + d.text + "\n")
          rtc.SetDefaultStyle(fontattr)
        cd += 1
      s = 0
      fontattr.SetBackgroundColour(wx.WHITE)
      rtc.SetDefaultStyle(fontattr)
      rtc.WriteText(self.tab) # normal tab
      if choruson:
        rtc.WriteText(self.tab) # chorus tab
      if highlighton:
        fontattr.SetBackgroundColour(highlight)
        cordattr.SetBackgroundColour(highlight)
        rtc.SetDefaultStyle(fontattr)
      else:
        cordattr.SetBackgroundColour(wx.WHITE)
      # if no chords then remove intro outro lines
      if self.chordcolor < 0:
        if lyric.lower().find("intro:") >= 0 or lyric.lower().find("outro:") >= 0:
          l += 1
          continue
        # remove timing hints for no chords
        lyric = lyric.replace('/','');
        lyric = lyric.replace('↑','')
        lyric = lyric.replace('↓','')
        lyric = lyric.replace('|', '')
      while True:
        cs = lyric.find('[',s)
        if cs < 0:
          rtc.WriteText(lyric[s:])
          break
        else:
          ce = lyric.find(']',s)
          if ce < 0:
            rtc.WriteText(lyric[s:])
            break
          rtc.WriteText(lyric[s:cs])
          if self.chordcolor >= 0:
            rtc.SetDefaultStyle(cordattr)
            rtc.WriteText(lyric[cs:ce+1])
            chord = lyric[cs+1:ce]
            self.setchord(chord)
            rtc.SetDefaultStyle(fontattr)
          s = ce + 1
          if s >= len(lyric):
            break
      l += 1
    #if wx.Platform == "__WXMSW__":
    rtc.SetInsertionPoint(0) # PC hac
    rtc.Show()
  
  def setchord(self, cs):
    # remove timing and strumming directives
    if (cs[0] < 'A' or cs[0] > 'G') and (cs[0] < 'a' or cs[0] > 'g'):
      return
    while cs[-1] == '/' or cs[-1] == '^' or cs[-1] == ' ' or cs[-1] == '↓' or cs[-1] == '↑' or cs[-1] == '*' or cs[-1] == '|' or cs[-1] == '~':
      if len(cs) > 1:
        cs = cs[:-1]
      else:
        break
    if cs not in self.chords:
      self.chords.append(cs)
      
