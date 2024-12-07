import wx

class SongWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1200,780))
    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(1)
    #self.resetstatus()
    #self.statusbar.SetStatusText("no status")
    self.Show()

  def setstatus(self, text):
    #print(text)
    self.statusbar.SetStatusText(text, 0)

