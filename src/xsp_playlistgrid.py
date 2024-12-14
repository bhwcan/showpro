import wx.grid
from xsp_songgrid import SongGrid

class PlayListGrid(SongGrid):
  def __init__(self, parent, rows, db, mf):
    SongGrid.__init__(self, parent, rows, db, mf)
    self.Bind(wx.EVT_KEY_DOWN, self.on_playlistkey)

  def on_playlistkey(self,event):
    key = event.GetKeyCode()
    if key == 315 and event.ShiftDown(): # shift up
      row = self.GetGridCursorRow()
      col = self.GetGridCursorCol()
      if row > 0:
        tsong = self.songs[row]
        self.songs[row] = self.songs[row-1]
        self.songs[row-1] = tsong
        self.gridrow(row, self.songs[row])
        self.gridrow(row-1, self.songs[row-1])
        self.SetGridCursor(row-1,col)
        if self.currentsortcol >= 0:
          self.SetColLabelValue(self.currentsortcol, self.collables[self.currentsortcol])
          self.currentsortcol = -1
    elif key == 317 and event.ShiftDown(): # shift down
      row = self.GetGridCursorRow()
      col = self.GetGridCursorCol()
      row = self.GetGridCursorRow()
      if row < len(self.songs)-1:
        tsong = self.songs[row]
        self.songs[row] = self.songs[row+1]
        self.songs[row+1] = tsong
        self.gridrow(row, self.songs[row])
        self.gridrow(row+1, self.songs[row+1])
        self.SetGridCursor(row+1,col)
        if self.currentsortcol >= 0:
          self.SetColLabelValue(self.currentsortcol, self.collables[self.currentsortcol])
          self.currentsortcol = -1
    elif key > 64 and key < 91: # A - Z disable for playlist
      pass
    else:
      self.on_key_pressed(event)
    
  def delrequested(self):
    row = self.GetGridCursorRow()
    if row >= 0 and row < len(self.songs):
      del self.songs[row]
      self.DeleteRows(row)
    
  #def row_move(self, event):
  #  print(event.GetRow(),self.GetGridCursorRow())
  #  event.Skip()
              
  #def on_label_click(self, event):
  #  event.Skip()    
