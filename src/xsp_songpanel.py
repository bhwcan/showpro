import wx
from xsp_songgrid import SongGrid

class SongPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, pp):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.books = {}
    self.currentbook = "All"
    self.pp = pp
    self.db = db
    #self.db.open()

#    fontattr = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    
    # the combobox Control
    self.booklist = []
    books = self.db.getBooks()
    for book in books:
      self.booklist.append(book[0])
    self.editbook = wx.ComboBox(self, choices=self.booklist, style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.editbook.SetValue(self.currentbook)
    self.rebuildbutton = wx.Button(self, label="Rebuild")

    self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.numrows = len(self.books[self.currentbook])
    self.grid = SongGrid(self, self.numrows, self.db, self.mf) 
    self.loadbook()
    self.grid.sizeColumns()

    self.editbook.Bind(wx.EVT_COMBOBOX, self.bookselect)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    self.rebuildbutton.Bind(wx.EVT_BUTTON, self.rebuildindexes)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.editbook, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.rebuildbutton, 0, wx.ALL, 10)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_LEFT)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    #sizer.SetSizeHints(self)
    self.SetSizerAndFit(sizer)

    self.Show()

  def rebuildindexes(self,event):
    currentfound = False
    self.db.rebuild(self.GetParent().GetParent().GetParent())
    self.booklist = []
    books = self.db.getBooks()
    self.editbook.Clear()
    for book in books:
      if self.currentbook == book[0]:
        currentfound = True
      self.booklist.append(book[0])
      self.editbook.Append(book[0])
    #slprint(self.currentbook, books)
    if not currentfound:
      self.currentbook = "All"
    self.editbook.SetValue(self.currentbook)
    self.books = {}
    self.loadbook()
    self.insearch = False
    
  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key)
    if key == 27: # Esc for quit
      self.mf.Parent.Close(True)
    elif key == 13 and event.AltDown():
      #print("Alt Enter")
      song = self.addtoplaylist()
    elif key > 48 and key < 52 and event.AltDown(): # Alt 1,2,4 for window tabs
      notebook = self.GetParent()
      value = key - 49
      if value != 0:
        notebook.ChangeSelection(value)
        notebook.GetParent().GetParent().pages[value].grid.SetFocus()
    else:
      event.Skip()

  def addtoplaylist(self):
      song = self.grid.getcurrentsong()
      if song:
        playlist = self.pp.addsong(song)
        self.Parent.Parent.Parent.setstatus2(song[4] + " - " + song[2] + " added to playlist [" + playlist + "]")

  def loadbook(self):
    if self.currentbook not in self.books:
      self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.books[self.currentbook] = sorted(self.db.getSongs(self.currentbook), key=lambda x: x[self.grid.getcurrentsortcol()])
    self.grid.gridsongs(self.books[self.currentbook])
    self.Parent.Parent.Parent.setstatus(str(len(self.books[self.currentbook])) + " book songs")

  def bookselect(self, event):
    self.currentbook = self.editbook.GetValue()
    self.loadbook()

    
