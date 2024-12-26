import os
import json
import string
from pathlib import Path

class Database():
  def __init__(self):
    self.path = None
    self.rebuildrequired = False
    self.songs = []
    self.titleidx = []
    self.booksidx = []
    self.readsize = 120
    self.nonidx = [
      "the",
      "are"
    ]

  def setrootpath(self, newpath=None):
    rvalue = False
    if newpath == None:
      newpath = os.path.join(Path.home(), "Documents", "showpro")
    if os.path.exists(newpath) and os.path.isdir(newpath):
      rvalue = True
    self.path = newpath
    return rvalue

  def getrootpath(self):
    return self.path

  def getplaylistpath(self):
    return(os.path.join(self.path, "playlists"))

  def getsongpath(self, book, songfile):
    return(os.path.join(self.path, book, songfile))

  def deletefile(self, filename):
    os.remove(filename)
    
  def readsong(self, book, songfile):
    filename = self.getsongpath(book, songfile)
    f = open(filename, 'r', encoding="utf-8", errors='ignore')
    data = f.read()
    #print (data)
    f.close()
    return data

  def writesong(self, book, songfile, data):
    filename = self.getsongpath(book, songfile)
    f = open(filename, 'w', encoding="utf-8")
    f.write(data)
    f.close()
    # this should work if the file was found
  
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
        
#  def readsong(self, filename):
#    f = open(filename, 'r', encoding="utf-8", errors='ignore')
#    data = f.read(self.readsize)
#    f.close()
#    return self.gettitles(data)

  def rebuild(self, sw):
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
            data = self.readsong(bookname, rfile)
            (title, subtitle, star) = self.gettitles(data)
            if title != "":
              if sid % 100 == 0 and sw != None:
                #print("titles:", sid, title, subtitle, statusbar)
                text = "Rebuilding indexes: {:05d}".format(sid)
                sw.setstatus(text)
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

  def searchset(self, songset, col, target):
    # obviously assumes sorted set
    first = -1
    last = -1
    found = -1
    low = 0
    high = len(songset) - 1

    while low <= high:
      mid = (low + high) // 2
      first_element = self.searchchar(songset[mid][col])
      if first_element == target:
        found =  mid  # found the target array
        break
      elif first_element < target:
        low = mid + 1
      else:
        high = mid - 1

    if found >= 0:
      first = found
      while self.searchchar(songset[first][col]) == target:
        first -= 1
      first += 1
      
    return first

  def searchchar(self, s):
    if len(s) > 0:
      return(s[0].upper())
    else:
      return chr(ord('A')-1)
  
    
  def searchindex(self, target):
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
      searchsongs = self.searchindex(search)
      if search2 != None and len(search2) > 0:
        search2songs = self.searchindex(search2)
      else:
        search2 = None
    else:
      if search2 != None and len(search2) > 0:
        search = search2
        searchsongs = self.searchindex(search)
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
