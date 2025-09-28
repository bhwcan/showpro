import sys
from xsp_database import Database

class Status():
  def __init__(self):
    self.text = ""

  def setstatus(self, text):
    self.text = text
    print(text)

db = Database()
sw = Status()

if len(sys.argv) > 1:
  filename = sys.argv[1]
else:
  print("must supply build directory")
  exit(10)

db.setrootpath(filename)
if not db.open():
  print("unable to open: ", filename)

db.rebuild(sw)

print("done", "found", len(db.songs), "songs")
