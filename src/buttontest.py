import wx

class MyFrame(wx.Frame):
  def __init__(self, parent, title):
    super(MyFrame, self).__init__(parent, title=title, size=(1200, 800))


    panel = wx.Panel(self)
    panel.SetBackgroundColour(wx.Colour(240, 240, 240))

    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    self.control = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    # self.control = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    # self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    main_sizer.Add(self.control, 1, wx.EXPAND)

    # In a vertical sizer:
    vbox = wx.BoxSizer(wx.VERTICAL)
    buttonfileopen = wx.Button(panel, label="File\nOpen")
    buttonplopen = wx.Button(panel, label="Playlist\nOpen")
    buttonplselect = wx.Button(panel, label="Playlist\nSelect")
    buttonplnext = wx.Button(panel, label="Playlist\nNext")
    buttonplprevious = wx.Button(panel, label="Playlist\nPrev")
    buttoninline = wx.Button(panel, label="Chords\nInline")
    buttonabove = wx.Button(panel, label="Chords\nAbove")
    buttonguitar = wx.Button(panel, label="Guitar\nChords")
    buttonukulele = wx.Button(panel, label="Ukulele\nChords")
    buttonscaleup = wx.Button(panel, label="Scale\nUp +")
    buttonscaledown = wx.Button(panel, label="Scale\nDown -")
    buttonzoomin = wx.Button(panel, label="Zoom\nIn +")
    buttonzoomout = wx.Button(panel, label="Zoom\nOut -")

    vbox.Add(buttonfileopen, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplopen, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplselect, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplnext, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonplprevious, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttoninline, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonabove, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonguitar, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonukulele, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonscaleup, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonscaledown, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonzoomin, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
    vbox.Add(buttonzoomout, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

    main_sizer.Add(vbox, proportion=0, flag=wx.EXPAND | wx.BOTTOM | wx.RIGHT, border=5)

    panel.SetSizer(main_sizer)
    #self.Layout()

class MyApp(wx.App):
  def OnInit(self):
    frame = MyFrame(None, "Button Showpro")
    frame.Show(True)
    return True

if __name__ == '__main__':
  app = MyApp()
  app.MainLoop()
