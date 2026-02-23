import wx

from rat.io import Student, Role

from .output import OutputPanel

class OutputWindow(wx.Frame):
    def __init__(self, assignments: dict[Student, Role]):
        super().__init__(parent=None, title="Assignment")

        self.SetMinSize((600, 500))

        self.panel = wx.Panel(self)

        self.output_display = OutputPanel(self.panel)
        self.output_display.load_group("", assignments)

        self._init_layout()
        self._bind_event_handlers()
    
    def _init_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.output_display, 1, wx.EXPAND | wx.ALL)
        
        self.panel.SetSizerAndFit(main_sizer)
        self.Fit()

    def _bind_event_handlers(self):
        pass
