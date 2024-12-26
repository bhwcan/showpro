import wx

class EditWindow(wx.Frame):
  def __init__(self, parent, filename, pos, size):
    self.filename = filename

    wx.Frame.__init__(self, parent, title=filename, pos=pos,size=size, style=wx.DEFAULT_FRAME_STYLE)

    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    font=wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    self.control.SetFont(font)
    self.control.LoadFile(filename)

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
    if key == 83 and event.ControlDown(): # ctrl-s save
      self.saveFile()
    elif key == 81 and event.ControlDown(): # ctrl-q quit
      self.OnExit(self, event)
    else:
      event.Skip()
      
  def OnSave(self,e):
    self.saveFile()


  def saveFile(self):
    if self.control.IsModified:
      self.control.SaveFile(self.filename)
      self.Parent.Parent.Parent.Parent.Parent.setstatus2(self.filename + " saved")


  def OnExit(self,e):
    print("editwindow exit")
    self.Close(True)  # Close the frame.

