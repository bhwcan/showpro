import wx
import wx.lib.scrolledpanel as scrolled

class ChordWindow(wx.Frame):
  def __init__(self, parent, name, strings, undefined, chorddefs):
    super().__init__(parent, title=name, size=(400, 1050))
    self.undefined = undefined
    self.chorddefs = chorddefs
    self.strings = strings
    self.gridcols = len(self.chorddefs) // 3
    if (len(self.chorddefs) % 3) != 0:
      self.gridcols += 1

    self.panel = wx.Panel(self)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
        
    # UI Elements
    if len(self.undefined) > 0:
      undefined_label = wx.StaticText(self.panel, label='Undefined Chords:')
      undefined_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
      undefined_text.AppendText(",".join(self.undefined))
      self.sizer.Add(undefined_label, 0, wx.ALL, 5)
      self.sizer.Add(undefined_text, 0, wx.EXPAND | wx.ALL, 5)

    self.chords = scrolled.ScrolledPanel(self.panel)
    self.chords.SetAutoLayout(1)
    self.chords.SetupScrolling()
#    self.chords.SetBackgroundColour(wx.BLACK)
    self.chordsizer = wx.GridSizer(self.gridcols)
    for cd in self.chorddefs:
      cw = DisplayChord(self.chords, self.strings, cd)
      self.chordsizer.Add(cw, 0, wx.ALL, 5)
    self.chords.SetSizer(self.chordsizer)
    self.sizer.Add(self.chords, 1, wx.EXPAND | wx.ALL, 5)
  
    self.panel.SetSizer(self.sizer)
    self.Show()
    
class DisplayChord(wx.Panel):
  def __init__(self, parent, strings, chorddef):
    super().__init__(parent, size=(150, 250))

    self.frets = chorddef["frets"]
    self.chord_name = chorddef["name"]
    self.base_fret = chorddef["base"]
    self.strings = strings
        
    self.SetBackgroundColour(wx.WHITE)
    self.Bind(wx.EVT_PAINT, self.on_paint)
    
  def on_paint(self, event):
    dc = wx.PaintDC(self)
    
    strings = self.strings
    num_strings = len(strings)
    num_frets = 4
    width, height = self.GetSize()
    fret_gap = int(height / (num_frets + 3))  # Extra gap for chord name
    string_gap = int(width / (num_strings + 1))
        
    # Clear canvas at the beginning of painting
    dc.SetBackground(wx.Brush('white'))
    dc.Clear()
        
    # Set thicker pen for grid lines
    dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), width=2))
        
    # Draw frets (start grid one fret_gap lower)
    for i in range(num_frets + 1):
      y = int((i + 1) * fret_gap)
      dc.DrawLine(int(string_gap), y, int(num_strings * string_gap), y)
        
    # Draw nut if base fret is 0
    if self.base_fret == 0:
      dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), width=8))
      dc.DrawLine(int(string_gap), fret_gap, int(num_strings * string_gap), fret_gap)
      dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), width=2))
        
    # Draw strings
    for i in range(num_strings):
      x = int((i + 1) * string_gap)
      dc.DrawLine(x, fret_gap, x, int((num_frets + 1) * fret_gap))
        
    # Draw open, muted, and fretted string markers
    font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    dc.SetFont(font)
    for i, fret in enumerate(self.frets):
      x = int((i + 1) * string_gap)
      if fret == -1:  # Muted string
        dc.DrawText('X', x - 5, int(fret_gap * 0.5))
      elif fret == 0:  # Open string
        dc.DrawText('O', x - 5, int(fret_gap * 0.5))
      elif isinstance(fret, int) and fret > 0:
        y = max(0, min(int((fret + 1) * fret_gap - (fret_gap / 2)), int((num_frets + 1) * fret_gap)))
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 255), wx.BRUSHSTYLE_SOLID))
        dc.DrawCircle(x, y, 8)
        dc.SetBrush(wx.NullBrush)
        
    # Draw base fret number only if greater than 0
    if self.base_fret > 1:
      dc.DrawText(str(self.base_fret), int(string_gap * 0.1), int(fret_gap * 1.1))
        
    # Draw string labels just below the last fret
    #for i, string in enumerate(strings):
    #  x = int((i + 1) * string_gap)
    #  dc.DrawText(string, x - 5, int((num_frets + 1.2) * fret_gap))
        
    # Draw chord name below the grid
    font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    dc.DrawText(self.chord_name, int(width / 2 - 20), int((num_frets + 1.8) * fret_gap))
    
