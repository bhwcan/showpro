import wx
import wx.lib.scrolledpanel as scrolled

class ChordWindow(wx.Frame):
  def __init__(self, parent, name, strings, undefined, chorddefs, color):
    super().__init__(parent, title=name,style=(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP) & ~(wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
    self.undefined = undefined
    self.chorddefs = chorddefs
    self.strings = strings
    self.ch = 270
    self.cw = 170
    self.co = 20
    #height = viewrect[3]

    self.panel = wx.Panel(self)
    self.sizer = wx.BoxSizer(wx.VERTICAL)

    viewrect = parent.GetScreenRect()
    height = viewrect[3]
    
    # UI Elements
    if len(self.undefined) > 0:
      self.co += 70
      undefined_label = wx.StaticText(self.panel, label='Undefined Chords:')
      undefined_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
      undefined_text.AppendText(",".join(self.undefined))
      self.sizer.Add(undefined_label, 0, wx.ALL, 5)
      self.sizer.Add(undefined_text, 0, wx.EXPAND | wx.ALL, 5)

    ch = (height - self.co) // self.ch
    self.gridcols = len(self.chorddefs) // ch
    if (len(self.chorddefs) % ch) != 0:
      self.gridcols += 1

    self.chords = scrolled.ScrolledPanel(self.panel)
    self.chords.SetAutoLayout(1)
    self.chords.SetupScrolling()
#    self.chords.SetBackgroundColour(wx.BLACK)
    self.chordsizer = wx.GridSizer(self.gridcols)
    for cd in self.chorddefs:
      cw = DisplayChord(self.chords, self.strings, cd, color)
      self.chordsizer.Add(cw, 0, wx.ALL, 5)
    self.chords.SetSizer(self.chordsizer)
    self.sizer.Add(self.chords, 1, wx.EXPAND | wx.ALL, 5)
  
    self.panel.SetSizer(self.sizer)
    w = self.cw * 2
    if self.gridcols > 0:
      w = self.gridcols * self.cw
    h = self.ch * 2
    if ch > 0:
      h = (ch * self.ch) + self.co
    #print(viewrect, w, h)
    self.SetPosition(wx.Point(viewrect[0] + viewrect[2]-w-30, viewrect[1]+viewrect[3]-h)) # for mac top bar
    self.SetSize(w,h)
    self.Show()
    
class DisplayChord(wx.Panel):
  def __init__(self, parent, strings, chorddef, color):
    super().__init__(parent, size=(150, 250))

    defaultbgcolour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

    self.frets = chorddef["frets"]
    self.chord_name = chorddef["name"]
    self.base_fret = chorddef["base"]
    self.strings = strings
    self.colour = wx.BLACK

    if color == 1:
      self.colour = wx.Colour(180,0,0) 
    elif color == 2:
      self.colour = wx.Colour(0,0,180) 
    elif color == 3:
      self.colour = wx.Colour(0,180,0) 
        
    self.SetBackgroundColour(wx.WHITE)
    self.Bind(wx.EVT_PAINT, self.on_paint)
    
  def on_paint(self, event):
    dc = wx.PaintDC(self)
    
    num_strings = self.strings
    num_frets = 4
    width, height = self.GetSize()
    fret_gap = int(height / (num_frets + 3))  # Extra gap for chord name
    string_gap = int(width / (num_strings + 1))
        
    # Clear canvas at the beginning of painting
    dc.SetBackground(wx.Brush('white'))
    dc.SetTextForeground(wx.BLACK)
    dc.Clear()
        
    # Set thicker pen for grid lines
    dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), width=2))
        
    # Draw frets (start grid one fret_gap lower)
    for i in range(num_frets + 1):
      y = int((i + 1) * fret_gap)
      dc.DrawLine(int(string_gap), y, int(num_strings * string_gap), y)
        
    # Draw nut if base fret is 0
    if self.base_fret <= 1:
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
        dc.SetBrush(wx.Brush(self.colour, wx.BRUSHSTYLE_SOLID))
        dc.DrawCircle(x, y, 8)
        dc.SetBrush(wx.NullBrush)
        
    # Draw base fret number only if greater than 0
    if self.base_fret > 1:
      dc.DrawText(str(self.base_fret), int(string_gap * 0.1), int(fret_gap * 1.1))
        
    # Draw chord name below the grid
    font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    dc.DrawText(self.chord_name, int(width / 2 - 20), int((num_frets + 1.8) * fret_gap))
    
    
