import wx

class Displays:
  def __init__(self):
    # figure out the displays for windows - should be a class
    self.displays = []
    self.wideidx = 0
    self.appidx = 0

    widevalue = 0
    dcount = wx.Display.GetCount()
    #dcount = 1
    for dc in range(dcount):
      d = wx.Display(dc)
      geo = d.GetGeometry()
      if geo[2] > widevalue:
        widevalue = geo[2]
        self.wideidx = dc
      #print(geo)
      self.displays.append(geo)

    if dcount > 1:
      for dc in range(dcount):
        if dc != self.wideidx:
          self.appidx = dc
          break
    else:
      half = int(self.displays[0][2]/2)
      self.displays[0][2] = half
      self.displays.append(wx.Rect([half, self.displays[0][1], half, self.displays[0][3]]))
      self.appidx = 1

  def getViewRect(self):
    return(self.displays[self.wideidx])

  def getListRect(self):
    return(self.displays[self.appidx])

