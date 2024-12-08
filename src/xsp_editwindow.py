import wx

class EditWindow(wx.Frame):
  def __init__(self, parent, filename):
    self.filename = filename

    wx.Frame.__init__(self, parent, title=filename, size=(800,600), style=wx.DEFAULT_FRAME_STYLE)

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

    self.Show()

  def OnSave(self,e):
    if self.control.IsModified:
      self.control.SaveFile(self.filename)

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

