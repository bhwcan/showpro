import os
import json
import string
from pathlib import Path

class ChordBase():
  def __init__(self):
    self.chorddefs = []
    self.path = os.path.join(Path.home(), "Documents", "showpro")
    if os.path.exists(os.path.join(self.path, "chords.dat")):
      with open(os.path.join(self.path, "chords.dat"), "r") as cf:
        self.chorddefs = json.load(cf)
  
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

