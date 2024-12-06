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
    self.tab = "    "
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

  def transform(self, value):
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
          oldfound = False
          newchord = ""
          for look in self.scalelookup:
            if oldchord.find(look["chord"]) == 0:
              oldfound = True
              oldlen = len(look["chord"])
              oldidx = look["index"]
              newidx = oldidx + value
              if newidx < 1:
                newidx = 12
              if newidx > 12:
                newidx = 1
              newchord = self.scale[newidx] + oldchord[oldlen:]
              break
          if oldfound:
            newlyric += newchord
          else:
            newlyric += oldchord
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
    cordattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    if self.chordcolor == 1:
      cordattr = wx.TextAttr(wx.Colour(120,0,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 2:
      cordattr = wx.TextAttr(wx.Colour(0,0,180), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 3:
      cordattr = wx.TextAttr(wx.Colour(0,100,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    boldattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    fontattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    itlcattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_NORMAL, False, face))
    
    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      cd += 1
    rtc = self.mx.control
    #if wx.Platform == "__WXMSW__":
    rtc.Hide()
    rtc.Clear()
    rtc.SetDefaultStyle(boldattr)
    rtc.WriteText(self.title.center(self.width) + "\n" + self.subtitle.center(self.width) + "\n")
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
        if d.name == "comment" or d.name == "c" or\
           d.name == "comment_italic" or d.name == "ci":
          #print("comment:", d.text)
          rtc.SetDefaultStyle(itlcattr)
          rtc.WriteText(self.tab + d.text + "\n")
          rtc.SetDefaultStyle(fontattr)
        cd += 1
      s = 0
      rtc.WriteText(self.tab) # normal tab
      if choruson:
        rtc.WriteText(self.tab) # chorus tab
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
          rtc.SetDefaultStyle(cordattr)
          rtc.WriteText(lyric[cs:ce+1])
          rtc.SetDefaultStyle(fontattr)
          s = ce + 1
          if s >= len(lyric):
            break
      l += 1
    #if wx.Platform == "__WXMSW__":
    rtc.SetInsertionPoint(0) # PC hac
    rtc.Show()
  