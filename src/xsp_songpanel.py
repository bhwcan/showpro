import wx
from xsp_songgrid import SongGrid

class SongPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, display):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.books = {}
    self.currentbook = "All"
    self.searchlist = None
    self.display = display
    self.insearch = False
    self.search = ""
    self.operator = "And"
    self.search2 = ""

    self.db = db
    self.db.open()

    fontattr = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    
    # the combobox Control
    self.booklist = []
    books = self.db.getBooks()
    for book in books:
      self.booklist.append(book[0])
    self.lblbook = wx.StaticText(self, label="Book")
    self.lblbook.SetFont(fontattr)
    self.editbook = wx.ComboBox(self, choices=self.booklist, style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.editbook.SetValue(self.currentbook)
    self.searchbutton = wx.Button(self, label="Search")
    self.searchtxt1 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchop = wx.ComboBox(self, choices=["And", "Or", "Not" ], style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.searchop.SetValue("And")
    self.searchtxt2 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
    self.searchclear = wx.Button(self, label="Clear")
    self.rebuildbutton = wx.Button(self, label="Rebuild")

    self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.numrows = len(self.books[self.currentbook])
    self.grid = SongGrid(self, self.numrows, self.db, self.mf) 
    self.loadbook()
    self.grid.sizeColumns()

    self.searchbutton.Bind(wx.EVT_BUTTON, self.on_button_click)
    self.searchtxt1.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchtxt2.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.editbook.Bind(wx.EVT_COMBOBOX, self.bookselect)
    self.searchclear.Bind(wx.EVT_BUTTON, self.on_button_clear)
#    self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    self.rebuildbutton.Bind(wx.EVT_BUTTON, self.rebuildindexes)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.lblbook, 0, wx.ALL, 10)
    topsizer.Add(self.editbook, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchbutton, 0, wx.ALL, 10)
    topsizer.Add(self.searchtxt1, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchop, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchtxt2, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.searchclear, 0, wx.ALL, 10)
    topsizer.Add(self.rebuildbutton, 0, wx.ALL, 10)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_CENTER)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    #sizer.SetSizeHints(self)
    self.SetSizerAndFit(sizer)

    self.Show()

  def rebuildindexes(self,event):
    currentfound = False
    self.db.rebuild(self.Parent)
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
    if key == 66: # b for book
      #print("B pressed")
      self.editbook.Popup()
    elif key == 83: # s for search
      self.searchtxt1.SetFocus()
    elif key == 67: # c for clear
      self.on_button_clear(event)
    elif key == 81: # q for quit
      self.mf.Parent.Close(True)
    else:
      event.Skip()

  def setstars(self, sidstr, book, filename, value):
    data = self.db.readsong(book, filename)
    starstring = "#showpro: {}\n".format(value)
    first = True
    if data.find("#showpro:") == 0:
      cr = data.find('\n')
      if ord(data[cr]) == 10:
        cr = cr + 1
      data = starstring + data[cr:]
    else:
      data = starstring + data
    #print(data)
    #exit(10)
    self.db.writesong(book, filename, data)
    # this should work if the file was found
    sid = int(sidstr)
    self.db.setSongValue(sid, 0, value)
    if book in self.books:
      del self.books[book]
    if "All" in self.books: 
      del self.books["All"]
    if self.insearch:
      self.searchlist = sorted(self.db.search(self.search, self.operator, self.search2), key=lambda x: x[self.currentsortcol])
      self.grid.gridsongs(self.searchlist)
    else:
      self.loadbook()

  def loadbook(self):
    if self.currentbook not in self.books:
      self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.books[self.currentbook] = sorted(self.db.getSongs(self.currentbook), key=lambda x: x[self.grid.getcurrentsortcol()])
    if self.insearch:
      self.searchtxt1.Clear()
      self.searchop.SetValue("And")
      self.searchtxt2.Clear()
      self.insearch = False
    self.grid.gridsongs(self.books[self.currentbook])
    self.Parent.setstatus(str(len(self.books[self.currentbook])) + " book songs")

  def sortcol(self, col):
    if self.insearch:
      self.searchlist = sorted(self.searchlist, key=lambda x: x[col])
      self.grid.gridsongs(self.searchlist)
    else:
      if col != self.currentsortcol:
        self.books[self.currentbook] = sorted(self.books[self.currentbook], key=lambda x: x[col])
        self.loadbook()
    self.currentsortcol = col
    
  def on_label_click(self, event):
    col = event.GetCol()
    self.sortcol(col)

  def bookselect(self, event):
    self.currentbook = self.editbook.GetValue()
    self.loadbook()

  def on_button_clear(self, event):
    self.searchtxt1.Clear()
    self.searchop.SetValue("And")
    self.searchtxt2.Clear()
    self.editbook.SetValue(self.currentbook)
    self.loadbook()
    
  def on_button_click(self, event):
    self.editbook.SetValue("All") # reset the book to all if search clicked
    self.search = self.searchtxt1.GetValue().strip().lower()
    self.operator = self.searchop.GetValue()
    self.search2 = self.searchtxt2.GetValue().strip().lower()
    self.searchlist = self.db.search(self.search, self.operator, self.search2)
    if self.grid.getcurrentsortcol() != 0:
      self.searchlist = sorted(self.searchlist, key=lambda x: x[self.grid.getcurrentsortcol()])
    self.insearch = True
    self.grid.gridsongs(self.searchlist)
    
