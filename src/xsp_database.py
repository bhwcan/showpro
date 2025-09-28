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
    self.chorddefs = []
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
      else:
        try:
          os.mkdir(newpath)
          rvalue = True
        except:
          pass
    self.path = newpath
    return rvalue

  def getrootpath(self):
    return self.path

  def getplaylistpath(self):
    return(os.path.join(self.path, "playlists"))

  def getsongpath(self, book, songfile):
    return(os.path.join(self.path, book, songfile))

  def deletesongs(self):
    for song in self.songs:
      if song[0] == -1:  # stars -1 is deleted
        self.deletefile(self.getsongpath(song[3], song[5]))

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
    songidxfile = os.path.join(self.path, "songsidx.dat")
    bookidxfile = os.path.join(self.path, "booksidx.dat")
    if  os.path.exists(songfile) and \
        os.path.exists(songidxfile) and \
        os.path.exists(bookidxfile): 
      with open(songfile, "r") as sf:
        self.songs = json.load(sf)
        #print(self.songs[0])
      with open(songidxfile, "r") as sf:
        self.titleidx = json.load(sf)
      with open(bookidxfile, "r") as sf:
        self.booksidx = json.load(sf)
    else:
      rvalue = False
    if os.path.exists(os.path.join(self.path, "chords.jsn")):
      with open(os.path.join(self.path, "chords.jsn"), "r") as cf:
        self.chorddefs = json.load(cf)
    return rvalue
  
  def find_ukuleledef(self, name):
    rvalue = None
    if "U0" in self.chorddefs:
      for d in self.chorddefs["U0"]["chords"]:
        if d["name"] == name:
          rvalue = d
          break
    return rvalue

  def find_guitardef(self, name):
    rvalue = None
    if "G0" in self.chorddefs:
      for d in self.chorddefs["G0"]["chords"]:
        if d["name"] == name:
          rvalue = d
          break
    return rvalue

  def gettitles(self, data):
    first = True
    star = 0
    title = ""
    subtitle = ""
    number = -1
    for line in data.splitlines():
      if first:
        if line.find("#showpro:") == 0:
          try:
            star = int(line[9:])
          except:
            star = 0
        if star < -1:
          star = -1
        if star > 5:
          star = 5
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
            if name == "number":
              try:
                number = int(line[colon+1:end].strip())
              except:
                number = -1
    return(title, subtitle, star, number)

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
    self.numberidx = []

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
        if bookname == "All": # reserved name for all books so skip directory
          bookno += 1
          continue
        for rfile in filenames:
          if rfile[-3:] == "pro" or rfile[-3:] == "cho":
            data = self.readsong(bookname, rfile)
            (title, subtitle, star, number) = self.gettitles(data)
            if title != "":
              if sid % 100 == 0 and sw != None:
                #print("titles:", sid, title, subtitle, statusbar)
                text = "Rebuilding indexes: {:05d}".format(sid)
                sw.setstatus(text)
              if number >= 0:
                self.numberidx.append([number, sid])
              self.songs.append([ star, title, subtitle, booknames[bookno], number, rfile ])
              self.idxtitle(sid, title)
              self.idxtitle(sid, subtitle)
              sid += 1
        bookend = sid
        #print("book:", bookno, bookname, bookstart, bookend)
        if bookend != bookstart: # no files found so no book
          self.booksidx.append([ bookname, bookstart, bookend ])
        bookno += 1
      
    #self.booksidx = sorted(self.booksidx, key=lambda x: x[1])
    self.booksidx.append([ "All", 0, bookend ])
    with open(os.path.join(self.path, "songs.dat"), "w") as fh:
      json.dump(self.songs, fh)
    with open(os.path.join(self.path, "booksidx.dat"), "w") as fh:
      json.dump(self.booksidx, fh)
    self.titleidx = sorted(self.titleidx, key=lambda x: x[0])
    with open(os.path.join(self.path, "songsidx.dat"), "w") as fh:
      json.dump(self.titleidx, fh)
    self.numberidx = sorted(self.numberidx, key=lambda x: x[0])
    with open(os.path.join(self.path, "numberidx.dat"), "w") as fh:
      json.dump(self.numberidx, fh)
    if os.path.exists(os.path.join(self.path, "chords.dat")):
      with open(os.path.join(self.path, "chords.dat"), "r") as cf:
        self.chorddefs = json.load(cf)

    #playlists
    plpath = self.getplaylistpath()
    if not os.path.isdir(plpath):
      try:
        os.mkdir(plpath)
      except:
        pass    
    

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
      while first >= 0 and self.searchchar(songset[first][col]) == target:
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

    if found >= 0:
      first = found
      while first >= 0 and arrays[first][0] == target:
        first -= 1
      first += 1
      last = found
      while last < len(arrays) and arrays[last][0] == target:
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
      resultset.append([sx, self.songs[sx][0], self.songs[sx][1], self.songs[sx][2], self.songs[sx][3], self.songs[sx][4], self.songs[sx][5]])
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
        idsongs.append([sid, song[0], song[1], song[2], song[3], song[4], song[5]])
      sid += 1
    return idsongs

  def newsong(self, book, title, subtitle):
    rvalue = -1
    bookid = -1
    idx = 0
    for be in self.booksidx:
      #print("\tbe:", idx, be[0], be[1])
      if book == be[0]:
        bookid = idx
        break
      idx += 1
    if bookid >= 0:
      #print("\tbook found")
      booklast = self.booksidx[bookid][2]
    else:
      #print("\tbook NOT found")
      booklast = self.booksidx[-1][2]
      #print("\tnewbook: ", book, self.booksidx[-1][0])
      dirpath = os.path.join(self.path, book)
      if os.path.exists(dirpath):
        if not os.path.isdir(dirpath):
          rvalue = -2
          return rvalue
      else:
        try:
          os.mkdir(dirpath)
        except:
          return rvalue    
    #print("\tbooklast:", booklast, len(self.songs))
    titleline = "#showpro: 0\n"
    if not subtitle:
      titleline += "{{t:{title}}}\n".format(title=title)
      filename = "{title}.pro".\
        format(title=title.replace("/"," ").replace("-","_"))
    else:
      titleline += "{{t:{title}}}\n{{st:{subtitle}}}\n".format(title=title,subtitle=subtitle)
      filename = "{title} - {subtitle}.pro".\
        format(title=title.replace("/"," ").replace("-","_"),
               subtitle=subtitle.replace("/"," ").replace("-","_"))

    self.writesong(book, filename, titleline)

    newsong = [ 0, title, subtitle, book, -1, filename ]

    if bookid < 0:
      bookid = len(self.booksidx)-1
      self.booksidx.insert(bookid, [book, booklast, booklast+1])
      self.booksidx[-1][2] += 1
      self.songs.append(newsong)
    else:
      self.songs.insert(booklast, newsong)      # insert new song at end of book
      self.booksidx[bookid][2] += 1             # add one to current book end
      self.booksidx[-1][2] += 1                 # add one to all book end
      for i in range(bookid+1, len(self.booksidx)-1): # add one to start and end
        self.booksidx[i][1] += 1                # for all the ones in between
        self.booksidx[i][2] += 1

    # add new titles to index
    self.idxtitle(booklast, title)
    self.idxtitle(booklast, subtitle)

    # write databases
    with open(os.path.join(self.path, "songs.dat"), "w") as fh:
      json.dump(self.songs, fh)
    with open(os.path.join(self.path, "booksidx.dat"), "w") as fh:
      json.dump(self.booksidx, fh)
    self.titleidx = sorted(self.titleidx, key=lambda x: x[0])
    with open(os.path.join(self.path, "songsidx.dat"), "w") as fh:
      json.dump(self.titleidx, fh)

    rvalue = booklast # return new book sid
    return rvalue
    
    
  def setSongValue(self, sid, field, value):
    #print(self.songs[sid])
    self.songs[sid][field] = value
    #print(self.songs[sid])
    #exit(10)
    with open(os.path.join(self.path, "songs.dat"), "w") as fh:
      json.dump(self.songs, fh)
