import wx
import wx.grid
from xsp_editwindow import EditWindow

class SongPanel(wx.Panel):
  def __init__(self, parent, mainframe, db, display):
    wx.Panel.__init__(self, parent)
    self.mf = mainframe
    self.SetSize(1200,800)
    self.books = {}
    self.currentbook = "All"
    self.currentsortcol = 0
    self.searchlist = None
    self.display = display
    self.insearch = False
    self.search = ""
    self.operator = "And"
    self.search2 = ""
    self.stars = [ "☆☆☆", "★☆☆", "★★☆", "★★★" ]
    self.colouredrows = []

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
    self.grid = wx.grid.Grid(self, size=(1200,600))
    self.grid.CreateGrid(self.numrows, 6)  # 20 rows, 4 columns
    #self.grid.SetDefaultCellFont(fontattr)
    self.grid.EnableEditing(False)
    self.grid.SetRowLabelSize(0)  # Hide row labels

    self.grid.SetColLabelValue(0, "Id")
    self.grid.SetColLabelValue(1, "Stars")
    self.grid.SetColLabelValue(2, "Title")
    self.grid.SetColLabelValue(3, "Subtitle")
    self.grid.SetColLabelValue(4, "Book")
    self.grid.SetColLabelValue(5, "File")
    self.loadbook()
    self.grid.AutoSizeColumn(0)
    self.grid.AutoSizeColumn(1)
    self.grid.SetColSize(2, 300)
    self.grid.SetColSize(3, 300)
    self.grid.AutoSizeColumn(4)
    self.grid.SetColSize(5, 300)
    self.grid.DisableDragRowSize()

    self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.searchbutton.Bind(wx.EVT_BUTTON, self.on_button_click)
    self.searchtxt1.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.searchtxt2.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
    self.editbook.Bind(wx.EVT_COMBOBOX, self.bookselect)
    self.searchclear.Bind(wx.EVT_BUTTON, self.on_button_clear)
    self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
    self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
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
    if key == 13: # Enter
      row = self.grid.GetGridCursorRow()
      filevalue = self.grid.GetCellValue(row,5)
      if len(filevalue) > 0:
        self.mf.opensong(self.db.readsong(self.grid.GetCellValue(row,4), filevalue))
        self.mf.song.display()
    elif key == 127: # DEL
      row = self.grid.GetGridCursorRow()
      filevalue = self.grid.GetCellValue(row,5)
      if len(filevalue) > 0:
        sidstr = self.grid.GetCellValue(row,0)
        book = self.grid.GetCellValue(row,4)
        self.setstars(sidstr, book, filevalue, -1)
    elif key == 69: # e for edit
      row = self.grid.GetGridCursorRow()
      filename = os.path.join(self.db.getpath(), self.grid.GetCellValue(row,4), self.grid.GetCellValue(row,5))
      editframe = EditWindow(self.mf, filename, self.display)
    elif key == 86: # v for view color (sick)
      if self.mf.song != None:
        color = self.mf.chordcolor
        color += 1
        if color > 3:
          color = 0
        self.mf.chordcolor = color
        self.mf.song.setchordcolor(color)
    elif key == 66: # b for book
      #print("B pressed")
      self.editbook.Popup()
    elif key == 83: # s for search
      self.searchtxt1.SetFocus()
    elif key == 67: # c for clear
      self.on_button_clear(event)
    elif key > 47 and key < 52: # 0-3 for number of stars
      row = self.grid.GetGridCursorRow()
      filevalue = self.grid.GetCellValue(row,5)
      if len(filevalue) > 0:
        sidstr = self.grid.GetCellValue(row,0)
        book = self.grid.GetCellValue(row,4)
        value = key - 48
        self.setstars(sidstr, book, filevalue, value)
    elif key == 90: # z zoom in
      self.mf.OnZoomIn(event)
    elif key == 88: # x zoom out
      self.mf.OnZoomOut(event)
    elif key == 84 or key == 61: # t tranpose up
      self.mf.OnPlus(event)
    elif key == 89 or key == 45: # y transpose down
      self.mf.OnMinus(event)
    elif key == 85: # u save transpose
      self.mf.OnSave(event)
    elif key == 77: # m move down
      self.mf.control.ScrollLines(1)
    elif key == 75: # k move up
      self.mf.control.ScrollLines(-1)
    elif key == 79: # o for order
      col = self.grid.GetGridCursorCol()
      self.sortcol(col)
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
      self.gridbook(self.searchlist)
    else:
      self.loadbook()

  def loadbook(self):
    if self.currentbook not in self.books:
      if self.currentsortcol  == 0:
        self.books[self.currentbook] = self.db.getSongs(self.currentbook)
      else:
        self.books[self.currentbook] = sorted(self.db.getSongs(self.currentbook), key=lambda x: x[self.currentsortcol])
    if self.insearch:
      self.searchtxt1.Clear()
      self.searchop.SetValue("And")
      self.searchtxt2.Clear()
      self.insearch = False
    self.gridbook(self.books[self.currentbook])
    
  def gridbook(self, book):
    #print(book)
    index = -1
    currentcol = self.grid.GetGridCursorCol()
    currentrow = self.grid.GetGridCursorRow()
    sindex = self.grid.GetCellValue(currentrow, 0)
    if len(sindex) > 0:
      index = int(sindex)
    #print('['+sindex+']', type(sindex), index)
    #index = int(sindex)
    #index = int(self.grid.GetCellValue(currentrow, 0))
    self.grid.ClearGrid()
    row = 0
    currentrow = 0
    if len(book) > self.numrows:
      appendrows = len(book) - self.numrows
      self.grid.AppendRows(appendrows)
      self.numrows = len(book)
    for cr in self.colouredrows: # reset colours
        self.grid.SetCellBackgroundColour(cr,1,wx.Colour(255,255,255))
    self.colouredrows = [] # reset colour list
    for song in book:
      #print(row, index, '=', song[0])
      if index > 0 and index == song[0]:
        #print("index found:", index, song[0])
        currentrow = row
      self.grid.SetCellValue(row, 0, str(song[0]))
      if song[1] == 0:
        self.grid.SetCellValue(row, 1, self.stars[song[1]])
      elif song[1] > 0:
        self.grid.SetCellValue(row, 1, self.stars[song[1]])
        if song[1] == 1:
          self.grid.SetCellBackgroundColour(row,1,wx.YELLOW)
        else:
          self.grid.SetCellBackgroundColour(row,1,wx.GREEN)
        self.colouredrows.append(row)
      else:
        self.grid.SetCellValue(row, 1, "DEL")
        self.grid.SetCellBackgroundColour(row,1,wx.RED)
        self.colouredrows.append(row)
      self.grid.SetCellValue(row, 2, song[2])
      self.grid.SetCellValue(row, 3, song[3])
      self.grid.SetCellValue(row, 4, song[4])
      self.grid.SetCellValue(row, 5, song[5])
      row += 1
    if self.insearch:
      songtxt = " search songs"
    else:
      songtxt = " book songs"
    self.Parent.setstatus(str(row) + songtxt)
    #print("set cursor at start", index, currentrow, currentcol)
    self.grid.SetGridCursor(currentrow,currentcol)
    self.grid.MakeCellVisible(currentrow,currentcol)
    self.grid.SetFocus()
    #wx.CallAfter(self.grid.SetGridCursor, 0, 1)

  def sortcol(self, col):
    if self.insearch:
      self.searchlist = sorted(self.searchlist, key=lambda x: x[col])
      self.gridbook(self.searchlist)
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
    if self.currentsortcol != 0:
      self.searchlist = sorted(self.searchlist, key=lambda x: x[self.currentsortcol])
    self.insearch = True
    self.gridbook(self.searchlist)
    
  def on_cell_click(self, event):
    #print("Cell clicked:", event.GetRow(), event.GetCol())
    row = event.GetRow()
    col = event.GetCol()
    bookvalue = self.grid.GetCellValue(row,4)
    filevalue = self.grid.GetCellValue(row,5)
    if len(filevalue) > 0:
      filename = self.db.getsongpath(bookvalue, filevalue)
      if col != 5:
        #print("filename:", filename)
        self.mf.opensong(self.db.readsong(bookvalue, filevalue))
        self.mf.song.display()
      else:
        editframe = EditWindow(self.mf, self.db.getsongpath(bookvalue, filevalue), self.display)
        #subprocess.Popen(["emacs", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    event.Skip()
