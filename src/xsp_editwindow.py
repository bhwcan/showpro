import wx
from xsp_editfind import EditFind

class EditWindow(wx.Frame):
  def __init__(self, parent, bookvalue, filevalue, pos, size):
    self.filevalue = filevalue
    self.bookvalue = bookvalue
    self.findopen = False
    self.finddata = wx.FindReplaceData()
    self.db = parent.db

    self.filename = self.db.getsongpath(bookvalue, filevalue)
    wx.Frame.__init__(self, parent, title=self.filename, pos=pos,size=size, style=wx.DEFAULT_FRAME_STYLE)

    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    face = "Monospace"
    if wx.Platform == "__WXMSW__":
      face = "Lucida Console"
    if wx.Platform == "__WXMAC__":
      face = "Menlo"
    font=wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face)
    self.control.SetFont(font)
    data = self.db.readsong(bookvalue, filevalue)
    self.control.SetValue(data)
    #self.control.LoadFile(filename)
    self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    # Setting up the menu.
    filemenu= wx.Menu()
    menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save file")
    menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the window")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
    self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    self.Show()

  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    if key == 83 and event.ControlDown(): # ctrl-s save
      self.saveFile()
    elif key == 81 and event.ControlDown(): # ctrl-q quit
      self.OnExit(event)
    elif key == 70 and event.ControlDown(): # ctrl-f find
      if not self.findopen:
        dlg = EditFind(self)
        self.findopen = True
    else:
      event.Skip()
      
  def OnSave(self,e):
    self.saveFile()


  def saveFile(self):
    if self.control.IsModified:
      self.db.writesong(self.bookvalue, self.filevalue, self.control.GetValue())
      self.Parent.Parent.Parent.Parent.Parent.setstatus2(self.filename + " saved")


  def OnExit(self,e):
    #print("editwindow exit")
    self.Close(True)  # Close the frame.

