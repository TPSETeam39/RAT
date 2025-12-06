import wx
import wx.dataview

class WxApp(wx.App):
    def __init__(self):
        super().__init__(redirect=False)

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

        self.dataview_list = wx.dataview.DataViewListCtrl(self.panel, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_MULTIPLE)
        self.dataview_list.SetMinSize((500, 200))

        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dataview_item_activated, self.dataview_list)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu, self.dataview_list)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_context_menu, self.dataview_list)
        
        self.dataview_list.AppendTextColumn("Last Name", mode=wx.dataview.DATAVIEW_CELL_EDITABLE, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.dataview_list.AppendTextColumn("First Name", mode=wx.dataview.DATAVIEW_CELL_EDITABLE, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.dataview_list.AppendColumn(wx.dataview.DataViewColumn("Gender", wx.dataview.DataViewChoiceRenderer(["Non-Binary", "Male", "Female"]), self.dataview_list.GetColumnCount(), flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE))
        self.dataview_list.AppendColumn(wx.dataview.DataViewColumn("Veto", wx.dataview.DataViewChoiceRenderer(["", "Non-Binary", "Male", "Female", "Non-Binary, Male", "Non-Binary, Female", "Male, Female"]), self.dataview_list.GetColumnCount(), flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE))

        self.dataview_list.AppendItem(["A", "A", "Male", ""])
        self.dataview_list.AppendItem(["B", "B", "Male", ""])
        self.dataview_list.AppendItem(["C", "C", "Male", ""])
        self.dataview_list.AppendItem(["D", "D", "Male", ""])
        self.dataview_list.AppendItem(["E", "E", "Male", ""])
        self.dataview_list.AppendItem(["F", "F", "Male", ""])
        self.dataview_list.AppendItem(["G", "G", "Female", ""])

        main_sizer.Add(self.dataview_list)

        self.panel.SetSizerAndFit(main_sizer)
        self.Fit()
    
    def on_dataview_item_activated(self, event: wx.dataview.DataViewEvent):
        print("on_dataview_item_activated")
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            print(column)
            self.dataview_list.EditItem(item, column)
    
    def on_context_menu(self, event: wx.dataview.DataViewEvent):
        print("on_context_menu")

        menu = wx.Menu()
        menu.Append(0, "test")
        self.PopupMenu(menu, event.GetPosition())