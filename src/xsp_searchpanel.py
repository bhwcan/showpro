import wx
from xsp_songgrid import SongGrid

class SearchPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, pp):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.pp = pp
    self.SetSize(1200,800)
    self.searchlist = None
    self.insearch = False
    self.search = ""
    self.operator = "And"
    self.search2 = ""
    self.numrows = 100

    self.db = db
    #self.db.open()

    fontattr = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    
    # the combobox Control
    self.searchbutton = wx.Button(self, label="Search")
    self.searchtxt1 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchop = wx.ComboBox(self, choices=["And", "Or", "Not" ], style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.searchop.SetValue("And")
    self.searchtxt2 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchclear = wx.Button(self, label="Clear")

    self.grid = SongGrid(self, self.numrows, self.db, self.mf) 
    self.grid.SetColSize(0, 50)
    self.grid.SetColSize(1, 50)
    self.grid.SetColSize(2, 300)
    self.grid.SetColSize(3, 310)
    self.grid.SetColSize(4, 100)
    self.grid.SetColSize(5, 310)

    self.searchbutton.Bind(wx.EVT_BUTTON, self.on_button_click)
    self.searchtxt1.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchtxt2.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchclear.Bind(wx.EVT_BUTTON, self.on_button_clear)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.searchbutton, 0, wx.ALL, 10)
    topsizer.Add(self.searchtxt1, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchop, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchtxt2, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchclear, 0, wx.ALL, 10)
 
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
      if value != 1:
        notebook.ChangeSelection(value)
        notebook.GetParent().GetParent().pages[value].grid.SetFocus()
    else:
      event.Skip()

  def on_button_clear(self, event):
    self.searchtxt1.Clear()
    self.searchop.SetValue("And")
    self.searchtxt2.Clear()
    self.grid.ClearGrid()
    
  def on_button_click(self, event):
    self.search = self.searchtxt1.GetValue().strip().lower()
    self.operator = self.searchop.GetValue()
    self.search2 = self.searchtxt2.GetValue().strip().lower()
    self.searchlist = self.db.search(self.search, self.operator, self.search2)
    if self.grid.getcurrentsortcol() != 0:
      self.searchlist = sorted(self.searchlist, key=lambda x: x[self.grid.getcurrentsortcol()])
    self.insearch = True
    self.grid.gridsongs(self.searchlist)
    
