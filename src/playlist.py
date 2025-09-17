import wx
import os
import json
import string
import pathlib
#from pathlib import Path

class PlayList():
  def __init__(self, parent):
    self.parent = parent
    self.on = False
    self.current = 0
    self.list = {}
    self.path = os.path.join(pathlib.Path.home(), "Documents", "showpro")
    self.defaultpath = os.path.join(self.path, "playlists")
    self.pathname = ""

  def currentFile(self):
    # use last for file name for compatability
    l = len(self.list[self.current])
    #print(self.list[self.current], "length=", l)
    return os.path.join(self.path, self.list[self.current][4], self.list[self.current][l-1])

  def open(self):
    self.on = False
    with wx.FileDialog(self.parent, "Open Playlist file", wildcard="Playlist files (*.plf)|*.plf",
                       defaultDir=self.defaultpath, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

      if fileDialog.ShowModal() == wx.ID_CANCEL:
        return     # the user changed their mind
      self.pathname = fileDialog.GetPath()
      self.openfile(self.pathname)

  def openfile(self, filename):
    self.current = 0
    self.pathname = filename
    self.name = pathlib.Path(self.pathname).stem
    if os.path.exists(self.pathname):
      with open(self.pathname, "r") as pf:
        self.list = json.load(pf)
      num = 1
      for song in self.list:
        #print(song)
        #print("length:", len(song))
        if len(song) < 7:
          #print("append:", song[5])
          song.append(song[5])
        song[5] = num
        #print(song)
        num += 1
    else:
      return
  
    #print(self.list)
    #print("======================")
    #self.current = 1
    #print(self.list[1])
    self.on = True
    self.parent.opensong(self.currentFile())
    self.parent.song.display()
    #print(self.currentFile(), self.name)
    self.parent.statusbar.SetStatusText(self.name)

  def select(self):
    songlist = []
    for song in self.list:
      strvalue = "{:4d} - {}".format(song[5], song[2])
      songlist.append(strvalue)
    # Create the dialog with a list of choices
    dlg = wx.SingleChoiceDialog(
      self.parent,
      self.name,
      "Select Song",
      songlist,
      wx.CHOICEDLG_STYLE
    )
    dlg.SetSelection(self.current)
    # Show the dialog and check the result
    if dlg.ShowModal() == wx.ID_OK:
      self.current = dlg.GetSelection()
      self.parent.opensong(self.currentFile())
      self.parent.song.display()

    # Clean up the dialog
    dlg.Destroy()


  def close(self):
    self.on = False
    self.current = 0
    self.list = {}
    self.parent.statusbar.SetStatusText(" ")

  def next(self):
    if self.on and self.current < (len(self.list)-1):
      self.current += 1
    else:
      return
    self.parent.opensong(self.currentFile())
    self.parent.song.display()

  def previous(self):
    if self.on and self.current > 0:
      self.current -= 1
    else:
      return
    self.parent.opensong(self.currentFile())
    self.parent.song.display()

