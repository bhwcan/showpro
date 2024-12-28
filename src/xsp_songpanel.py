import wx
from xsp_songgrid import SongGrid
from xsp_newfile import NewFile

class SongPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, pp):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.books = {}
    self.currentbook = "All"
    self.pp = pp
    self.db = db
    self.booklist = None
    
    # the combobox Control
    self.loadbooklist()
    self.editbook = wx.ComboBox(self, choices=self.booklist, size=(200,-1), style=wx.CB_DROPDOWN|wx.TE_READONLY)
    self.editbook.SetValue(self.currentbook)
    self.rebuildbutton = wx.Button(self, label="Rebuild")
    self.newbutton = wx.Button(self, label="New Song")

    self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.numrows = len(self.books[self.currentbook])
    self.grid = SongGrid(self, self.numrows, self.db, self.mf) 
    self.loadbook()
    self.grid.sizeColumns()

    self.editbook.Bind(wx.EVT_COMBOBOX, self.bookselect)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
    self.rebuildbutton.Bind(wx.EVT_BUTTON, self.rebuildindexes)
    self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
    self.newbutton.Bind(wx.EVT_BUTTON, self.newsong)

    topsizer = wx.BoxSizer(wx.HORIZONTAL)
    topsizer.Add(self.editbook, 0, wx.EXPAND|wx.ALL, 10)
    topsizer.Add(self.newbutton, 0, wx.ALL, 10)
    topsizer.Add(self.rebuildbutton, 0, wx.ALL, 10)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(topsizer, 0, wx.ALIGN_LEFT)
    sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 10)
    #sizer.SetSizeHints(self)
    self.SetSizerAndFit(sizer)

    self.Show()

  def newsong(self, event):
    book = ""
    newlist = []
    if self.currentbook != "All":
      book = self.currentbook
    for nb in self.booklist:
      if nb != "All":
        newlist.append(nb)

    with NewFile(self, newlist, book) as dlg:
      dlg.ShowModal()
      
    rvalue = dlg.GetReturnCode()
    if rvalue != wx.ID_OK:
      return
    if dlg.book == "All" or not dlg.book or not dlg.title:
      errordlg = wx.MessageDialog(self,
                                  "Must have valid book and title",
                                  "Invalid Song",
                                  wx.OK|wx.ICON_ERROR)
      errordlg.ShowModal() # Shows it
      errordlg.Destroy() # finally destroy it when finished.
      return
    index = self.db.newsong(dlg.book, dlg.title, dlg.subtitle)
    self.currentbook = dlg.book
    if dlg.book not in self.booklist:
      self.loadbooklist()
      self.loadeditbook()
    self.editbook.SetValue(self.currentbook)
    self.books = {}
    self.loadbook(index)
      
  def loadbooklist(self):
    self.booklist = []
    books = self.db.getBooks()
    for book in books:
      if book[0] != "All":
        self.booklist.append(book[0])
    self.booklist = sorted(self.booklist)
    self.booklist.insert(0, "All")

  def loadeditbook(self):
    self.editbook.Clear()
    for be in self.booklist:
      self.editbook.Append(be)
      if self.currentbook == be:
        currentfound = True
    if not currentfound:
      self.currentbook = "All"
    self.editbook.SetValue(self.currentbook)
    
  def rebuildindexes(self,event):
    currentfound = False
    self.db.rebuild(self.GetParent().GetParent().GetParent())
    self.loadbooklist()
    self.loadeditbook()
    self.books = {}
    self.loadbook()
    
  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key)
    if key == 27: # Esc for quit
      self.mf.Parent.Close(True)
    elif key == 13 and event.AltDown():
      #print("Alt Enter")
      self.addtoplaylist()
    elif key > 48 and key < 52 and event.AltDown(): # Alt 1,2,4 for window tabs
      notebook = self.GetParent()
      value = key - 49
      if value != 0:
        notebook.ChangeSelection(value)
        notebook.GetParent().GetParent().pages[value].grid.SetFocus()
    else:
      event.Skip()

  def on_right_click(self, event):
    self.addtoplaylist()
    
  def addtoplaylist(self):
      song = self.grid.getcurrentsong()
      if song:
        playlist = self.pp.addsong(song)
        self.Parent.Parent.Parent.setstatus2(song[4] + " - " + song[2] + " added to playlist [" + playlist + "]")

  def loadbook(self, index=-1):
    if self.currentbook not in self.books:
      self.books[self.currentbook] = self.db.getSongs(self.currentbook)
    self.books[self.currentbook] = self.grid.sortsongs(self.db.getSongs(self.currentbook), self.grid.getcurrentsortcol())
    self.grid.gridsongs(self.books[self.currentbook], index)
    self.showsongs()

  def showsongs(self):
    self.Parent.Parent.Parent.setstatus(str(len(self.books[self.currentbook])) + " book songs")
    self.Parent.Parent.Parent.setstatus2("")

  def bookselect(self, event):
    self.currentbook = self.editbook.GetValue()
    self.loadbook()

    
