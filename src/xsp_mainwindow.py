import wx
from xsp_viewwindow import ViewWindow
from xsp_displays import Displays
from xsp_songpanel import SongPanel
from xsp_searchpanel import SearchPanel
from xsp_playlist import ListPanel

class MainWindow(wx.Frame):
  def __init__(self, db):
    wx.Frame.__init__(self, None, title="XshowPro")

    self.db = db
    self.pages = []
    self.currentpage = 0

    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(2)
    self.statusbar.SetStatusWidths([-1,-4])

    if (not db.open()):
      dlg = wx.MessageDialog(None,
        "System may require a rebuild to operate.\n",
        "Database Open Error.", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal() # Shows it
      dlg.Destroy() # finally destroy it when finished.

    displays = Displays()
    viewrect = displays.getViewRect()
    listrect = displays.getListRect()

    self.SetPosition(wx.Point(listrect[0], listrect[1]+30))
    self.SetSize(listrect[2]-60, listrect[3]-120)
    self.vf = ViewWindow(self, db, viewrect)
    self.vf.Raise()

    # Here we create a panel and a notebook on the panel
    p = wx.Panel(self)
    self.nb = wx.Notebook(p)
    self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.pagechanged)

    pp = ListPanel(self.nb, self.vf, db)
    bp = SongPanel(self.nb, self.vf, db, pp)
    sp = SearchPanel(self.nb, self.vf, db, pp)
    self.pages.append(bp)
    self.pages.append(sp)
    self.pages.append(pp)

    # add the pages to the notebook with the label to show on the tab
    self.nb.AddPage(self.pages[0], "Books")
    self.nb.AddPage(self.pages[1], "Search")
    self.nb.AddPage(self.pages[2], "PlayList")

    # put the notebook in a sizer for the panel to manage
    # the layout
    sizer = wx.BoxSizer()
    sizer.Add(self.nb, 1, wx.EXPAND)
    p.SetSizer(sizer)

  def pagechanged(self, event):
    #grid = self.pages[self.currentpage].grid
    #if grid.chordframe != None:
    #  grid.chordframe.Close(True)
    #  grid.chordframe = None
    self.currentpage = event.GetSelection()
    #print("new page:", self.currentpage)
    self.pages[self.currentpage].showsongs()
      
  def setstatus(self, text):
    #print(text)
    self.statusbar.SetStatusText(text, 0)

  def setstatus2(self, text):
    self.statusbar.SetStatusText(text, 1)

  def start(self):
    self.Show()
    self.vf.Show()
