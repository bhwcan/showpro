import wx
import os
import sys
import webbrowser

from xsp_song import Song
from xsp_directive import Directive
from chordbase import ChordBase
from xsp_chords import ChordWindow
from playlist import PlayList
      
class MainWindow(wx.Frame):
  def __init__(self, parent, title, filename):
    self.dirname=""
    self.filename=""
    self.song = None
    self.textsize = 14
    self.chordcolor = 2
    self.inline = True
    self.chordframe = None
    self.db = ChordBase()
    self.playlist = PlayList(self)

    wx.Frame.__init__(self, parent, title=title, size=(1200,800))
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window

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
    chordAbove = chordmenu.Append(1005, "&Above", "Chords above lyrics")
    chordInline = chordmenu.Append(1006, "&Inline", "Chords inline with lyrics")

    # Setting up the menu.
    transmenu= wx.Menu()
    transplus = transmenu.Append(2005, "Up &+","Transpose up one step")
    transminus = transmenu.Append(2006, "Down &-", "Transpose down one step")
    transave = transmenu.Append(wx.ID_SAVE, "&Save", "Save transformation to chordpro file")

    # Setting up the menu.
    chordxmenu= wx.Menu()
    chordxguitar = chordxmenu.Append(3007, "&Guitar","Display guitar chords")
    chordxukulele = chordxmenu.Append(3008, "&Ukulele", "Display ukulele chords")
    chordxoff = chordxmenu.Append(3009, "&Off", "Display no chords")

    # Setting up the menu.
    playlistmenu= wx.Menu()
    playlistselect = playlistmenu.Append(4012, "&Select","Select from list")
    playlistopen = playlistmenu.Append(4008, "&Open","Open play list")
    playlistnext = playlistmenu.Append(4009, "&Next","Next song")
    playlistprevious = playlistmenu.Append(4010, "&Previous","Previous song")
    playlistclose = playlistmenu.Append(4011, "&Close","Close play list")
 
    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    menuBar.Append(zoommenu,"&Zoom") # Adding the "filemenu" to the MenuBar
    menuBar.Append(chordmenu,"&View") # Adding the "filemenu" to the MenuBar
    menuBar.Append(transmenu,"&Transpose") # Adding the "filemenu" to the MenuBar
    menuBar.Append(chordxmenu,"&Chords") # Adding the "filemenu" to the MenuBar
    menuBar.Append(playlistmenu,"&Playlist") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    # Events.
    self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)
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
    self.Bind(wx.EVT_MENU, self.displayGuitarChords, chordxguitar)
    self.Bind(wx.EVT_MENU, self.displayUkuleleChords, chordxukulele)
    self.Bind(wx.EVT_MENU, self.displayOffChords, chordxoff)
    self.Bind(wx.EVT_MENU, self.OnAbove, chordAbove)
    self.Bind(wx.EVT_MENU, self.OnInline, chordInline)
    self.Bind(wx.EVT_MENU, self.OnPlayListOpen, playlistopen)
    self.Bind(wx.EVT_MENU, self.OnPlayListNext, playlistnext)
    self.Bind(wx.EVT_MENU, self.OnPlayListPrevious, playlistprevious)
    self.Bind(wx.EVT_MENU, self.OnPlayListClose, playlistclose)
    self.Bind(wx.EVT_MENU, self.OnPlayListSelect, playlistselect)
    self.control.Bind(wx.EVT_MOUSE_EVENTS, self.mouse)

    if filename != None:
      #print(filename, filename[-4:])
      if filename[-4:] == ".plf":
        self.playlist.openfile(filename)
      else:
        if self.opensong(filename):
          self.song.display()
        else:
          song = None

    self.Show()

  def OnTextURL(self, event):
    #print('OnTextURL')
    if event.MouseEvent.LeftUp():
        #print(event.GetURLStart(), event.GetURLEnd())
        url = self.control.GetRange(event.GetURLStart(), event.GetURLEnd())
        #print(url)
        webbrowser.open_new_tab(url)
    event.Skip()

  def ToggleFullScreen(self, event):
    self.ShowFullScreen(not self.IsFullScreen())

  def mouse(self, event):
    if event.ButtonDClick():
      self.ToggleFullScreen(event)
      return
    if self.playlist.on and event.IsButton() and event.GetButton() == 1:
      if event.ButtonDown():
        viewrect = self.GetScreenRect()
        xdivider = viewrect[2] // 4
        #print("Rectangle:", viewrect)
        #print("X", event.X, "divider:", xdivider, xdivider*3)
        if event.X > xdivider * 3:
          self.playlist.next()
        elif event.X < xdivider:
          self.playlist.previous()
        else:
          event.Skip()
      else:
        event.Skip()
    else:
      event.Skip()

  def OnPlayListSelect(self, e):
    self.playlist.select()

  def OnPlayListOpen(self, e):
    self.playlist.open()

  def OnPlayListClose(self, e):
    self.playlist.close()

  def OnPlayListNext(self, e):
    self.playlist.next()

  def OnPlayListPrevious(self, e):
    self.playlist.previous()

  def OnAbove(self, e):
    if self.inline == False:
      return
    self.inline = False
    self.song.display()

  def OnInline(self, e):
    if self.inline == True:
      return
    self.inline = True
    self.song.display()
    
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
    self.displayOffChords(e)
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

  def displayGuitarChords(self, e):

    if self.song == None:
      return

    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None
    
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

  def displayOffChords(self, e):
    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None

  def displayUkuleleChords(self, e):

    if self.song == None:
      return
    
    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None
    
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
