def allspacers(s):
    if not s:  # Handle empty string case
        return True
    for char in s:
        if char != ' ' and char != '/' and char != '|':
            return False
    return True

def parsechords(line):
  
  s = 0
  cl = 0

  chordline = ""
  lyricline = ""

  #special case no chords
  cs = line.find('[',s)
  if cs < 0:
    lyricline = line
    return chordline, lyricline

  lp = 0
  cp = 0
  while True:
    cs = line.find('[',s)
    if cs < 0:
      # done chords
      lyric = line[s:]
      ll = len(lyric)
      lyricline += lyric
      
      print("last spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cp, "lyric len:", ll)
      print("["+lyricline+"]")
      print("["+chordline+"]")

      if cp >= ll:
        # plus one is to always have a space between chords
        chordline += ' '
        lyricline += ' ' * (cp-ll+1)
      if ll > cp:
        chordline += ' ' * (ll-cp)

      break
    else:
      ce = line.find(']',s)
      if ce < 0:
        lyric = line[s:cs]
        ll = len(lyric)
        chord = line[cs+1:]
        cl = len(chord)

        # add broken chord to end of lyric
        lyricline += lyric
        if cl >= ll:
          chordline += ' ' * (cl-ll)
        chordline += line[cs+1:]
        lyricline += ' ' * cl
        
        print("broken spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cl, "lyric len:", ll)
        print("|"+chordline+"|")
        print("|"+lyricline+"|")
        
        # done chords no closing brace
        #chordline += ' ' * (len(line[s:]) - cp)
        #cl = 0
        break

      # found end
      lyric = line[s:cs]
      ll = len(lyric)
      chord = line[cs+1:ce]
      cl = len(chord)
      print("chord:", "["+chord+"]", cl)
      print("lyric:", "["+lyric+"]", ll, allspacers(lyric))
      
      lyricline += lyric
      print("cp:", cp, "ll:", ll, "cp>0", cp>0, "cp>=ll", cp>=ll)
      if cp >= ll:
        # plus one is to always have a space between chords
        print("add space")
        #if cs > 0:
        chordline += ' '
        lyricline += ' ' * (cp-ll+1)
      else:
        chordline += ' ' * (ll-cp)
      chordline += chord
      
      print("spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cp, "lyric len:", ll)
      print("["+lyricline+"]")
      print("["+chordline+"]")

      cp = cl

    s = ce + 1
    if s >= len(line):
      break

  # check if ends on chord expand lyric line
  if cs >= 0 and ce >= 0:
    lyricline += ' ' * (cp)

  print("end spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cl, "lyric len:", ll)
  print("|"+chordline+"|")
  print("|"+lyricline+"|")

  return chordline, lyricline

# MAIN

#line = "[A#dim5]/ [C+++++++]/"
#line = "[C ↓ ↓]/ [A ↓ Tacet] [C ↓ ↓]/ dog    [A ↓ Tacet dog"
#line = "[C ↓ ↓]/[A ↓]"
line = "/ [C ↓ ↓] [A ↓] [G ↓] / [F ↓ ↓ ↓ ↓] / [D] / [D] /"

chordline, lyricline = parsechords(line)

print("OUT")
print("["+chordline+"]")
print("["+lyricline+"]")

