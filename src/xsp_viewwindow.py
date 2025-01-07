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

    parent.vf = self

    wx.Frame.__init__(self, parent, size=(1200,800), style=wx.DEFAULT_FRAME_STYLE &~ wx.CLOSE_BOX) #wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION)
    self.SetPosition(wx.Point(viewrect[0], viewrect[1]+30)) # for mac top bar
    self.SetSize(wx.Size(viewrect[2],viewrect[3]-70)) # for mac top bar and window bottom

    #self.EnableFullScreenView()

    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    #self.CreateStatusBar() # A Statusbar in the bottom of the window
    # self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

     # Events.
    #self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)
    self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    self.Raise()
    self.Show()

  def ToggleFullScreen(self, event):
    self.ShowFullScreen(not self.IsFullScreen())

  def ChangeFocus(self, event):
    p = self.GetParent()
    p.pages[p.currentpage].SetFocus()
    p.Raise()
  
  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key, chr(key))
    if key == 350: #F11 - does not work on mac
      self.ToggleFullScreen(event)
    elif key == 47: #/ slash to change focus
      self.ChangeFocus(event)
    elif key == 59: #; print chords
      self.displayUkuleleChords()
    elif key == 39: #; print chords
      self.displayGuitarChords()
    else:
     p = self.GetParent()
     p.pages[p.currentpage].grid.on_key_pressed(event)
     self.control.SetFocus()
     #event.Skip()

  def OnTextURL(self, event):
    #print('OnTextURL')
    if event.MouseEvent.LeftUp():
        #print(event.GetURLStart(), event.GetURLEnd())
        url = self.control.GetRange(event.GetURLStart(), event.GetURLEnd())
        #print(url)
        webbrowser.open_new_tab(url)
    event.Skip()

  def displayGuitarChords(self):
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

    chordframe = ChordWindow(self, "Guitar Chords", self.db.get_guitartunning(), undefined, chorddefs)
    chordframe.SetPosition(wx.Point(self.viewrect[2]-401, self.viewrect[1]+30)) # for mac top bar
    
  def displayUkuleleChords(self):
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

    chordframe = ChordWindow(self, "Ukulele Chords", self.db.get_ukuleletunning(), undefined, chorddefs)
    chordframe.SetPosition(wx.Point(self.viewrect[2]-401, self.viewrect[1]+30)) # for mac top bar
    
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
    self.song = Song(self, self.textsize, self.chordcolor, data)
    rvalue = self.song.process()
    if not rvalue:
      dlg = wx.MessageDialog(self,
                             " File: " + self.filename + "\n",
                             "Invalid file", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal() # Shows it
      dlg.Destroy() # finally destroy it when finished.
    return rvalue
