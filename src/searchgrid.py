import wx
import wx.grid
import subprocess
import platform
#from xsp_editwindow import EditWindow

class SearchGrid(wx.grid.Grid):
  def __init__(self, parent, rows, db):
    wx.grid.Grid.__init__(self, parent, rows)
    self.parent = parent
    self.currentsortcol = -1
    self.stars = [ "☆☆☆☆☆", "★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★" ]
    self.starcolours = [ wx.WHITE, wx.Colour(254,251,1), wx.Colour(206, 251, 2), wx.Colour(135, 250, 0), wx.Colour(58, 249, 1), wx.Colour (0, 255, 0) ]
    self.songs = []
    self.numrows = rows
    self.numcols = 4
    self.db = db
    self.collables = [ "Stars", "Title", "Subtitle", "Book", "#", "File" ]
    self.colsortlables = [ "Stars *", "Title *", "Subtitle *", "Book *", "# *", "File *" ]
    self.starscol = 0
    self.titlecol = 1
    self.subtitlecol = 2
    self.bookcol = 3
    self.filecol = 5
    self.rowbuff = 10
    self.fontsize = 12
   
    self.CreateGrid(rows, self.numcols)  # 20 rows, 4 columns

    # fonts
    font = self.GetLabelFont()
    font.SetPointSize(self.fontsize)
    self.SetLabelFont(font)
    font.SetWeight(wx.FONTWEIGHT_NORMAL)
    self.SetDefaultCellFont(font)
    self.AutoSizeRows()

    self.EnableEditing(False)
    self.SetRowLabelSize(0)  # Hide row labels
    self.DisableDragRowSize()
    self.SetSelectionMode(wx.grid.Grid.GridSelectRows)

    self.sizeColumns()

    for i in range(self.numcols):
      self.SetColLabelValue(i, self.collables[i])

    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_label_click)
    self.Bind(wx.grid.EVT_GRID_RANGE_SELECTING, self.on_range_select)

  def on_range_select(self, event):
    #return
    top_row = event.GetTopRow()
    #  bottom_row = event.GetBottomRow()
    left_col = event.GetLeftCol()
    #  right_col = event.GetRightCol()
    #  num_songs = len(self.songs)

    #  print(f"Selected range: Rows {top_row}-{bottom_row}, Cols {left_col}-{right_col}, Songs {num_songs}, Rows {self.numrows}")
    #  if event.Selecting():
    #    print("Selection is in progress.")
        #self.GoToCell(top_row, left_col)
    self.SelectRow(top_row, False)
        #event.Skip()
    #  else:
    #    print("Selection is complete.")
        #event.Skip()

      # Optional: Get the actual cell values in the range
      #for row in range(top_row, bottom_row + 1):
      #    for col in range(left_col, right_col + 1):
      #        value = self.grid.GetCellValue(row, col)
      #        print(f"Cell ({row},{col}): {value}")
      #event.Skip()
    #  self.ClearSelection()

  def getcurrentsortcol(self):
    return self.currentsortcol
  
  def sizeColumns(self):
    self.SetColSize(0, 70)
    self.SetColSize(1, 300)
    self.SetColSize(2, 400)
    self.SetColSize(3, 100)

  def gridclear(self):
    self.ClearSelection()
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
    #print(song)
    #self.SetCellValue(row, 0, str(song[0]))
    self.SetCellTextColour(row, 0, wx.BLACK)
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
    if song[5] < 0:
      number = ""
    else:
      number = str(song[5]).rjust(6)
    self.SetCellValue(row, 1, song[2])
    self.SetCellValue(row, 2, song[3])
    self.SetCellValue(row, 3, song[4])
    
  def on_cell_click(self, event):
    #print("Cell clicked:", event.GetRow(), event.GetCol())
    row = event.GetRow()
    col = event.GetCol()
    filevalue = ""
    if row < len(self.songs):
      filevalue = self.songs[row][self.filecol+1]
    if len(filevalue) > 0:
      bookvalue = self.songs[row][self.bookcol+1]
      filename = self.db.getsongpath(bookvalue, filevalue)
      self.parent.parent.parent.opensong(filename)
      self.parent.parent.parent.song.display()
    #self.ClearSelection()
    self.GoToCell(row, col)
    self.SelectRow(row, False)

  def sortsongs(self, songs, gridcol):
    #print("sortsongs", gridcol)
    if gridcol < 0:
      return songs
    col = gridcol + 1  # sid is hidden
    if col != 1:
      return sorted(songs, key=lambda x: x[col].lower())
    else:
      return sorted(songs, key=lambda x: x[col])
    
  def sortcol(self, col):
    #print("sortcol:", col)
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
    self.ClearSelection()
    col = event.GetCol()
    self.sortcol(col)
