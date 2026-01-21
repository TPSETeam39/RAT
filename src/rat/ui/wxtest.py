import wx
import wx.dataview

from .editor import StudentInfoEditorPanel, StudentInfoDataViewModel
from .output import OutputPanel

class WxApp(wx.App):
    def __init__(self):
        super().__init__(redirect=False)

        # wx.Log.SetActiveTarget(wx.LogStderr())

        self.frame = TestWindow()
        self.frame.Show()

class TestWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Test")

        self.SetMinSize((1200, 500))

        self.menu_bar = wx.MenuBar()
        test_menu = wx.Menu()
        test_menu.Append(0, "Hi")
        self.menu_bar.Append(test_menu, "&Test")

        self.SetMenuBar(self.menu_bar)

        self.panel = wx.Panel(self)
        
        #main_sizer = wx.FlexGridSizer(2, 10, 10)
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #self.label = wx.StaticText(self.panel, label="Hi from wxPython!")
        #main_sizer.Add(self.label)

        self.button = wx.Button(self.panel, label="Press me!")
        self.Bind(wx.EVT_BUTTON, self.on_button, self.button)
        main_sizer.Add(self.button)

        self.test = StudentInfoEditorPanel(self.panel)
        #self.test.BackgroundColour = wx.RED
        #self.test.SetMinSize((500, 200))
        main_sizer.Add(self.test, 1, wx.EXPAND | wx.ALL)

        self.test2 = StudentInfoEditorPanel(self.panel)
        #self.test2.BackgroundColour = wx.BLUE
        main_sizer.Add(self.test2, 1, wx.EXPAND | wx.ALL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL)

        self.test3 = OutputPanel(self.panel)
        top_sizer.Add(self.test3, 1, wx.EXPAND | wx.ALL)

        self.panel.SetSizerAndFit(top_sizer)
        self.Fit()
    
    def on_button(self, event: wx.Event):
        self.test3.clear()
        self.test3.load_group("Test Group 1", self.test.get_students())
        self.test3.load_group("Test Group 2", self.test2.get_students())
