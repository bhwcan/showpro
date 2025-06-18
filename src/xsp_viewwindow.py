import wx
import webbrowser

from xsp_song import Song
from xsp_chords import ChordWindow
  
class ViewWindow(wx.Frame):
  def __init__(self, parent, db, viewrect):
    self.db = db
    self.dirname=""
    self.filename=""
    self.song = None
    self.textsize = 20
    self.chordcolor = 0
    self.row = 0
    self.viewrect = viewrect
    self.chordframe = None
    self.songtitles = True
    self.instrument = "ukulele"

    parent.vf = self

    wx.Frame.__init__(self, parent, size=(1200,800), style=wx.DEFAULT_FRAME_STYLE &~ wx.CLOSE_BOX)
    self.SetPosition(wx.Point(viewrect[0], viewrect[1]+30)) # for mac top bar
    self.SetSize(wx.Size(viewrect[2],viewrect[3]-70)) # for mac top bar and window bottom

    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)

     # Events.
    #self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)
    self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    self.control.Bind(wx.EVT_MOUSE_EVENTS, self.mouse)
    self.control.Bind(wx.EVT_GESTURE_ZOOM, self.zoom)

    #self.Show()

  def zoom(self, event):
#    if event.IsGestureStart():
#      print("Start: ", event.GetZoomFactor())
    if event.IsGestureEnd():
      factor = event.GetZoomFactor()
      if factor > 1.0:
        self.OnZoomIn(event)
      else:
        self.OnZoomOut(event)
    self.control.SetFocus()
    #event.Skip()
    
  def mouse(self, event):
    if event.IsButton() and event.GetButton() == 1:
        if event.ButtonDown():
          #print("Right Button Up")
          viewrect = self.GetScreenRect()
          xdivider = viewrect[2] // 4
          ydivider = viewrect[3] // 5
          #print("Rectangle:", viewrect)
          #print("X", event.X, "divider:", xdivider, xdivider*3)
          grid = self.GetParent().pages[self.GetParent().currentpage].grid
          if event.X > xdivider * 3:
            #print("Forward")
            grid.ChangeSong(1)
            self.control.SetFocus()
          elif event.X > xdivider:
            if event.Y < ydivider:
              if self.instrument == "ukulele":
                self.displayUkuleleChords()
                self.ResetFocus()
              elif self.instrument == "guitar":
                self.displayGuitarChords()
                self.ResetFocus()
              else:
                self.control.SetFocus()
          else:
            #print("Back")
            grid.ChangeSong(-1)
            self.control.SetFocus()
    else:
      event.Skip()

# Right click for next song - shakes stand
#  def mouse(self, event):
#    if event.IsButton():
#      if event.GetButton() == 3:
#        if event.ButtonUp():
#          #print("Right Button Up")
#          viewrect = self.GetScreenRect()
#          divider = viewrect[3] // 3
#          #print("Rectangle:", viewrect)
#          #print("X", event.X, "divider:", divider)
#          grid = self.GetParent().pages[self.GetParent().currentpage].grid
#          if event.X > divider:
#            #print("Forward")
#            grid.ChangeSong(1)
#            self.control.SetFocus()
#          else:
#            #print("Back")
#            grid.ChangeSong(-1)
#            self.control.SetFocus()
#      elif event.Button() == 1:
#        if event.ButtonDown():
#          self.control.SetFocus()
#      else:
#        event.Skip()  
#    else:
#      event.Skip()
        
  def ToggleFullScreen(self, event):
    self.ShowFullScreen(not self.IsFullScreen())

  def ChangeFocus(self, event):
    p = self.GetParent()
    p.pages[p.currentpage].SetFocus()
    p.Raise()

  def on_key_pressed(self,event):
    p = self.GetParent()
    #print("current page:", p.currentpage)
    grid = p.pages[p.currentpage].grid
    key = event.GetKeyCode()
    #print(key, chr(key))
    if key == 350: #F11 - does not work on mac
      self.ToggleFullScreen(event)
    elif key == 85 and event.ControlDown(): # ctrl-U
      self.instrument = "ukulele"
    elif key == 71 and event.ControlDown(): # ctrl-G
      self.instrument = "guitar"
    elif key == 84 and event.ControlDown(): # ctrl-T
      if self.songtitles:
        self.songtitles = False
      else:
        self.songtitles = True
      if self.song != None:
        self.song.settitles(self.songtitles)
        self.song.display()
        self.control.SetFocus()
    elif key == 47: #/ slash to change focus
      self.ChangeFocus(event)
    elif key == 45: # dash zoom in
      self.OnZoomOut(event)
      self.control.SetFocus()
    elif key == 61: # equal zoom out
      self.OnZoomIn(event)
      self.control.SetFocus()
    elif key == 314: # leftarrow previous song
      grid.ChangeSong(-1)
      self.control.SetFocus()
    elif key == 316: # rightarrow next song
      grid.ChangeSong(1)
      self.control.SetFocus()
    elif key == 59: #; print chords
      self.displayUkuleleChords()
      self.ResetFocus()
    elif key == 39: #; print chords
      self.displayGuitarChords()
      self.ResetFocus()
    elif key == 317 and wx.Platform == "__WXMSW__": # override on windows
      self.control.ScrollLines(1)
    elif key == 315 and wx.Platform == "__WXMSW__":
      self.control.ScrollLines(-1)
    else:
      grid.on_key_pressed(event)
      self.ResetFocus()
      #self.control.SetFocus()
      #event.Skip()

  def ResetFocus(self):
    #print("ViewWindow Reset Focus")
#    self.control.SetInsertionPoint(0)
    self.control.SetFocus()
    self.Raise()

  def OnTextURL(self, event):
    #print('OnTextURL')
    if event.MouseEvent.LeftUp():
        #print(event.GetURLStart(), event.GetURLEnd())
        url = self.control.GetRange(event.GetURLStart(), event.GetURLEnd())
        #print(url)
        webbrowser.open_new_tab(url)
    event.Skip()

  def displayGuitarChords(self):

    if self.song == None:
      return

    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None
      return
    
    chorddefs = []
    undefined = []

    for cn in self.song.chords:
      found = False
      for cl in self.song.guitardefs: # check song defines for chord
        if cl["name"] == cn:
          found = True
          chorddefs.append(cl)
          break
      #print(cn)
      if not found:
        cd = self.db.find_guitardef(cn)
        if cd == None:
          undefined.append(cn)
        else:
          chorddefs.append(cd)

    self.chordframe = ChordWindow(self, "Guitar Chords", 6, undefined, chorddefs, self.chordcolor)
    return
    
  def displayUkuleleChords(self):

    if self.song == None:
      return
    
    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None
      return
    
    chorddefs = []
    undefined = []

    for cn in self.song.chords:
      found = False
      for cl in self.song.ukuleledefs: # check song defines for chord
        if cl["name"] == cn:
          found = True
          chorddefs.append(cl)
          break
      #print(cn)
      if not found:
        cd = self.db.find_ukuleledef(cn)
        if cd == None:
          undefined.append(cn)
        else:
          chorddefs.append(cd)

    self.chordframe = ChordWindow(self, "Ukulele Chords", 4, undefined, chorddefs, self.chordcolor)
    return
    
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
      self.textsize = self.song.zoom(2)

  def OnZoomOut(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(-2)
      
  def OnAbout(self,e):
    # Create a message dialog box
    dlg = wx.MessageDialog(self,
                           " A simple chordpro viewer and database\n"\
                           " for large dislplay monitors \n\n"\
                           "    by Byron Walton\n"\
                           "    bhwcan@netscape.net",
                           "About XShowPro", wx.OK)
    dlg.ShowModal() # Shows it
    dlg.Destroy() # finally destroy it when finished.

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

  def opensong(self, data):
    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None
    
    self.song = Song(self, self.textsize, self.chordcolor, data)
    self.song.settitles(self.songtitles)
    rvalue = self.song.process()
    if not rvalue:
      dlg = wx.MessageDialog(self,
                             " File: " + self.filename + "\n",
                             "Invalid file", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal() # Shows it
      dlg.Destroy() # finally destroy it when finished.
    return rvalue
