import wx

from .main_window import MainWindow

class RATApp(wx.App):
    def __init__(self):
        super().__init__(redirect=False)

        # wx.Log.SetActiveTarget(wx.LogStderr())

        self.frame = MainWindow()
        self.frame.Show()
