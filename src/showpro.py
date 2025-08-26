import wx
import os
import sys

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
      self.text = self.line[colon+1:end].strip()
    else:
      self.name = self.line[self.x+1:end].strip().lower()
    return self.name, self.text    
  
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
      if cd < len(self.directives):
        while self.directives[cd].y == l:
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
      if lineno > 1 and self.title == "":
        self.lyrics = []
        rvalue = False
        break
    #print("process:", rvalue)
    return rvalue

  def zoom(self, value):
    self.textsize += value
    if self.textsize < 14:
      self.textsize = 14
    if self.textsize > 48:
      self.textsize = 48
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
      cordattr = wx.TextAttr(wx.Colour(120,0,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 2:
      cordattr = wx.TextAttr(wx.Colour(0,0,180), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 3:
      cordattr = wx.TextAttr(wx.Colour(0,100,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    boldattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    fontattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    itlcattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_NORMAL, False, face))
    highlight = wx.Colour(200,200,200) #grey

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
        if d.name == "comment" or d.name == "c" or\
           d.name == "comment_italic" or d.name == "ci":
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
      
class MainWindow(wx.Frame):
  def __init__(self, parent, title, filename):
    self.dirname=""
    self.filename=""
    self.song = None
    self.textsize = 14
    self.chordcolor = 2

    wx.Frame.__init__(self, parent, title=title, size=(1200,800))
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
    self.CreateStatusBar() # A Statusbar in the bottom of the window

    # Setting up the menu.
    filemenu= wx.Menu()
    menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to view")
    menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
    menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

    zoommenu = wx.Menu()
    menuZoomIn = zoommenu.Append(wx.ID_ZOOM_IN, "Zoom &In", "Zoom in text size")
    menuZoomOut = zoommenu.Append(wx.ID_ZOOM_OUT, "Zoom &Out", "Zoom out text size")
    
    # Setting up the menu.
    chordmenu= wx.Menu()
    chordBold = chordmenu.Append(1001, "&Bold","Set chords to bold")
    chordRed = chordmenu.Append(1002, "&Red", "Set chord to red")
    chordBlue = chordmenu.Append(1003, "&Blue", "Set chords to blue")
    chordGreen= chordmenu.Append(1004, "&Green","Set chords to green")

    # Setting up the menu.
    transmenu= wx.Menu()
    transplus = transmenu.Append(2005, "Up &+","Transpose up one step")
    transminus = transmenu.Append(2006, "Down &-", "Transpose down one step")
    transave = transmenu.Append(wx.ID_SAVE, "&Save", "Save transformation to chordpro file")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    menuBar.Append(zoommenu,"&Zoom") # Adding the "filemenu" to the MenuBar
    menuBar.Append(chordmenu,"&Color") # Adding the "filemenu" to the MenuBar
    menuBar.Append(transmenu,"&Transpose") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    # Events.
    self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_MENU, self.OnZoomIn, menuZoomIn)
    self.Bind(wx.EVT_MENU, self.OnZoomOut, menuZoomOut)
    self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
    self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    self.Bind(wx.EVT_MENU, self.OnBold, chordBold)
    self.Bind(wx.EVT_MENU, self.OnRed, chordRed)
    self.Bind(wx.EVT_MENU, self.OnBlue, chordBlue)
    self.Bind(wx.EVT_MENU, self.OnGreen, chordGreen)
    self.Bind(wx.EVT_MENU, self.OnPlus, transplus)
    self.Bind(wx.EVT_MENU, self.OnMinus, transminus)
    self.Bind(wx.EVT_MENU, self.OnSave, transave)

    if filename != None:
      if self.opensong(filename):
        self.song.display()
      else:
        song = None

    self.Show()

  def OnPlus(self,e):
    if self.song != None:
      self.song.transform(1)

  def OnMinus(self,e):
    if self.song != None:
      self.song.transform(-1)

  def OnSave(self,e):
    if self.song != None:
      output = self.song.save()
      f = open(os.path.join(self.dirname, self.filename), 'w')
      f.write(output)
      f.close()
    
  def OnBold(self,e):
    self.chordcolor = 0
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnRed(self,e):
    self.chordcolor = 1
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnBlue(self,e):
    self.chordcolor = 2
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnGreen(self,e):
    self.chordcolor = 3
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnZoomIn(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(4)

  def OnZoomOut(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(-4)
      
  def OnAbout(self,e):
    # Create a message dialog box
    dlg = wx.MessageDialog(self,
                           " A simple chordpro viewer \n"\
                           " for large dislplay monitors \n\n"\
                           "    by Byron Walton\n"\
                           "    bhwcan@netscape.net",
                           "About Chordpro Show", wx.OK)
    dlg.ShowModal() # Shows it
    dlg.Destroy() # finally destroy it when finished.

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

  def opensong(self, filename):
    rvalue = True
    f = open(filename, 'r', encoding="utf-8", errors='ignore')
    data = f.read()
    #print (data)
    f.close()
    self.song = Song(self, self.textsize, self.chordcolor, data)
    rvalue = self.song.process()
    if not rvalue:
      dlg = wx.MessageDialog(self,
                             " File: " + self.filename + "\n",
                             "Invalid file", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal() # Shows it
      dlg.Destroy() # finally destroy it when finished.
    return rvalue

  def OnOpen(self,e):
    """ Open a file"""
    dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*pro;*.cho", wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      self.filename = dlg.GetFilename()
      self.dirname = dlg.GetDirectory()
    dlg.Destroy()
    filename = os.path.join(self.dirname, self.filename)
    if not self.opensong(filename):
      self.song.display()
      self.song = None
    else:
      self.song.display()

#MAIN
#print("platform:", wx.Platform)
filename = None
if len(sys.argv) > 1:
  filename = sys.argv[1]
  #if not filename.endswith("pro"):
  #  filename = None
app = wx.App(False)
frame = MainWindow(None, "Chordpro Show", filename)
app.MainLoop()
