import wx
import os
import sys
import webbrowser
from pathlib import Path

from xsp_song import Song
from playlist import PlayList
from chordbase import ChordBase
from xsp_chords import ChordWindow

class MyFrame(wx.Frame):
  def __init__(self, parent, title):
    super(MyFrame, self).__init__(parent, title=title, size=(1200, 800))

    self.dirname = os.path.join(Path.home(), "Documents", "showpro")
    self.filename=""
    self.song = None
    self.textsize = 14
    self.chordcolor = 2
    self.inline = True
    self.chordframe = None
    self.db = ChordBase()
    self.playlist = PlayList(self)

    panel = wx.Panel(self)
    panel.SetBackgroundColour(wx.Colour(240, 240, 240))

    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    self.control = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    main_sizer.Add(self.control, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

    # In a vertical sizer:
    vbox = wx.BoxSizer(wx.VERTICAL)
    buttonfileopen = wx.Button(panel, label="File\nOpen")
    buttonplopen = wx.Button(panel, label="Playlist\nOpen")
    buttonplselect = wx.Button(panel, label="Playlist\nSelect")
    buttonplnext = wx.Button(panel, label="Playlist\nNext")
    buttonplprevious = wx.Button(panel, label="Playlist\nPrev")
    buttoninline = wx.Button(panel, label="Chords\nInline")
    buttonabove = wx.Button(panel, label="Chords\nAbove")
    buttonguitar = wx.Button(panel, label="Guitar\nChords")
    buttonukulele = wx.Button(panel, label="Ukulele\nChords")
    buttonscaleup = wx.Button(panel, label="Scale\nUp +")
    buttonscaledown = wx.Button(panel, label="Scale\nDown -")
    buttonzoomin = wx.Button(panel, label="Zoom\nIn +")
    buttonzoomout = wx.Button(panel, label="Zoom\nOut -")

    vbox.Add(buttonfileopen, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplopen, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplselect, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplnext, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplprevious, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttoninline, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonabove, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonguitar, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonukulele, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonscaleup, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonscaledown, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonzoomin, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonzoomout, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

    main_sizer.Add(vbox, proportion=0, flag=wx.EXPAND | wx.BOTTOM | wx.RIGHT, border=5)

    buttonfileopen.Bind(wx.EVT_BUTTON, self.OnOpen)
    buttonzoomin.Bind(wx.EVT_BUTTON, self.OnZoomIn)
    buttonzoomout.Bind(wx.EVT_BUTTON, self.OnZoomOut)
    buttoninline.Bind(wx.EVT_BUTTON, self.OnInline)
    buttonabove.Bind(wx.EVT_BUTTON, self.OnAbove)
    buttonscaleup.Bind(wx.EVT_BUTTON, self.OnPlus)
    buttonscaledown.Bind(wx.EVT_BUTTON, self.OnMinus)
    buttonplopen.Bind(wx.EVT_BUTTON, self.OnPlayListOpen)
    buttonplnext.Bind(wx.EVT_BUTTON, self.OnPlayListNext)
    buttonplprevious.Bind(wx.EVT_BUTTON, self.OnPlayListPrevious)
    buttonplselect.Bind(wx.EVT_BUTTON, self.OnPlayListSelect)
    buttonguitar.Bind(wx.EVT_BUTTON, self.displayGuitarChords)
    buttonukulele.Bind(wx.EVT_BUTTON, self.displayUkuleleChords)
    self.control.Bind(wx.EVT_MOUSE_EVENTS, self.mouse)
 
    panel.SetSizer(main_sizer)
    self.Layout()

  def ToggleFullScreen(self, event):
    self.ShowFullScreen(not self.IsFullScreen())
    
  def mouse(self, event):
    if event.ButtonDClick():
      self.ToggleFullScreen(event)
    else:
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

  def OnPlus(self,e):
    if self.song != None:
      self.song.transform(1)

  def OnMinus(self,e):
    if self.song != None:
      self.song.transform(-1)
      
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
    
  def OnZoomIn(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(4)

  def OnZoomOut(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(-4)
      
  def displayOffChords(self, e):
    if self.chordframe != None:
      self.chordframe.Close(True)
      self.chordframe = None

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
      if self.chordframe:
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
      if self.chordframe:
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

class MyApp(wx.App):
  def OnInit(self):
    frame = MyFrame(None, "Button Showpro")
    frame.Show(True)
    return True

if __name__ == '__main__':
  app = MyApp()
  app.MainLoop()
