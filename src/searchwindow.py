import wx
from searchgrid import SearchGrid

class SearchPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, pp):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.pp = pp
    self.SetSize(1200,800)
    self.searchlist = []
    self.search = ""
    self.operator = "And"
    self.search2 = ""
    self.numrows = 100
    self.parent = parent

    self.db = db
    #self.db.open()

    fontattr = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    
    # the combobox Control
    self.searchtxt1 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchtxt2 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchop = wx.ComboBox(self, choices=["And", "Or", "Not" ], style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.searchop.SetValue("And")
    self.searchclear = wx.Button(self, label="Clear")
    self.searchbutton = wx.Button(self, label="Search")

    self.grid = SearchGrid(self, self.numrows, self.db) 

    self.searchbutton.Bind(wx.EVT_BUTTON, self.on_button_click)
    self.searchtxt1.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchtxt2.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchclear.Bind(wx.EVT_BUTTON, self.on_button_clear)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.searchtxt1, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchtxt2, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchop, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchclear, 0, wx.ALL, 10)
    topsizer.Add(self.searchbutton, 0, wx.ALL, 10)
 
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_LEFT)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    self.SetSizerAndFit(sizer)

    self.Show()

  def showsongs(self):
    self.parent.setstatus(str(len(self.searchlist)) + " search songs")
    self.parent.setstatus2("")
   
  def on_button_clear(self, event):
    self.searchtxt1.Clear()
    self.searchop.SetValue("And")
    self.searchtxt2.Clear()
    self.grid.ClearGrid()
    self.searchlist = []
    self.showsongs()
    
  def on_button_click(self, event):
    self.search = self.searchtxt1.GetValue().strip().lower()
    self.operator = self.searchop.GetValue()
    self.search2 = self.searchtxt2.GetValue().strip().lower()
    self.searchlist = self.db.search(self.search, self.operator, self.search2)
    self.searchlist = self.grid.sortsongs(self.searchlist, self.grid.getcurrentsortcol())
    self.grid.gridsongs(self.searchlist)
    self.showsongs()

class SearchWindow(wx.Frame):
  def __init__(self, parent, db):
    wx.Frame.__init__(self, None, title="Song Search",size=(925,600))
    self.parent = parent
    self.db = db

    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(2)
    self.statusbar.SetStatusWidths([-1,-4])

    self.sp = SearchPanel(self, self.Parent, db, None)

    # put the notebook in a sizer for the panel to manage
    # the layout
    sizer = wx.BoxSizer()
    sizer.Add(self.sp, 1, wx.EXPAND)
    self.SetSizer(sizer)
   
  def setstatus(self, text):
    #print(text)
    self.statusbar.SetStatusText(text, 0)

  def setstatus2(self, text):
    self.statusbar.SetStatusText(text, 1)

  def start(self):
    self.Show()
