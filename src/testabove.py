def allspacers(s):
  spacers = { ' ', '/', '|', '↓' , '-'}
  if not s:  # Handle empty string case
    return False
  for char in s:
    if char not in spacers:
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
#      lyricline += lyric

#      print("lyric:", "["+lyric+"]", ll, allspacers(lyric))

      if allspacers(lyric):
        chordline += ' ' * ll
        lyricline += ' ' * cp
        lyricline += lyric
      else:
        lyricline += lyric
        if cp >= ll:
          # plus one is to always have a space between chords
          chordline += ' '
          lyricline += ' ' * (cp-ll+1)
        else:
          chordline += ' ' * (ll-cp)

#      print("last spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cp, "lyric len:", ll)
#      print("|"+chordline+"|")
#      print("|"+lyricline+"|")
      break
    else:
      ce = line.find(']',s)
      if ce < 0:
        lyric = line[s:cs]
        ll = len(lyric)
        chord = line[cs+1:]
        cl = len(chord)
#        print("chord:", "["+chord+"]", cl)
#        print("lyric:", "["+lyric+"]", ll, allspacers(lyric))
 
        # add broken chord to end of lyric
        if allspacers(lyric):
          chordline += ' ' * ll
          chordline += chord
          lyricline += ' ' * cp
          lyricline += lyric
          lyricline += ' ' * cl
        else:
          lyricline += lyric
          if cl >= ll:
            chordline += ' ' * (cl-ll)
          chordline += line[cs+1:]
          lyricline += ' ' * cl
        
#        print("broken spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cl, "lyric len:", ll)
#        print("|"+chordline+"|")
#        print("|"+lyricline+"|")
        
        # done chords no closing brace
        #chordline += ' ' * (len(line[s:]) - cp)
        #cl = 0
        break

      # found end
      lyric = line[s:cs]
      ll = len(lyric)
      chord = line[cs+1:ce]
      cl = len(chord)
#      print("chord:", "["+chord+"]", cl)
#      print("lyric:", "["+lyric+"]", ll, allspacers(lyric))
      
      if allspacers(lyric):
        chordline += ' ' * ll
        chordline += chord
        lyricline += ' ' * cp
        lyricline += lyric
      else:
        lyricline += lyric
#        print("cp:", cp, "ll:", ll, "cp>0", cp>0, "cp>=ll", cp>=ll)
        if cp >= ll:
          # plus one is to always have a space between chords
#          print("add space")
          if cs > 0:
            chordline += ' '
            lyricline += ' ' * (cp-ll+1)
        else:
          chordline += ' ' * (ll-cp)
        chordline += chord
      
#      print("spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cp, "lyric len:", ll)
#      print("["+chordline+"]")
#      print("["+lyricline+"]")

      cp = cl

    s = ce + 1
    if s >= len(line):
      break

  # check if ends on chord expand lyric line
  if cs >= 0 and ce >= 0:
    lyricline += ' ' * (cp)

#  print("end spot:",s,"chord start:", cs, "chord end:", ce, "chord len:", cl, "lyric len:", ll)
#  print("|"+chordline+"|")
#  print("|"+lyricline+"|")

  return chordline, lyricline

# MAIN

print("Main *********************")

#line = "[A#dim5]/ [C+++++++]/"
#line = "[C ↓ ↓]/ [A ↓ Tacet] [C ↓ ↓]/ dog    [A ↓ Tacet dog"
#line = "[C ↓ ↓]/[A ↓]"
lines = ["[C] ↓ ↓ [A] ↓ [Tacet] /  [C] ↓ ↓ [A] ↓ [Tacet] /",
         "/ [C] ↓ ↓ [A] ↓ [G] ↓ / [F] ↓ ↓ ↓ ↓ / [D] - / [D] / -",
         "[C] [↓ ↓] [A] [↓] [G] [↓]  [F] [↓] [↓] [↓] [↓]   [D]    [D]",
         "Verse 1:",
         "[D]Left a good job in the [D]city", 
         "[D]Workin' for [D] -- [D] the man ev'ry [D]night and day",
         "[D]And I never lost↓ one [D]minute of sleepin'",
         "[D]Worryin' 'bout the way things [D]might h/ave been"
        ]

#lines = [
#         "[C] ↓ ↓ [A] ↓ [Tacet] /  [C] ↓ ↓ [A] ↓ [Tacet] /" 
#        ]

print("\nOUT\n")

for line in lines:
  chordline, lyricline = parsechords(line)
  if chordline:
    print("chord|"+chordline+"|")
  if not lyricline.isspace():
    print("lyric|"+lyricline+"|")

