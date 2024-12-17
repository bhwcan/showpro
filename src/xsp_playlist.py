import wx
import pathlib
import json
import copy
from xsp_playlistgrid import PlayListGrid

class ListPanel(wx.Panel):
  def __init__(self, parent, mainframe, db):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.numrows = 1
    self.editlist = [ "Unsaved" ]
    self.playlists = {}
    self.currentplaylist = "Unsaved"
    self.db = db
    self.defaultpath = db.getplaylistpath()

    self.playlists[self.currentplaylist] = {}
    self.playlists[self.currentplaylist]["filename"] = ""
    self.playlists[self.currentplaylist]["songs"] = []
    self.editbox = wx.ComboBox(self, choices=self.editlist, size=(200,-1), style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.editbox.SetValue(self.editlist[0])
    self.clearbutton = wx.Button(self, label="Clear")
    self.saveasbutton = wx.Button(self, label="Save")
    self.openbutton = wx.Button(self, label="Open")
    self.deletebutton = wx.Button(self, label="Delete")
   
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    #self.savebutton.Bind(wx.EVT_BUTTON, self.on_save)
    self.clearbutton.Bind(wx.EVT_BUTTON, self.on_clear)
    self.saveasbutton.Bind(wx.EVT_BUTTON, self.on_saveas)
    self.openbutton.Bind(wx.EVT_BUTTON, self.on_open)
    self.deletebutton.Bind(wx.EVT_BUTTON, self.on_delete)
    self.editbox.Bind(wx.EVT_COMBOBOX, self.listselect)

    self.grid = PlayListGrid(self, self.numrows, self.db, self.mf) 
    self.grid.SetColSize(0, 50)
    self.grid.SetColSize(1, 50)
    self.grid.SetColSize(2, 300)
    self.grid.SetColSize(3, 310)
    self.grid.SetColSize(4, 100)
    self.grid.SetColSize(5, 310)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.editbox, 2, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.openbutton, 0, wx.ALL, 10)
    topsizer.Add(self.saveasbutton, 0, wx.ALL, 10)
    topsizer.Add(self.clearbutton, 0, wx.ALL, 10)
    topsizer.Add(self.deletebutton, 0, wx.ALL, 10)
 
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_LEFT)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    self.SetSizerAndFit(sizer)

    self.grid.gridsongs()
    self.Show()

  def on_delete(self, event):
    if self.currentplaylist != "Unsaved":
      filename = self.playlists[self.currentplaylist]["filename"]
      dlg = wx.MessageDialog(self,
                             "Delete Filename:\n" + filename,
                             caption="Delete PlayList: "+ self.currentplaylist,
                             style=wx.OK|wx.CANCEL)

      if dlg.ShowModal() == wx.ID_OK:
        selected = self.editbox.GetSelection()
        self.editbox.SetValue("Unsaved")
        self.editbox.Delete(selected)
        self.currentplaylist = "Unsaved"
        self.grid.gridsongs(self.playlists[self.currentplaylist]["songs"])
        self.db.deletefile(filename)
        
       # Shows it
      dlg.Destroy() # finally destroy it when finished.

  def on_saveas(self, event):
    newopen = True
    if self.currentplaylist == "Unsaved":
      defaultfile = ""
    else:
      defaultfile = self.currentplaylist
    with wx.FileDialog(self, "Save Playlist file", wildcard="Playlist files (*.plf)|*.plf", defaultFile=defaultfile,
                       defaultDir=self.defaultpath, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

      if fileDialog.ShowModal() == wx.ID_CANCEL:
        return     # the user changed their mind

      # save the current contents in the file
      pathname = fileDialog.GetPath()
      suffix = pathlib.Path(pathname).suffix
      if not suffix:
        pathname += ".plf"
      #print(pathname)
      name = pathlib.Path(pathname).stem
      if name in self.playlists:
        newopen = False
      if newopen:
        self.playlists[name] = copy.deepcopy(self.playlists[self.currentplaylist])
        self.playlists[name]["filename"] = pathname
      try:
        with open(pathname, 'w') as file:
          json.dump(self.playlists[name]["songs"], file)
          if newopen:
            self.editbox.Append(name)
          self.editbox.SetValue(name)
          self.currentplaylist = name
      except:
        del self.playlists[name]
        wx.LogError("Cannot save current data in file '%s'." % pathname)

  def on_open(self,event):
    with wx.FileDialog(self, "Save Playlist file", wildcard="Playlist files (*.plf)|*.plf",
                       defaultDir=self.defaultpath, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

      if fileDialog.ShowModal() == wx.ID_CANCEL:
        return     # the user changed their mind

      newlist = False
      # save the current contents in the file
      pathname = fileDialog.GetPath()
      name = pathlib.Path(pathname).stem
      if name not in self.playlists:
        self.playlists[name] = {}
        newlist = True
        #print("open new: ", name, pathname)
      self.playlists[name]["filename"] = pathname
      try:
        with open(pathname, 'r') as file:
          self.playlists[name]["songs"] = json.load(file)
          if newlist:
            self.editbox.Append(name)
          self.editbox.SetValue(name)
          self.currentplaylist = name
          self.grid.gridsongs(self.playlists[self.currentplaylist]["songs"])
      except:
        del self.playlists[name]
        wx.LogError("Cannot open current data in file '%s'." % pathname)
  
  def listselect(self, event):
    self.currentplaylist = self.editbox.GetValue()
    self.grid.gridsongs(self.playlists[self.currentplaylist]["songs"])

  def on_clear(self, event):
    self.grid.gridclear()
    self.playlists[self.currentplaylist]["songs"] = []
    self.statussongs()
   
#  def on_save(self, event):
#    self.grid.gridsongs()

  def addsong(self, song):
    self.playlists[self.currentplaylist]["songs"].append(song)
    return self.currentplaylist

  def showsongs(self):
    self.grid.gridsongs(self.playlists[self.currentplaylist]["songs"])
    self.statussongs()
    
  def statussongs(self):
    self.Parent.Parent.Parent.setstatus(str(len(self.playlists[self.currentplaylist]["songs"])) + " playlist songs")
    self.Parent.Parent.Parent.setstatus2("")
    
  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key)
    if key == 27: # Esc for quit
      self.mf.Parent.Close(True)
    elif key > 48 and key < 52 and event.AltDown(): # Alt 1,2,4 for window tabs
      notebook = self.GetParent()
      value = key - 49
      if value != 2:
        notebook.ChangeSelection(value)
        notebook.GetParent().GetParent().pages[value].grid.SetFocus()
    else:
      event.Skip()
