#
# showpro.py - show and database app for laptop connected to big screen
#(c) Byron Walton, bhwcan@netscape.net
#
import wx

#local imports
from xsp_database import Database
from xsp_mainwindow import MainWindow

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


# open the windows
mainframe = MainWindow(db)
mainframe.Show()
app.MainLoop()
