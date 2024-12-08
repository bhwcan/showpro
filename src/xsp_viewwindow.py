import wx
import webbrowser

from xsp_song import Song

class ViewWindow(wx.Frame):
  def __init__(self, parent):
    self.dirname=""
    self.filename=""
    self.song = None
    self.textsize = 20
    self.chordcolor = 0
    self.row = 0

    wx.Frame.__init__(self, parent, size=(1200,800), style=wx.DEFAULT_FRAME_STYLE &~ wx.CLOSE_BOX) #wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION)
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    #self.CreateStatusBar() # A Statusbar in the bottom of the window
    # self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    # Setting up the menu.
    filemenu= wx.Menu()
    #menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to view")
    menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")

    zoommenu = wx.Menu()
    menuZoomIn = zoommenu.Append(wx.ID_ZOOM_IN, "Zoom &In", "Zoom in text size")
    menuZoomOut = zoommenu.Append(wx.ID_ZOOM_OUT, "Zoom &Out", "Zoom out text size")
    
    # Setting up the menu.
    chordmenu= wx.Menu()
    chordBold = chordmenu.Append(1001, "&Bold","Set chords to bold")
    chordRed = chordmenu.Append(1002, "&Red", "Set chord to red")
    chordBlue = chordmenu.Append(1003, "&Blue", "Set chords to blue")
    chordGreen= chordmenu.Append(1004, "&Green","Set chords to green")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    menuBar.Append(zoommenu,"&Zoom") # Adding the "filemenu" to the MenuBar
    menuBar.Append(chordmenu,"&Color") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    # Events.
    #self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_MENU, self.OnZoomIn, menuZoomIn)
    self.Bind(wx.EVT_MENU, self.OnZoomOut, menuZoomOut)
    self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    self.Bind(wx.EVT_MENU, self.OnBold, chordBold)
    self.Bind(wx.EVT_MENU, self.OnRed, chordRed)
    self.Bind(wx.EVT_MENU, self.OnBlue, chordBlue)
    self.Bind(wx.EVT_MENU, self.OnGreen, chordGreen)
    self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)

    self.Raise()
    self.Show()
    
  def OnTextURL(self, event):
    #print('OnTextURL')
    if event.MouseEvent.LeftUp():
        #print(event.GetURLStart(), event.GetURLEnd())
        url = self.control.GetRange(event.GetURLStart(), event.GetURLEnd())
        #print(url)
        webbrowser.open_new_tab(url)
    event.Skip()

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
