import wx
import wx.grid
from xsp_editwindow import EditWindow

class SongGrid(wx.grid.Grid):
  def __init__(self, parent, rows, db, mf):
    wx.grid.Grid.__init__(self, parent, size=(1200,600))
    
    self.currentsortcol = -1
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

    for i in range(self.numcols):
      self.SetColLabelValue(i, self.collables[i])

    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key, chr(key))
    if key == 13 and not event.AltDown(): # Enter to show
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        self.mf.opensong(self.db.readsong(self.GetCellValue(row,4), filevalue))
        self.mf.song.display()
    elif key == 96: # ` baclquote for edit
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
    elif key == 44: # , comma for view color (sick)
      if self.mf.song != None:
        color = self.mf.chordcolor
        color += 1
        if color > 3:
          color = 0
        self.mf.chordcolor = color
        self.mf.song.setchordcolor(color)
    elif key == 314 and event.ControlDown(): # ctrl-leftarrow zoom in
      self.mf.OnZoomIn(event)
    elif key == 316 and event.ControlDown(): # ctrl-rightarrow zoom out
      self.mf.OnZoomOut(event)
    elif key == 93: # ] tranpose up
      self.mf.song.transform(1)
    elif key == 91: # [ transpose down
      self.mf.song.transform(-1)
    elif key == 92: # \ save transpose
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        self.db.writesong(self.GetCellValue(row,4), filevalue, self.mf.song.save())
        self.mf.song.display()
    elif key == 317 and event.AltDown(): # alt-downarrow next song
      row = self.GetGridCursorRow()
      if row < len(self.songs)-1:
        row += 1
        filevalue = self.GetCellValue(row,5)
        if len(filevalue) > 0:
          self.mf.opensong(self.db.readsong(self.GetCellValue(row,4), filevalue))
          self.mf.song.display()
          col = self.GetGridCursorCol()
          self.SetGridCursor(row,col)
          self.MakeCellVisible(row,col)
    elif key == 315 and event.AltDown(): # alt-uparrow  previos song
      row = self.GetGridCursorRow()
      if row > 0:
        row -= 1
        filevalue = self.GetCellValue(row,5)
        if len(filevalue) > 0:
          self.mf.opensong(self.db.readsong(self.GetCellValue(row,4), filevalue))
          self.mf.song.display()
          col = self.GetGridCursorCol()
          self.SetGridCursor(row,col)
          self.MakeCellVisible(row,col)
    elif key == 317 and event.ControlDown(): # ctrl-downarrow move down
      self.mf.control.ScrollLines(1)
    elif key == 315 and event.ControlDown(): # ctrl-uparrow  move up
      self.mf.control.ScrollLines(-1)
    elif key == 46: # . period for order
      col = self.GetGridCursorCol()
      self.sortcol(col)
    elif key == 127: # DEL
      self.delrequested()
    elif key > 47 and key < 52 and not event.AltDown(): # 0-3 for number of stars
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,5)
      if len(filevalue) > 0:
        sid = int(self.GetCellValue(row,0))
        book = self.GetCellValue(row,4)
        value = key - 48
        self.songs[row][1] = value
        self.setstars(sid, book, filevalue, value)
    elif key == 60: # < first
      col = self.GetGridCursorCol()
      row =  0
      self.SetGridCursor(row,col)
      self.MakeCellVisible(row,col)
    elif key == 62: # >  last
      col = self.GetGridCursorCol()
      row =  len(self.songs) - 1
      self.SetGridCursor(row,col)
      self.MakeCellVisible(row,col)
    elif key > 64 and key < 91: # A - Z
      col = self.GetGridCursorCol()
      if col > 1 and col < 4:
        if col != self.currentsortcol:
          self.sortcol(col)
        row = self.db.searchset(self.songs, col, chr(key))
        while row < 0 and key > 64:
          key -= 1
          row = self.db.searchset(self.songs, col, chr(key))
        if row >= 0:
          self.SetGridCursor(row,col)
          self.MakeCellVisible(row,col)
        #print("search:", row, chr(key), self.GetColLabelValue(col))
    else:
      event.Skip()

  def delrequested(self):
    row = self.GetGridCursorRow()
    filevalue = self.GetCellValue(row,5)
    if len(filevalue) > 0:
      sid = int(self.GetCellValue(row,0))
      book = self.GetCellValue(row,4)
      self.songs[row][1] = -1
      self.setstars(sid, book, filevalue, -1)
    
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

  def gridclear(self):
    self.ClearGrid()
    for cr in range(len(self.songs)):
        self.SetCellBackgroundColour(cr,1,wx.WHITE)
    
  def gridsongs(self, book=None):
    index = -1
    currentcol = self.GetGridCursorCol()
    currentrow = self.GetGridCursorRow()
    sindex = self.GetCellValue(currentrow, 0)
    if len(sindex) > 0:
      index = int(sindex)
    self.gridclear()
    if book != None:
      self.songs = book
    #print(book)
    #print('['+sindex+']', type(sindex), index)
    #index = int(sindex)
    #index = int(self.grid.GetCellValue(currentrow, 0))
    row = 0
    currentrow = 0
    if len(self.songs) > self.numrows:
      appendrows = len(self.songs) - self.numrows
      self.AppendRows(appendrows)
      self.numrows += appendrows
    for song in self.songs:
      #print(row, index, '=', song[0])
      if index > 0 and index == song[0]:
        #print("index found:", index, song[0])
        currentrow = row
      self.gridrow(row, song)
      row += 1
    #print("set cursor at start", index, currentrow, currentcol)
    self.SetGridCursor(currentrow,currentcol)
    self.MakeCellVisible(currentrow,currentcol)
    self.SetFocus()
    #wx.CallAfter(self.grid.SetGridCursor, 0, 1)

  def gridrow(self, row, song):
    coloured = False
    self.SetCellValue(row, 0, str(song[0]))
    if song[1] == 0:
      self.SetCellValue(row, 1, self.stars[song[1]])
      self.SetCellBackgroundColour(row,1,wx.WHITE)
    elif song[1] > 0:
      self.SetCellValue(row, 1, self.stars[song[1]])
      if song[1] == 1:
        self.SetCellBackgroundColour(row,1,wx.YELLOW)
      else:
        self.SetCellBackgroundColour(row,1,wx.GREEN)
      coloured = True
    else:
      self.SetCellValue(row, 1, "DEL")
      self.SetCellBackgroundColour(row,1,wx.RED)
      coloured = True
    self.SetCellValue(row, 2, song[2])
    self.SetCellValue(row, 3, song[3])
    self.SetCellValue(row, 4, song[4])
    self.SetCellValue(row, 5, song[5])
    
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
      if col > 1:
        self.songs = sorted(self.songs, key=lambda x: x[col].lower())
      else:
        self.songs = sorted(self.songs, key=lambda x: x[col])
      self.gridsongs(self.songs)
      if self.currentsortcol >= 0:
        self.SetColLabelValue(self.currentsortcol, self.collables[self.currentsortcol])
      self.SetColLabelValue(col, self.colsortlables[col])
      self.currentsortcol = col

  def getcurrentsong(self):
    row = self.GetGridCursorRow()
    if row >= 0 and row < len(self.songs):
      return self.songs[row]
    else:
      return None

  def on_label_click(self, event):
    col = event.GetCol()
    self.sortcol(col)
