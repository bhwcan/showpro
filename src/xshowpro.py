#
# showpro.py - show and database app for laptop connected to big screen
#(c) Byron Walton, bhwcan@netscape.net
#
import wx
#import wx.grid
#import string
#import webbrowser
#from pathlib import Path

#local imports
from xsp_database import Database
from xsp_displays import Displays
from xsp_song import Song
from xsp_songpanel import SongPanel
from xsp_songwindow import SongWindow
from xsp_viewwindow import ViewWindow

#MAIN
#print("platform:", wx.Platform)
app = wx.App(False)
db = Database()

if not db.setrootpath():
  dlg = wx.MessageDialog(None,
                         " Invalid Path: " + db.getrootpath() + "\n",
                         "Please create showpro song database\n"\
                         "ask Byron", wx.OK|wx.ICON_ERROR)
  dlg.ShowModal() # Shows it
  dlg.Destroy() # finally destroy it when finished.
  exit(10)

displays = Displays()
viewrect = displays.getViewRect()
listrect = displays.getListRect()

# open the windows
songframe = SongWindow(None, "Showpro Songs")
viewframe = ViewWindow(songframe)
viewframe.SetPosition(wx.Point(viewrect[0], viewrect[1]+30))
viewframe.SetSize(wx.Size(viewrect[2],viewrect[3]-30))
songframe.SetPosition(wx.Point(listrect[0], listrect[1]+30))
panel = SongPanel(songframe, viewframe, db, listrect)
songframe.Show()
app.MainLoop()
