import wx

class EditFind(wx.FindReplaceDialog):
  def __init__(self, parent):
    self.data = wx.FindReplaceData()
    self.control = parent.control
    self.data.SetFlags(wx.FR_MATCHCASE|wx.FR_DOWN)
    wx.FindReplaceDialog.__init__(self, parent, self.data, "Find", wx.FR_NOUPDOWN | wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
    #wx.FindReplaceDialog.__init__(self, parent, self.data, "Find", wx.FR_NOUPDOWN | wx.FR_NOWHOLEWORD)
    wpos = parent.GetPosition()
    wsize = parent.GetSize()
    self.SetPosition(wx.Point(wpos[0]+wsize[0]+1,wpos[1])) 

    self.pos = 0
    
    self.Bind(wx.EVT_FIND, self.on_find)
    self.Bind(wx.EVT_FIND_NEXT, self.on_next)
#    self.Bind(wx.EVT_FIND_REPLACE, self.on_find_replace)
#    self.Bind(wx.EVT_FIND_REPLACE_ALL, self.on_find_replace_all)
    self.Bind(wx.EVT_FIND_CLOSE, self.on_close)

    self.Show()

  def on_find(self, event):
    self.pos = 0
    self.text = self.control.GetValue()
    self.on_next(event)

  def fixpos(self, data, newpos):
    rpos = newpos
    if  wx.Platform == "__WXMSW__":
      nl = data[0:newpos-1].count('\n')
      rpos = newpos + nl
    return rpos
      
  def on_next(self, event):
    findstr = self.data.GetFindString()
    newpos = self.text.find(findstr, self.pos)
    #print("newpos:", newpos, "self.pos:", self.pos)
    if newpos >= self.pos:
      self.control.SetInsertionPoint(self.fixpos(self.text,newpos))
      self.pos = newpos + 1
      self.control.SetFocus()
      self.Parent.Raise()
    else:
      self.on_find(event)
#    event.Skip()

#  def on_find_replace(self, event):
#    findstr = self.data.GetFindString()
#    replacestr = self.data.GetReplaceString()
#    print("find_replace", findstr, replace_str)
#    event.Skip()

#  def on_find_replace_all(self, event):
#    findstr = self.data.GetFindString()
#    replacestr = self.data.GetReplaceString()
#    print("find_replace_all", findstr, replace_str)
#    event.Skip()

  def on_close(self, event):
    self.Parent.findopen = False
#    self.Close(True)  # Close the frame.
#    print("on_close")
    event.Skip()

