import wx

class SongWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1200,780))
    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(2, [-1, -4])
    self.resetstatus()
    #self.statusbar.SetStatusText("no status")
    self.Show()

  def resetstatus(self):
    self.statusbar.SetStatusText(
      "Keys: [Enter] view [e] edit [b] book, [s] search [c] clear"\
      " [o] order column [q] quit [0-3] stars [DEL] red [z-x] zoom [t-y-u] transpose [v] color"\
      " [m-k] scoll",1)

