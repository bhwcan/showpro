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
    self.showtitles = True
    self.showtabs = True
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

  def splitChords(self, inchord):
    oldchords = []
    for split in ("/", "add"):
      splitchords = inchord.split(split)
      if len(splitchords) > 1 and len(splitchords[1]) > 0 \
         and splitchords[1][0] >= 'A' and splitchords[1][0] <= 'G':
        splitchords[1] = split.join(splitchords[1:])
        oldchords.append(splitchords[0])
        oldchords.append(splitchords[1])
        #print("oldchords:", splitchords[0], splitchords[1])
        break
    if len(oldchords) == 0:
      split = ""
      oldchords.append(inchord)
    return split, oldchords

  def transposeChord(self, inchord, value):
    newchords = []
    split, oldchords = self.splitChords(inchord)
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
      output += self.directives[cd].line + "\n"
      cd += 1
    l = 0
    for lyric in self.lyrics:
      while cd < len(self.directives) and self.directives[cd].y == l:
        output += self.directives[cd].line + "\n"
        cd += 1
      output += lyric + "\n"
      l += 1
    while cd < len(self.directives):
      output += self.directives[cd].line + "\n"
      cd += 1
    #print(output)
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
    self.lines = self.data.splitlines()
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
    if self.textsize < 12:
      self.textsize = 12
    if self.textsize > 52:
      self.textsize = 52
    #print (self.textsize)
    if self.textsize < 16:
      self.tab = "    "
    elif self.textsize < 24:
      self.tab = "   "
    elif self.textsize < 32:
      self.tab = "  "
    elif self.textsize < 40:
      self.tab = " "
    else:
      self.tab = ""
    self.display()
    return self.textsize    

  def setchordcolor(self, value):
    self.chordcolor = value
    self.display()

  def settitles(self, value):
    self.showtitles = value
    self.showtabs = value
    
  def display(self):
    face = "Monospace"
    if wx.Platform == "__WXMSW__":
      face = "Lucida Console"
    if wx.Platform == "__WXMAC__":
      face = "Menlo"
    choruson = False
    highlighton = False
    bluelighton = False
    tabon = False

    defaulttextcolour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
    defaultbgcolour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

    if defaultbgcolour[0] < 46:
      highlight = wx.Colour(80,80,80) #grey
      bluelight = wx.Colour(21,69,77)
      red = wx.Colour(255,51,51)
      blue = wx.Colour(51,137,255)
      green = wx.Colour(0,180,0)
    else:
      highlight = wx.Colour(180,180,180) #grey
      bluelight = wx.Colour(171,219,227)
      red = wx.Colour(180,0,0)
      blue = wx.Colour(0,0,180)
      green = wx.Colour(0,90,0)

    cordattr = wx.TextAttr(defaulttextcolour, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    commentattr = wx.TextAttr(defaulttextcolour, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    if self.chordcolor == 1:
      cordattr = wx.TextAttr(red, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
      commentattr = wx.TextAttr(red, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    elif self.chordcolor == 2:
      cordattr = wx.TextAttr(blue, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
      commentattr = wx.TextAttr(blue, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    elif self.chordcolor == 3:
      cordattr = wx.TextAttr(green, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
      commentattr = wx.TextAttr(green, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    boldattr = wx.TextAttr(defaulttextcolour, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    fontattr = wx.TextAttr(defaulttextcolour, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    itlcattr = wx.TextAttr(defaulttextcolour, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_NORMAL, False, face))
    boldattr.SetBackgroundColour(defaultbgcolour)

    #if wx.Platform == "__WXMSW__":
    rtc = self.mx.control
    rtc.Hide()
    rtc.Clear()
    if self.showtitles:
      rtc.SetDefaultStyle(boldattr)
      rtc.WriteText(self.tab + self.title.center(self.width) + "\n" + self.tab + self.subtitle.center(self.width) + "\n")
    rtc.SetDefaultStyle(fontattr)
    self.mx.SetTitle(self.title + " - " + self.subtitle);
    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      if self.showtitles and self.directives[cd].name == "artist":
        rtc.SetDefaultStyle(boldattr)
        rtc.WriteText(self.tab + self.directives[cd].text.center(self.width) + "\n")
        rtc.SetDefaultStyle(fontattr)
      cd += 1
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
          highlighton = True
        if d.name == "end_of_chorus" or d.name == "eoc":
          choruson = False
          highlighton = False
          #print("end_of_chorus");
        if d.name == "start_of_tab" or d.name == "sot":
          #print("start_of_chorus");
          tabon = True
        if d.name == "end_of_tab" or d.name == "eot":
          tabon = False
          #print("end_of_chorus");
        if d.name == "start_of_bridge" or d.name == "sob":
          bluelighton = True
        if d.name == "start_of_highlight" or d.name == "soh":
          highlighton = True
          #print("start_of_chorus");
          #cordattr.SetBackgroundColour(highlight)
          #fontattr.SetBackgroundColour(highlight)
        if d.name == "end_of_bridge" or d.name == "eob":
          bluelighton = False
        if d.name == "end_of_highlight" or d.name == "eoh":
          highlighton = False
          #cordattr.SetBackgroundColour(defaultbgcolour)
          #fontattr.SetBackgroundColour(defaultbgcolour)
          #choruson = False
          #print("end_of_chorus");
        if d.name == "comment" or d.name == "c":
          if self.chordcolor >= 0:
            fontattr.SetBackgroundColour(defaultbgcolour)
            rtc.SetDefaultStyle(fontattr)       
            if choruson:
              rtc.WriteText(self.tab)
            if self.showtabs:
              rtc.WriteText(self.tab)
            if highlighton:
              commentattr.SetBackgroundColour(highlight)
            else:
              commentattr.SetBackgroundColour(defaultbgcolour)
            rtc.SetDefaultStyle(commentattr)
            rtc.WriteText(d.text)
            rtc.SetDefaultStyle(fontattr)       
            rtc.WriteText("\n")
        if d.name == "comment_italic" or d.name == "ci":
          if self.chordcolor >= 0:
            fontattr.SetBackgroundColour(defaultbgcolour)
            rtc.SetDefaultStyle(fontattr)       
            if choruson:
              rtc.WriteText(self.tab)
            if self.showtabs:
              rtc.WriteText(self.tab)
            if highlighton:
              itlcattr.SetBackgroundColour(highlight)
            else:
              itlcattr.SetBackgroundColour(defaultbgcolour)
            rtc.SetDefaultStyle(itlcattr)
            rtc.WriteText(d.text)
            rtc.SetDefaultStyle(fontattr)       
            rtc.WriteText("\n")
        cd += 1
      s = 0
      # if no chords then remove intro outro lines
      if self.chordcolor < 0:
        if tabon or lyric.lower().find("intro:") >= 0 \
           or lyric.lower().find("outro:") >= 0 \
           or lyric.lower().find("riff:") >= 0 \
           or lyric.find("<") == 0:
          l += 1
          continue
        # remove timing hints for no chords
        lyric = lyric.replace('/','');
        lyric = lyric.replace('↑','')
        lyric = lyric.replace('↓','')
        lyric = lyric.replace('|', '')
      fontattr.SetBackgroundColour(defaultbgcolour)
      rtc.SetDefaultStyle(fontattr)
      if self.showtabs:
        rtc.WriteText(self.tab) # normal tab
      if choruson:
        rtc.WriteText(self.tab) # chorus tab
      if highlighton or bluelighton:
        if highlighton:
          fontattr.SetBackgroundColour(highlight)
          cordattr.SetBackgroundColour(highlight)
          rtc.SetDefaultStyle(fontattr)
        if bluelighton:
          fontattr.SetBackgroundColour(bluelight)
          cordattr.SetBackgroundColour(bluelight)
          rtc.SetDefaultStyle(fontattr)
      else:
        cordattr.SetBackgroundColour(defaultbgcolour)
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
            chord = lyric[cs+1:ce]
            if self.setchord(chord):
              rtc.WriteText(lyric[cs:ce+1])
            else:
              # if not valid chord remove square brackets
              rtc.WriteText(lyric[cs+1:ce])
            rtc.SetDefaultStyle(fontattr)
          s = ce + 1
          if s >= len(lyric):
            break
          
      # stop highlight for new line
      fontattr.SetBackgroundColour(defaultbgcolour)
      rtc.SetDefaultStyle(fontattr)
      rtc.WriteText("\n")
      if highlighton:
        fontattr.SetBackgroundColour(highlight)
        rtc.SetDefaultStyle(fontattr)
      if bluelighton:
        fontattr.SetBackgroundColour(bluelight)
        rtc.SetDefaultStyle(fontattr)
  
      l += 1
    #if wx.Platform == "__WXMSW__":
    rtc.SetInsertionPoint(0) # PC hac
    rtc.Show()
  
  def setchord(self, cs):
    # remove timing and strumming directives
    if len(cs) < 1:
      return False
    if (cs[0] < 'A' or cs[0] > 'G') and (cs[0] < 'a' or cs[0] > 'g'):
      return False
    while cs[-1] == '/' or cs[-1] == '^' or cs[-1] == ' ' or cs[-1] == '↓' or cs[-1] == '↑' or cs[-1] == '*' or cs[-1] == '|' or cs[-1] == '~':
      if len(cs) > 1:
        cs = cs[:-1]
      else:
        break
    if cs not in self.chords:
      self.chords.append(cs)
    return True
      
