import wx
from xsp_songgrid import SongGrid

class ListPanel(wx.Panel):
  def __init__(self, parent, mainframe, db):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.numrows = 100

    self.db = db
    #self.db.open()

    fontattr = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    
    # the combobox Control
    self.createbutton = wx.Button(self, label="Create")
    
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    self.grid = SongGrid(self, self.numrows, self.db, self.mf) 
    self.grid.SetColSize(0, 50)
    self.grid.SetColSize(1, 50)
    self.grid.SetColSize(2, 300)
    self.grid.SetColSize(3, 310)
    self.grid.SetColSize(4, 100)
    self.grid.SetColSize(5, 310)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.createbutton, 0, wx.ALL, 10)
 
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_LEFT)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    self.SetSizerAndFit(sizer)

    self.Show()

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
