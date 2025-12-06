import wx
import wx.dataview

class WxApp(wx.App):
    def __init__(self):
        super().__init__(redirect=True)

        # wx.Log.SetActiveTarget(wx.LogStderr())

        self.frame = TestWindow()
        self.frame.Show()

class TestWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Test")

        self.panel = wx.Panel(self)
        
        main_sizer = wx.FlexGridSizer(2, 10, 10)

        self.label = wx.StaticText(self.panel, label="Hi from wxPython!")
        main_sizer.Add(self.label)

        self.button = wx.Button(self.panel, label="Press me!")
        main_sizer.Add(self.button)

        tree_list = wx.dataview.TreeListCtrl(self.panel)
        tree_list.SetMinSize((100, 100))

        tree_list.AppendColumn("A", width=100)
        tree_list.AppendColumn("B", width=100)
        tree_list.AppendColumn("C", width=100)

        tree_list.AppendItem(tree_list.GetRootItem(), "Hi")
        tree_list.AppendItem(tree_list.GetRootItem(), "Hi")
        
        main_sizer.Add(tree_list, 1, wx.EXPAND | wx.ALL)

        list = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        list.InsertColumn(0, "A", width=100)
        list.InsertColumn(1, "B", width=100)
        list.InsertColumn(2, "C", width=100)

        list.InsertItem(0, "Hi")
        list.SetItem(0, 1, "Hi")
        list.SetItem(0, 2, "Hi")

        list.InsertItem(1, "Bye")
        list.SetItem(1, 1, "Bye")
        list.SetItem(1, 2, "Bye")

        main_sizer.Add(list)

        self.panel.SetSizerAndFit(main_sizer)
        self.Fit()
