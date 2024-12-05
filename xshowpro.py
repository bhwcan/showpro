#
# showpro.py - show and database app for laptop connected to big screen
#(c) Byron Walton, bhwcan@netscape.net
#
import wx
import wx.grid
import os
import sys
import json
import subprocess
import string
import webbrowser
from pathlib import Path

class Directive:
  def __init__(self, raw, pos):
    self.line = raw
    self.y = pos
    self.x = 0
    self.name = ""
    self.text = ""

  def process(self):
    if self.line.find("#") == 0:
      self.name = self.line[0:1]
      self.text = self.line[1:]
      return self.name, self.text
    self.x = self.line.find("{")
    colon = self.line.find(":")
    end = self.line.find("}")
    if end < 0:
      end = len(self.line)
    if colon > 0:
      self.name = self.line[self.x+1:colon].strip().lower()
      self.text = self.line[colon+1:end]
    else:
      self.name = self.line[self.x+1:end].strip().lower()
    return self.name, self.text    
  
class Song:
  def __init__(self, parent, textsize, chordcolor, raw):
    self.mx = parent
    self.data = raw
    self.lines = []
    self.lyrics = []
    self.directives = []
    self.title = ""
    self.subtitle = ""
    self.width = 0
    self.textsize = textsize
    self.chordcolor = chordcolor
    self.tab = "    "
    self.scalelookup = [ \
                         { "chord": "A#", "index": 2 }, 
                         { "chord": "Bb", "index": 2 }, 
                         { "chord": "C#", "index": 5 },
                         { "chord": "Db", "index": 5 },
                         { "chord": "D#", "index": 7 }, 
                         { "chord": "Eb", "index": 7 }, 
                         { "chord": "F#", "index": 10 }, 
                         { "chord": "Gb", "index": 10 }, 
                         { "chord": "G#", "index": 12 }, 
                         { "chord": "Ab", "index": 12 }, 
                         { "chord": "A", "index": 1 }, 
                         { "chord": "B", "index": 3 }, 
                         { "chord": "C", "index": 4 }, 
                         { "chord": "D", "index": 6 }, 
                         { "chord": "E", "index": 8 }, 
                         { "chord": "F", "index": 9 }, 
                         { "chord": "G", "index": 11 } ]
    self.scale = [ "NC", "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "F#", "G", "G#" ]  

  def transform(self, value):
    newlyrics = []
    for lyric in self.lyrics:
      newlyric = ""
      s = 0
      while True:
        cs = lyric.find('[',s)
        if cs < 0:
          newlyric += lyric[s:]
          break
        else:
          ce = lyric.find(']',s)
          if ce < 0:
            newlyric += lyric[s:]
            break
          newlyric += lyric[s:cs+1] # include brace
          oldchord = lyric[cs+1:ce]
          oldfound = False
          newchord = ""
          for look in self.scalelookup:
            if oldchord.find(look["chord"]) == 0:
              oldfound = True
              oldlen = len(look["chord"])
              oldidx = look["index"]
              newidx = oldidx + value
              if newidx < 1:
                newidx = 12
              if newidx > 12:
                newidx = 1
              newchord = self.scale[newidx] + oldchord[oldlen:]
              break
          if oldfound:
            newlyric += newchord
          else:
            newlyric += oldchord
          newlyric += "]" # add back the brace
          s = ce + 1
          if s >= len(lyric):
            break
      newlyrics.append(newlyric)
    self.lyrics = newlyrics
    self.display()

  def save(self): # rebuild the original with new lyrics
    output = ""
    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      output += self.directives[cd].line
      cd += 1
    l = 0
    for lyric in self.lyrics:
      if cd < len(self.directives):
        while self.directives[cd].y == l:
          output += self.directives[cd].line
          cd += 1
      output += lyric
      l += 1
    while cd < len(self.directives):
      output += self.directives[cd].line
      cd += 1
    return(output)
    
  def command(self, line, lineno):
    dtive = Directive(line, lineno)
    name, text = dtive.process()
    if name == "t" or name == "title":
      self.title = text
    if name == "st" or name == "subtitle":
      self.subtitle = text
    self.directives.append(dtive)
    
  def process(self):
    rvalue = True
    lineno = 0 # before lyrics
    self.lines = self.data.splitlines(True)
    for line in self.lines:
      #print(line)
      if line.find("#") == 0 or line.find("{") >= 0:
        self.command(line, lineno)
      else:
        lineno += 1
        if len(line) > self.width:
          self.width = len(line)
        line = line.replace("", "↓")  # down arrows
        line = line.replace("’", "\'") # fancy quotes
        self.lyrics.append(line)
      if lineno > 10 and self.title == "":
        self.lyrics = []
        rvalue = False
        break
    #print("process:", rvalue)
    return rvalue

  def zoom(self, value):
    self.textsize += value
    if self.textsize < 16:
      self.textsize = 16
    if self.textsize > 52:
      self.textsize = 52
    #print (self.textsize)
    self.display()
    return self.textsize    

  def setchordcolor(self, value):
    self.chordcolor = value
    self.display()

  def display(self):
    face = "Monospace"
    if wx.Platform == "__WXMSW__":
      face = "Lucida Console"
    if wx.Platform == "__WXMAC__":
      face = "Menlo"
    choruson = False
    cordattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    if self.chordcolor == 1:
      cordattr = wx.TextAttr(wx.Colour(120,0,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 2:
      cordattr = wx.TextAttr(wx.Colour(0,0,180), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    elif self.chordcolor == 3:
      cordattr = wx.TextAttr(wx.Colour(0,100,0), font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT,  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    boldattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, face))
    fontattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face))
    itlcattr = wx.TextAttr(wx.BLACK, font=wx.Font(self.textsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_NORMAL, False, face))
    
    cd = 0
    while cd < len(self.directives) and self.directives[cd].y <= 0:
      cd += 1
    rtc = self.mx.control
    #if wx.Platform == "__WXMSW__":
    rtc.Hide()
    rtc.Clear()
    rtc.SetDefaultStyle(boldattr)
    rtc.WriteText(self.title.center(self.width) + "\n" + self.subtitle.center(self.width) + "\n")
    rtc.SetDefaultStyle(fontattr)
    self.mx.SetTitle(self.title + " - " + self.subtitle);
    l = 0
    for lyric in self.lyrics:
      #print(l,";",lyric[:-1])
      #print("cd < len:", cd, len(self.directives))
      while cd < len(self.directives) and self.directives[cd].y == l:
        #print("y == l:", cd, self.directives[cd].y, l)
        d = self.directives[cd]
        if d.name == "start_of_chorus" or d.name == "soc":
          #print("start_of_chorus");
          choruson = True
        if d.name == "end_of_chorus" or d.name == "eoc":
          choruson = False
          #print("end_of_chorus");
        if d.name == "comment" or d.name == "c" or\
           d.name == "comment_italic" or d.name == "ci":
          #print("comment:", d.text)
          rtc.SetDefaultStyle(itlcattr)
          rtc.WriteText(self.tab + d.text + "\n")
          rtc.SetDefaultStyle(fontattr)
        cd += 1
      s = 0
      rtc.WriteText(self.tab) # normal tab
      if choruson:
        rtc.WriteText(self.tab) # chorus tab
      while True:
        cs = lyric.find('[',s)
        if cs < 0:
          rtc.WriteText(lyric[s:])
          break
        else:
          ce = lyric.find(']',s)
          if ce < 0:
            rtc.WriteText(lyric[s:])
            break
          rtc.WriteText(lyric[s:cs])
          rtc.SetDefaultStyle(cordattr)
          rtc.WriteText(lyric[cs:ce+1])
          rtc.SetDefaultStyle(fontattr)
          s = ce + 1
          if s >= len(lyric):
            break
      l += 1
    #if wx.Platform == "__WXMSW__":
    rtc.SetInsertionPoint(0) # PC hac
    rtc.Show()

class Database():
  def __init__(self, songpath):
    self.path = songpath
    self.songs = []
    self.titleidx = []
    self.booksidx = []
    self.readsize = 120
    self.nonidx = [
      "the",
      "are"
    ]

  def getpath(self):
    return self.path
  
  def open(self):
    rvalue = True
    songfile = os.path.join(self.path, "songs.dat")
    if os.path.exists(songfile):
      with open(songfile, "r") as sf:
        self.songs = json.load(sf)
      with open(os.path.join(self.path, "songsidx.dat"), "r") as sf:
        self.titleidx = json.load(sf)
      with open(os.path.join(self.path, "booksidx.dat"), "r") as sf:
        self.booksidx = json.load(sf)
    else:
      self.rebuild(None)
    return rvalue

  def gettitles(self, data):
    first = True
    star = 0
    title = ""
    subtitle = ""
    for line in data.splitlines():
      if first:
        if line.find("#showpro:") == 0:
          try:
            star = int(line[9:])
          except:
            star = 0
        if star < -1:
          star = -1
        if star > 3:
          star = 3
      #print(line)
      start = line.find("{")
      if start >= 0:
        colon = line.find(":")
        if colon >= 0:
          end = line.find("}")
          if end >= 0:
            name = line[start+1:colon].strip().lower()
            if name == "t" or name == "title":
              title = line[colon+1:end].strip()
            if name == "st" or name == "subtitle":
              subtitle = line[colon+1:end].strip()
    return(title, subtitle, star)

  def idxtitle(self, sid, title):
    titles = set(title.lower().split())
    for tword in titles:
      if tword[-1] in string.punctuation:
        tword = tword[0:-1]
      if len(tword) > 0 and tword[0] in string.punctuation:
        tword = tword[1:]
      if len(tword) > 2 and tword not in self.nonidx: #exclude words 2 characters or less
        self.titleidx.append([tword, sid])
        
  def readsong(self, filename):
    f = open(filename, 'r', encoding="utf-8", errors='ignore')
    data = f.read(self.readsize)
    f.close()
    return self.gettitles(data)

  def rebuild(self, statusbar):
    #print("db.rebuild")
    bookno = 0
    booknames = None
    bookend = 0
    first = True

    self.songs = []
    self.titleidx = []
    self.booksidx = []

    sid = 0
    # search files
    for (dirpath, dirnames, filenames) in os.walk(self.path):
      if dirpath[len(self.path):].count(os.sep) < 2: # max depth
        if first:
          booknames = dirnames
          first = False
          continue
        bookstart = sid
        #print("bookno:", bookno, dirpath)
        #if bookno >= len(booknames):
        #  print("bookno:", bookno, dirpath, dirnames, filenames)
        bookname = booknames[bookno]
        for rfile in filenames:
          if rfile[-3:] == "pro":
            profile = os.path.join(dirpath, rfile)
            (title, subtitle, star) = self.readsong(profile)
            if title != "":
              #print("titles:", sid, title, subtitle)
              if statusbar != None:
                statusbar.SetStatusText("Rebuilding indexes: {:05d}".format(sid), 0)
              self.songs.append([ star, title, subtitle, booknames[bookno], rfile ])
              self.idxtitle(sid, title)
              self.idxtitle(sid, subtitle)
              sid += 1
        bookend = sid
        #print("book:", bookno, bookname, bookstart, bookend)
        if bookend != bookstart: # no files found so no book
          self.booksidx.append([ bookname, bookstart, bookend ])
        bookno += 1
      
    self.booksidx.append([ "All", 0, bookend ])
    with open(os.path.join(self.path, "songs.dat"), "w") as fh:
      json.dump(self.songs, fh)
    self.booksidx = sorted(self.booksidx, key=lambda x: x[0])
    with open(os.path.join(self.path, "booksidx.dat"), "w") as fh:
      json.dump(self.booksidx, fh)
    self.titleidx = sorted(self.titleidx, key=lambda x: x[0])
    with open(os.path.join(self.path, "songsidx.dat"), "w") as fh:
      json.dump(self.titleidx, fh)

  def binary_search_array_of_arrays(self, target):
    arrays = self.titleidx
    songlist = []
    first = -1
    last = -1
    found = -1
    low = 0
    high = len(arrays) - 1

    while low <= high:
      mid = (low + high) // 2
      first_element = arrays[mid][0]
      if first_element == target:
        found =  mid  # found the target array
        break
      elif first_element < target:
        low = mid + 1
      else:
        high = mid - 1

    if found > 0:
      first = found
      while arrays[first][0] == target:
        first -= 1
      first += 1
      last = found
      while arrays[last][0] == target:
        last += 1

    for i in range(first, last):
      songlist.append(arrays[i][1])
  
    return set(songlist)

#  return first, last  # not found
  def search(self, search, operator, search2):
    resultset = []
    if search != None and len(search) > 0:
      searchsongs = self.binary_search_array_of_arrays(search)
      if search2 != None and len(search2) > 0:
        search2songs = self.binary_search_array_of_arrays(search2)
      else:
        search2 = None
    else:
      if search2 != None and len(search2) > 0:
        search = search2
        searchsongs = self.binary_search_array_of_arrays(search)
        search2 = None
      else:
        return resultset # no data to search
        
    found = False
    songset = None
    if search2 != None:
      if operator == "Or":
        songset = searchsongs.union(search2songs)
      elif operator == "Not":
        songset = searchsongs.difference(search2songs)
      elif operator == "And":
        songset = searchsongs.intersection(search2songs)
      else:
        songset = search2songs
    else:
      songset = searchsongs

    #print(len(songset), "songs found")

    for sx in songset:
      resultset.append([sx, self.songs[sx][0], self.songs[sx][1], self.songs[sx][2], self.songs[sx][3], self.songs[sx][4]])
    return resultset

  def getBooks(self):
    return self.booksidx

  def getSongs(self, bookname):
    # deepcopy plus id
    for book in self.booksidx:
      if bookname == book[0]:
        idstart = book[1]
        idend = book[2]
    idsongs = []
    sid = 0
    for song in self.songs:
      if sid >= idstart and sid < idend:
        idsongs.append([sid, song[0], song[1], song[2], song[3], song[4]])
      sid += 1
    return idsongs

  def setSongValue(self, sid, field, value):
    #print(self.songs[sid])
    self.songs[sid][field] = value
    #print(self.songs[sid])
    #exit(10)
    with open(os.path.join(self.path, "songs.dat"), "w") as fh:
      json.dump(self.songs, fh)
  
class SongPanel(wx.Panel):
  def __init__(self, parent, mainframe, songpath, display):
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
    
    self.db = Database(songpath)
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
    self.searchtxt2 = wx.TextCtrl(self)
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

    self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_cell_click)
    self.searchbutton.Bind(wx.EVT_BUTTON, self.on_button_click)
    self.searchtxt1.Bind(wx.EVT_TEXT_ENTER, self.on_button_click)
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
    self.db.rebuild(self.Parent.statusbar)
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
        filename = os.path.join(self.db.getpath(), self.grid.GetCellValue(row,4), filevalue)
        self.mf.opensong(filename)
        self.mf.song.display()
    elif key == 127: # DEL
      row = self.grid.GetGridCursorRow()
      filename = os.path.join(self.db.getpath(), self.grid.GetCellValue(row,4), self.grid.GetCellValue(row,5))
      sidstr = self.grid.GetCellValue(row,0)
      self.setstars(sidstr, filename, -1)
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
      filename = os.path.join(self.db.getpath(), self.grid.GetCellValue(row,4), self.grid.GetCellValue(row,5))
      sidstr = self.grid.GetCellValue(row,0)
      value = key - 48
      self.setstars(sidstr, filename, value)
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

  def setstars(self, sidstr, filename, value):
    if os.path.isfile(filename):
      f = open(filename, 'r', encoding="utf-8", errors='ignore')
      data = f.read()
      #print (data)
      f.close()
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
      f = open(filename, 'w', encoding="utf-8")
      f.write(data)
      f.close()
      # this should work if the file was found
      sid = int(sidstr)
      self.db.setSongValue(sid, 0, value)
      if self.insearch:
        self.searchlist = self.db.search(self.search, self.operator, self.search2)
        self.gridbook(self.searchlist)
      else:
        self.books[self.currentbook] = self.db.getSongs(self.currentbook)
        self.gridbook(self.books[self.currentbook])

  def loadbook(self):
    if self.currentbook not in self.books:
      self.books[self.currentbook] = self.db.getSongs(self.currentbook)
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
    self.Parent.statusbar.SetStatusText(str(row) + songtxt, 0)
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
    self.insearch = True
    self.gridbook(self.searchlist)
    
  def on_cell_click(self, event):
    #print("Cell clicked:", event.GetRow(), event.GetCol())
    row = event.GetRow()
    col = event.GetCol()
    filevalue = self.grid.GetCellValue(row,5)
    if len(filevalue) > 0:
      filename = os.path.join(self.db.getpath(), self.grid.GetCellValue(row,4), filevalue)
      if col != 5:
        #print("filename:", filename)
        self.mf.opensong(filename)
        self.mf.song.display()
      else:
        editframe = EditWindow(self.mf, filename, self.display)
        #subprocess.Popen(["emacs", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
      event.Skip()
    
class SongWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1200,780))
    self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
    self.statusbar.SetFieldsCount(2, [-1, -4])
    self.resetstatus()
    #self.statusbar.SetStatusText("no status")
    self.Show()

  def resetstatus(self):
    self.statusbar.SetStatusText(
      "Keys: [Enter] view [e] edit [b] book, [s] search [c] clear"\
      " [o] order column [q] quit [0-3] stars [DEL] red [z-x] zoom [t-y-u] transpose [v] color"\
      " [m-k] scoll",1)

class EditWindow(wx.Frame):
  def __init__(self, parent, filename, display):
    self.filename = filename

    wx.Frame.__init__(self, parent, title=filename, pos=(display[0]+200, display[1]+100), size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    font=wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    self.control.SetFont(font)
    self.control.LoadFile(filename)

    # Setting up the menu.
    filemenu= wx.Menu()
    menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save file")
    menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the window")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
    self.Bind(wx.EVT_MENU, self.OnSave, menuSave)

    self.Show()

  def OnSave(self,e):
    if self.control.IsModified:
      self.control.SaveFile(self.filename)

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

class MainWindow(wx.Frame):
  def __init__(self, parent):
    self.dirname=""
    self.filename=""
    self.song = None
    self.textsize = 20
    self.chordcolor = 0
    self.row = 0

    wx.Frame.__init__(self, parent, size=(1200,800), style=wx.DEFAULT_FRAME_STYLE &~ wx.CLOSE_BOX) #wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION)
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL)
    #self.CreateStatusBar() # A Statusbar in the bottom of the window
    # self.control.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)

    # Setting up the menu.
    filemenu= wx.Menu()
    #menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to view")
    menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")

    zoommenu = wx.Menu()
    menuZoomIn = zoommenu.Append(wx.ID_ZOOM_IN, "Zoom &In", "Zoom in text size")
    menuZoomOut = zoommenu.Append(wx.ID_ZOOM_OUT, "Zoom &Out", "Zoom out text size")
    
    # Setting up the menu.
    chordmenu= wx.Menu()
    chordBold = chordmenu.Append(1001, "&Bold","Set chords to bold")
    chordRed = chordmenu.Append(1002, "&Red", "Set chord to red")
    chordBlue = chordmenu.Append(1003, "&Blue", "Set chords to blue")
    chordGreen= chordmenu.Append(1004, "&Green","Set chords to green")

    # Setting up the menu.
    transmenu= wx.Menu()
    transplus = transmenu.Append(2005, "Up &+","Transpose up one step")
    transminus = transmenu.Append(2006, "Down &-", "Transpose down one step")
    transave = transmenu.Append(wx.ID_SAVE, "&Save", "Save transformation to chordpro file")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    menuBar.Append(zoommenu,"&Zoom") # Adding the "filemenu" to the MenuBar
    menuBar.Append(chordmenu,"&Color") # Adding the "filemenu" to the MenuBar
    menuBar.Append(transmenu,"&Transpose") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    # Events.
    #self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_MENU, self.OnZoomIn, menuZoomIn)
    self.Bind(wx.EVT_MENU, self.OnZoomOut, menuZoomOut)
    self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    self.Bind(wx.EVT_MENU, self.OnBold, chordBold)
    self.Bind(wx.EVT_MENU, self.OnRed, chordRed)
    self.Bind(wx.EVT_MENU, self.OnBlue, chordBlue)
    self.Bind(wx.EVT_MENU, self.OnGreen, chordGreen)
    self.Bind(wx.EVT_MENU, self.OnPlus, transplus)
    self.Bind(wx.EVT_MENU, self.OnMinus, transminus)
    self.Bind(wx.EVT_MENU, self.OnSave, transave)
    self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)

    self.Raise()
    self.Show()

  # def on_key_pressed(self, event):
  #   delay = 0
  #   jump = 5
  #   steps = 10
  #   key = event.GetKeyCode()
  #   print(key)
  #   if key == 315:
  #     y = self.control.G
  #     self.control.ScrollLines(-jump)
  #     #for step in range(0,steps):
  #     #  prow = self.control.GetScrollPos(wx.VERTICAL)
  #     #  prow -= jump
  #     #  self.control.SetScrollPos(wx.VERTICAL, prow)
  #     #  time.sleep(delay)
  #   elif key == 317:
  #     self.control.ScrollLines(jump)
  #     #for step in range(0,steps):
  #     #  prow = self.control.GetScrollPos(wx.VERTICAL)
  #     #  prow += jump
  #     #  self.control.SetScrollPos(wx.VERTICAL, prow)
    
  def OnTextURL(self, event):
    #print('OnTextURL')
    if event.MouseEvent.LeftUp():
        #print(event.GetURLStart(), event.GetURLEnd())
        url = self.control.GetRange(event.GetURLStart(), event.GetURLEnd())
        #print(url)
        webbrowser.open_new_tab(url)
    event.Skip()

  def OnPlus(self,e):
    if self.song != None:
      self.song.transform(1)

  def OnMinus(self,e):
    if self.song != None:
      self.song.transform(-1)

  def OnSave(self,e):
    if self.song != None:
      output = self.song.save()
      f = open(self.filename, 'w')
      f.write(output)
      f.close()
    
  def OnBold(self,e):
    self.chordcolor = 0
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnRed(self,e):
    self.chordcolor = 1
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnBlue(self,e):
    self.chordcolor = 2
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnGreen(self,e):
    self.chordcolor = 3
    if self.song != None:
      self.song.setchordcolor(self.chordcolor)

  def OnZoomIn(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(4)

  def OnZoomOut(self,e):
    if self.song != None:
      self.textsize = self.song.zoom(-4)
      
  def OnAbout(self,e):
    # Create a message dialog box
    dlg = wx.MessageDialog(self,
                           " A simple chordpro viewer and database\n"\
                           " for large dislplay monitors \n\n"\
                           "    by Byron Walton\n"\
                           "    bhwcan@netscape.net",
                           "About XShowPro", wx.OK)
    dlg.ShowModal() # Shows it
    dlg.Destroy() # finally destroy it when finished.

  def OnExit(self,e):
    self.Close(True)  # Close the frame.

  def opensong(self, filename):
    #print("mainwindow opensong:", filename)
    self.filename = filename
    rvalue = True
    if os.path.isfile(filename):
      f = open(filename, 'r', encoding="utf-8", errors='ignore')
      data = f.read()
      #print (data)
      f.close()
      self.song = Song(self, self.textsize, self.chordcolor, data)
      rvalue = self.song.process()
    else:
      rvalue = False
    if not rvalue:
      dlg = wx.MessageDialog(self,
                             " File: " + self.filename + "\n",
                             "Invalid file", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal() # Shows it
      dlg.Destroy() # finally destroy it when finished.
    return rvalue

#  def OnOpen(self,e):
#    """ Open a file"""
#    dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*pro", wx.FD_OPEN)
#    if dlg.ShowModal() == wx.ID_OK:
#      self.filename = dlg.GetFilename()
#      self.dirname = dlg.GetDirectory()
#    dlg.Destroy()
#    filename = os.path.join(self.dirname, self.filename)
#    if not self.opensong(filename):
#      self.song.display()
#      self.song = None
#    else:
#      self.song.display()

#MAIN
#print("platform:", wx.Platform)
home = Path.home()
songpath = os.path.join(home, "Documents", "showpro")

app = wx.App(False)
if  not os.path.exists(songpath):
  dlg = wx.MessageDialog(None,
                         " Invalid Path: " + songpath + "\n",
                         "Please create showpro song database\n"\
                         "ask Byron", wx.OK|wx.ICON_ERROR)
  dlg.ShowModal() # Shows it
  dlg.Destroy() # finally destroy it when finished.
  exit(10)

# figure out the displays for windows - should be a class
displays = []
widevalue = 0
wideidx = 0
appidx = 0
dcount = wx.Display.GetCount()
#dcount = 1
for dc in range(dcount):
  d = wx.Display(dc)
  geo = d.GetGeometry()
  if geo[2] > widevalue:
    widevalue = geo[2]
    wideidx = dc
  #print(geo)
  displays.append(geo)
#debug
if dcount > 1:
  for dc in range(dcount):
    if dc != wideidx:
      appidx = dc
      break
else:
  half = int(displays[0][2]/2)
  displays[0][2] = half
  displays.append(wx.Rect([half, displays[0][1], half, displays[0][3]]))
  appidx = 1

#print (displays)
#print ("wide:", wideidx, displays[wideidx][2], "app:", appidx, displays[appidx][2])
#exit(10)

# open the windows
songframe = SongWindow(None, "Showpro Songs")
mainframe = MainWindow(songframe)
mainframe.SetPosition(wx.Point(displays[wideidx][0], displays[wideidx][1]+30))
mainframe.SetSize(wx.Size(displays[wideidx][2],displays[wideidx][3]-30))
songframe.SetPosition(wx.Point(displays[appidx][0], displays[appidx][1]+30))
panel = SongPanel(songframe, mainframe, songpath, displays[appidx])
songframe.Show()
app.MainLoop()
