import wx
import wx.grid
from xsp_editwindow import EditWindow

class SongGrid(wx.grid.Grid):
  def __init__(self, parent, rows, db, mf):
    wx.grid.Grid.__init__(self, parent, size=(1200,600))
    
    self.currentsortcol = -1
    self.stars = [ "☆☆☆☆☆", "★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★" ]
    self.starcolours = [ wx.WHITE, wx.Colour(254,251,1), wx.Colour(206, 251, 2), wx.Colour(135, 250, 0), wx.Colour(58, 249, 1), wx.Colour (0, 255, 0) ]
    self.songs = []
    self.numrows = rows
    self.numcols = 5
    self.db = db
    self.mf = mf
    self.collables = [ "Stars", "Title", "Subtitle", "Book", "File" ]
    self.colsortlables = [ "Stars *", "Title *", "Subtitle *", "Book *", "File *" ]
    self.starscol = 0
    self.titlecol = 1
    self.subtitlecol = 2
    self.filecol = 4
    self.bookcol = 3
    self.rowbuff = 10
    self.pf = self.GetParent().GetParent().GetParent().GetParent()
   
    self.CreateGrid(rows, self.numcols)  # 20 rows, 4 columns
    self.EnableEditing(False)
    self.SetRowLabelSize(0)  # Hide row labels
    self.DisableDragRowSize()

    self.sizeColumns()

    for i in range(self.numcols):
      self.SetColLabelValue(i, self.collables[i])

    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
    self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

  def editsong(self, bookvalue, filevalue):
    pos = self.pf.GetPosition()
    pos[0] += 50
    pos[1] += 50
    size = self.pf.GetSize()
    size[0] -= 250
    size[1] -= 100
    editframe = EditWindow(self, bookvalue, filevalue, pos, size)
    
  def on_key_pressed(self,event):
    key = event.GetKeyCode()
    #print(key, "alt:", event.AltDown())
    if key == 13 and not event.AltDown(): # Enter to show
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,self.filecol)
      if len(filevalue) > 0:
        col = self.GetGridCursorCol()
        bookvalue = self.GetCellValue(row, self.bookcol)
        if col == self.filecol:
          self.editsong(bookvalue, filevalue)
        else:
          try:
            self.mf.opensong(self.db.readsong(bookvalue, filevalue))
            self.mf.song.display()
          except:
            wx.LogError("Cannot open current data in file '%s'." %  self.db.getsongpath(bookvalue, filevalue))
    elif key == 96: # ` backquote for edit
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,self.filecol)
      if len(filevalue) > 0:
        bookvalue = self.GetCellValue(row, self.bookcol)
        self.editsong(bookvalue, filevalue)
    elif key == 61 or (key == 314 and event.ControlDown()): # ctrl-leftarrow zoom in
      self.mf.OnZoomIn(event)
    elif key == 45 or (key == 316 and event.ControlDown()): # ctrl-rightarrow zoom out
      self.mf.OnZoomOut(event)
    elif key == 59: #; print chords
      self.mf.displayUkuleleChords()
      self.ResetFocus()
    elif key == 39: #; print chords
      self.mf.displayGuitarChords()
      self.ResetFocus()
    elif key == 93: # ] tranpose up
      self.mf.song.transform(1)
    elif key == 91: # [ transpose down
      self.mf.song.transform(-1)
    elif key == 92: # \ save transpose
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,self.filecol)
      if len(filevalue) > 0:
        bookvalue = self.GetCellValue(row,self.bookcol)
        self.db.writesong(bookvalue, filevalue, self.mf.song.save())
        self.mf.song.display()
        self.pf.setstatus2(self.db.getsongpath(bookvalue, filevalue) + " saved")
    elif key == 317 and event.AltDown(): # alt-downarrow next song
      self.ChangeSong(1)
    elif key == 315 and event.AltDown(): # alt-uparrow  previos song
      self.ChangeSong(-1)
    elif key == 317 and event.ControlDown(): # ctrl-downarrow move down
      self.mf.control.ScrollLines(1)
    elif key == 315 and event.ControlDown(): # ctrl-uparrow  move up
      self.mf.control.ScrollLines(-1)
    elif key == 60 or (key == 44 and event.ShiftDown()): # < first
      col = self.GetGridCursorCol()
      row =  0
      self.SetGridCursor(row,col)
      self.MakeCellVisible(row,col)
    elif key == 62 or (key == 46 and event.ShiftDown()): # >  last
      col = self.GetGridCursorCol()
      row =  len(self.songs) - 1
      self.SetGridCursor(row,col)
      self.MakeCellVisible(row,col)
    elif key == 44: # , comma for view color (sick)
      if self.mf.song != None:
        color = self.mf.chordcolor
        color += 1
        if color > 3:
          color = -1
        self.mf.chordcolor = color
        self.mf.song.setchordcolor(color)
    elif key == 46: # . period for order
      col = self.GetGridCursorCol()
      self.sortcol(col)
    elif key == 127: # DEL
      self.delrequested()
    elif key > 47 and key < 54 and not event.AltDown(): # 0-5 for number of stars
      row = self.GetGridCursorRow()
      filevalue = self.GetCellValue(row,self.filecol)
      if len(filevalue) > 0:
        sid = self.songs[row][0]
        book = self.songs[row][self.bookcol+1]
        value = key - 48
        self.songs[row][1] = value
        self.setstars(sid, book, filevalue, value)
    elif key > 64 and key < 91: # A - Z
      col = self.GetGridCursorCol()
      if col == self.titlecol or col == self.subtitlecol:
        if col != self.currentsortcol:
          self.sortcol(col)
        row = self.db.searchset(self.songs, col+1, chr(key))
        while row < 0 and key > 64:
          key -= 1
          row = self.db.searchset(self.songs, col+1, chr(key))
        #print("row: ", row, "col:", col)
        if row < 0:
          row = 0
        self.SetGridCursor(row,col)
        self.MakeCellVisible(row,col)
          #print("search:", row, chr(key), self.GetColLabelValue(col))
    elif key == 47: # / slash change focus
      self.ChangeFocus(event)
    else:
      event.Skip()

  def ChangeSong(self, next):
    row = self.GetGridCursorRow()
    row += next
    if row >= 0 and row < len(self.songs):
      filevalue = self.GetCellValue(row,self.filecol)
      if len(filevalue) > 0:
        self.mf.opensong(self.db.readsong(self.GetCellValue(row,self.bookcol), filevalue))
        self.mf.song.display()
        col = self.GetGridCursorCol()
        self.SetGridCursor(row,col)
        self.MakeCellVisible(row,col)
    
  def ResetFocus(self):
    self.SetFocus()
    self.pf.Raise()

  def ChangeFocus(self, event):
    self.pf.vf.control.SetFocus()
    self.pf.vf.Raise()
    
  def delrequested(self):
    row = self.GetGridCursorRow()
    filevalue = self.songs[row][self.filecol+1]
    if len(filevalue) > 0:
      sid = self.songs[row][0]
      book = self.songs[row][self.bookcol+1]
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
    self.SetColSize(0, 70)
    self.SetColSize(1, 300)
    self.SetColSize(2, 300)
    self.SetColSize(3, 100)
    self.SetColSize(4, 300)

  def gridclear(self):
    self.ClearGrid()
    for cr in range(len(self.songs)):
        self.SetCellBackgroundColour(cr,0,wx.WHITE)
    
  def gridsongs(self, book=None, index=-1):
    currentcol = 0
    currentrow = 0
    if index == -1:
      if len(self.songs) > 0:
        currentcol = self.GetGridCursorCol()
        currentrow = self.GetGridCursorRow()
        #print(currentrow)
        if currentrow >= 0 and currentrow < self.numrows and currentrow < len(self.songs):
          index = self.songs[currentrow][0]
    else:
      currentcol = self.filecol # index only set for new song
    self.gridclear()
    if book != None:
      self.songs = book
    row = 0
    currentrow = 0
    #print("resize grid:", len(self.songs), self.numrows)
    if len(self.songs) > self.numrows:
      appendrows = len(self.songs) - self.numrows + self.rowbuff
      #print("appendrows:", appendrows)
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
    #self.SetCellValue(row, 0, str(song[0]))
    if song[1] < 0:
      self.SetCellValue(row, 0, " DEL ")
      self.SetCellBackgroundColour(row,0,wx.RED)
      coloured = True
    elif song[1] >= 0 and song[1] < 6:
      self.SetCellValue(row, 0, self.stars[song[1]])
      self.SetCellBackgroundColour(row,0,self.starcolours[song[1]])
      coloured = True
    else:
      self.SetCellValue(row, 0, "     ")
    self.SetCellValue(row, 1, song[2])
    self.SetCellValue(row, 2, song[3])
    self.SetCellValue(row, 3, song[4])
    self.SetCellValue(row, 4, song[5])
    
  def on_cell_click(self, event):
    #print("Cell clicked:", event.GetRow(), event.GetCol())
    row = event.GetRow()
    filevalue = ""
    if row < len(self.songs):
      filevalue = self.songs[row][self.filecol+1]
    if len(filevalue) > 0:
      col = event.GetCol()
      bookvalue = self.songs[row][self.bookcol+1]
      filename = self.db.getsongpath(bookvalue, filevalue)
      if col != self.filecol:
        try:
          self.mf.opensong(self.db.readsong(bookvalue, filevalue))
          self.mf.song.display()
        except:
          wx.LogError("Cannot open current data in file '%s'." % filename)
      else:
        self.editsong(bookvalue, filevalue)
    event.Skip()

  def sortsongs(self, songs, gridcol):
    col = gridcol + 1  # sid is hidden
    if col > 1:
      return sorted(songs, key=lambda x: x[col].lower())
    else:
      return sorted(songs, key=lambda x: x[col])
    
  def sortcol(self, col):
    if col != self.currentsortcol:
      self.songs = self.sortsongs(self.songs, col)
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
