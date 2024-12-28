import wx

class NewFile(wx.Dialog):

  def __init__(self, parent, booklist, defaultbook):
    wx.Dialog.__init__(self, parent)

    self.booklist = booklist
    self.defaultbook = defaultbook
    self.init()
    self.SetSize((250, 380))
    self.SetTitle("Create New Chordpro file")

    self.book = ""
    self.title = ""
    self.subtitle = ""

  def init(self):

    ibox = wx.BoxSizer(wx.VERTICAL)
    bookprompt = wx.StaticText(self, label="Book")
    self.bookinput = wx.ComboBox(self, choices=self.booklist, size=(240,-1), style=wx.CB_DROPDOWN)
    if len(self.defaultbook) > 0:
      self.bookinput.SetValue(self.defaultbook)
    titleprompt = wx.StaticText(self, label="Title")
    self.titleinput = wx.TextCtrl(self, size=(240,-1))
    subtitleprompt = wx.StaticText(self, label="Subtitle")
    self.subtitleinput = wx.TextCtrl(self, size=(240,-1))
    #bbox = self.CreateButtonSizer(wx.OK | wx.CANCEL)
    ibox.AddSpacer(20)
    ibox.Add(bookprompt, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.Add(self.bookinput, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.AddSpacer(20)
    ibox.Add(titleprompt, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.Add(self.titleinput, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.AddSpacer(20)
    ibox.Add(subtitleprompt, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.Add(self.subtitleinput, flag=wx.LEFT | wx.RIGHT, border=5)
    ibox.AddSpacer(20)

    bbox = wx.BoxSizer(wx.HORIZONTAL)
    okButton = wx.Button(self, label='Ok')
    closeButton = wx.Button(self, label='Close')
    bbox.Add(okButton, flag=wx.LEFT, border=5)
    bbox.Add(closeButton, flag=wx.LEFT, border=64)
    ibox.Add(bbox)

    okButton.Bind(wx.EVT_BUTTON, self.OnOk)
    closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
  
    self.SetSizer(ibox)

  def OnOk(self, e):

    self.book = self.bookinput.GetValue()
    self.title = self.titleinput.GetValue()
    self.subtitle = self.subtitleinput.GetValue()
    self.EndModal(wx.ID_OK)

  def OnClose(self, e):

    self.EndModal(wx.ID_CANCEL)


