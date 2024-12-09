import wx
import wx.grid
from xsp_editwindow import EditWindow

class SongGrid(wx.grid.Grid):
  def __init__(self, parent, rows, db, mf):
    wx.grid.Grid.__init__(self, parent, size=(1200,600))
    
    self.currentsortcol = 0
    self.colouredrows = []
    self.stars = [ "☆☆☆", "★☆☆", "★★☆", "★★★" ]
    self.songs = []
    self.numrows = rows
    self.numcols = 6
    self.db = db
    self.mf = mf
    self.collables = [ "Id", "Stars", "Title", "Subtitle", "Book", "File" ]
    self.colsortlables = [ "Id *", "Stars *", "Title *", "Subtitle *", "Book *", "File *" ]
   
    self.CreateGrid(rows, 6)  # 20 rows, 4 columns
    self.EnableEditing(False)
    self.SetRowLabelSize(0)  # Hide row labels
    self.DisableDragRowSize()

    for i in range(1, self.numcols):
      self.SetColLabelValue(i, self.collables[i])
    self.SetColLabelValue(self.currentsortcol, self.colsortlables[self.currentsortcol])

    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key)
    if key == 13: # Enter
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        self.mf.opensong(self.db.readsong(self.GetCellValue(row,4), filevalue))
        self.mf.song.display()
    elif key == 69: # e for edit
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        pos = self.Parent.Parent.GetPosition()
        pos[0] += 100
        pos[1] += 100
        size = self.Parent.Parent.GetSize()
        size[0] -= 200
        size[1] -= 200
        editframe = EditWindow(self, self.db.getsongpath(self.GetCellValue(row,4), filevalue), pos, size)
    elif key == 86: # v for view color (sick)
      if self.mf.song != None:
        color = self.mf.chordcolor
        color += 1
        if color > 3:
          color = 0
        self.mf.chordcolor = color
        self.mf.song.setchordcolor(color)
    elif key == 90: # z zoom in
      self.mf.OnZoomIn(event)
    elif key == 88: # x zoom out
      self.mf.OnZoomOut(event)
    elif key == 84 or key == 61: # t tranpose up
      self.mf.song.transform(1)
    elif key == 89 or key == 45: # y transpose down
      self.mf.song.transform(-1)
    elif key == 85: # u save transpose
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        self.db.writesong(self.GetCellValue(row,4), filevalue, self.mf.song.save())
    elif key == 77: # m move down
      self.mf.control.ScrollLines(1)
    elif key == 75: # k move up
      self.mf.control.ScrollLines(-1)
    elif key == 79: # o for order
      col = self.GetGridCursorCol()
      self.sortcol(col)
    elif key == 127: # DEL
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        sid = int(self.GetCellValue(row,0))
        book = self.GetCellValue(row,4)
        self.songs[row][1] = -1
        self.setstars(sid, book, filevalue, -1)
    elif key > 47 and key < 52: # 0-3 for number of stars
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        sid = int(self.GetCellValue(row,0))
        book = self.GetCellValue(row,4)
        value = key - 48
        self.songs[row][1] = value
        self.setstars(sid, book, filevalue, value)
    else:
      event.Skip()

  def setstars(self, sid, book, filename, value):
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
    self.db.setSongValue(sid, 0, value)
    self.gridsongs(self.songs)

  def getcurrentsortcol(self):
    return self.currentsortcol
  
  def sizeColumns(self):
    self.AutoSizeColumn(0)
    self.AutoSizeColumn(1)
    self.SetColSize(2, 300)
    self.SetColSize(3, 300)
    self.AutoSizeColumn(4)
    self.SetColSize(5, 300)

  def gridsongs(self, book):
    self.songs = book
    #print(book)
    index = -1
    currentcol = self.GetGridCursorCol()
    currentrow = self.GetGridCursorRow()
    sindex = self.GetCellValue(currentrow, 0)
    if len(sindex) > 0:
      index = int(sindex)
    #print('['+sindex+']', type(sindex), index)
    #index = int(sindex)
    #index = int(self.grid.GetCellValue(currentrow, 0))
    self.ClearGrid()
    row = 0
    currentrow = 0
    if len(book) > self.numrows:
      appendrows = len(book) - self.numrows
      self.grid.AppendRows(appendrows)
      self.numrows = len(book)
    for cr in self.colouredrows: # reset colours
        self.SetCellBackgroundColour(cr,1,wx.Colour(255,255,255))
    self.colouredrows = [] # reset colour list
    for song in book:
      #print(row, index, '=', song[0])
      if index > 0 and index == song[0]:
        #print("index found:", index, song[0])
        currentrow = row
      self.SetCellValue(row, 0, str(song[0]))
      if song[1] == 0:
        self.SetCellValue(row, 1, self.stars[song[1]])
      elif song[1] > 0:
        self.SetCellValue(row, 1, self.stars[song[1]])
        if song[1] == 1:
          self.SetCellBackgroundColour(row,1,wx.YELLOW)
        else:
          self.SetCellBackgroundColour(row,1,wx.GREEN)
        self.colouredrows.append(row)
      else:
        self.SetCellValue(row, 1, "DEL")
        self.SetCellBackgroundColour(row,1,wx.RED)
        self.colouredrows.append(row)
      self.SetCellValue(row, 2, song[2])
      self.SetCellValue(row, 3, song[3])
      self.SetCellValue(row, 4, song[4])
      self.SetCellValue(row, 5, song[5])
      row += 1
    #print("set cursor at start", index, currentrow, currentcol)
    self.SetGridCursor(currentrow,currentcol)
    self.MakeCellVisible(currentrow,currentcol)
    self.SetFocus()
    #wx.CallAfter(self.grid.SetGridCursor, 0, 1)
    
  def on_cell_click(self, event):
    #print("Cell clicked:", event.GetRow(), event.GetCol())
    row = event.GetRow()
    col = event.GetCol()
    bookvalue = self.GetCellValue(row,4)
    filevalue = self.GetCellValue(row,5)
    if len(filevalue) > 0:
      filename = self.db.getsongpath(bookvalue, filevalue)
      if col != 5:
        #print("filename:", filename)
        self.mf.opensong(self.db.readsong(bookvalue, filevalue))
        self.mf.song.display()
      else:
        pos = self.Parent.Parent.GetPosition()
        pos[0] += 100
        pos[1] += 100
        size = self.Parent.Parent.GetSize()
        size[0] -= 200
        size[1] -= 200
        editframe = EditWindow(self, self.db.getsongpath(bookvalue, filevalue), pos, size)
    event.Skip()

  def sortcol(self, col):
    if col != self.currentsortcol:
      self.songs = sorted(self.songs, key=lambda x: x[col])
      self.gridsongs(self.songs)
      self.SetColLabelValue(self.currentsortcol, self.collables[self.currentsortcol])
      self.SetColLabelValue(col, self.colsortlables[col])
      self.currentsortcol = col
    
  def on_label_click(self, event):
    col = event.GetCol()
    self.sortcol(col)
