import wx
from xsp_viewwindow import ViewWindow
from xsp_displays import Displays
from xsp_songpanel import SongPanel
from xsp_searchpanel import SearchPanel
from xsp_playlist import ListPanel

class MainWindow(wx.Frame):
  def __init__(self, db):
    wx.Frame.__init__(self, None, title="XshowPro", size=(1200,780))

    self.db = db
    self.db.open()
    self.pages = []
    self.currentpage = 0

    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(2)
    self.statusbar.SetStatusWidths([-1,-4])

    displays = Displays()
    viewrect = displays.getViewRect()
    listrect = displays.getListRect()

    self.SetPosition(wx.Point(listrect[0], listrect[1]+30))
    self.vf = ViewWindow(self)
    self.vf.SetPosition(wx.Point(viewrect[0], viewrect[1]+30)) # for mac top bar
    self.vf.SetSize(wx.Size(viewrect[2],viewrect[3]-70)) # for mac top bar and window bottom

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
    self.currentpage = event.GetSelection()
    #print("new page:", page)
    self.pages[self.currentpage].showsongs()
      
  def setstatus(self, text):
    #print(text)
    self.statusbar.SetStatusText(text, 0)

  def setstatus2(self, text):
    self.statusbar.SetStatusText(text, 1)
