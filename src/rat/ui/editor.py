import wx
import wx.dataview

class StudentInfoEditorPanel(wx.Panel):
    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.list = wx.dataview.DataViewListCtrl(self, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_MULTIPLE)

        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dataview_item_activated, self.list)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_context_menu, self.list)
        # self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu, self.list)

        self.list.AppendTextColumn("ID", flags=wx.dataview.DATAVIEW_COL_HIDDEN)
        self.list.AppendTextColumn("Last Name", mode=wx.dataview.DATAVIEW_CELL_EDITABLE, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendTextColumn("First Name", mode=wx.dataview.DATAVIEW_CELL_EDITABLE, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn(wx.dataview.DataViewColumn("Gender", wx.dataview.DataViewChoiceRenderer(["Non-Binary", "Male", "Female"]), self.list.GetColumnCount(), flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE))
        self.list.AppendColumn(wx.dataview.DataViewColumn("Veto", wx.dataview.DataViewChoiceRenderer(["", "Non-Binary", "Male", "Female", "Non-Binary, Male", "Non-Binary, Female", "Male, Female"]), self.list.GetColumnCount(), flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE))

        top_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        button_add = wx.Button(self, id=wx.ID_ADD, label="Add")
        button_sizer.Add(button_add, flag=wx.RIGHT, border=5)

        button_delete = wx.Button(self, id=wx.ID_DELETE, label="Delete")
        button_sizer.Add(button_delete)

        self.Bind(wx.EVT_BUTTON, self.on_button)

        top_sizer.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        self.SetSizerAndFit(top_sizer)
    
    def add_student(self, id: int, last_name: str, first_name: str, gender: str) -> None:
        self.list.AppendItem([
            str(id),
            last_name,
            first_name,
            gender,
            ""
        ])

    def load_test_data(self):
        self.add_student(0, "A", "A", "Non-Binary")
        self.add_student(1, "B", "B", "Male")
        self.add_student(2, "C", "C", "Female")
    
    def on_dataview_item_activated(self, event: wx.dataview.DataViewEvent):
        print("on_dataview_item_activated")
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            print(column)
            self.list.EditItem(item, column)
    
    def on_button(self, event: wx.Event):
        print("on_button")
        if event.Id == wx.ID_ADD:
            self.add_student(0, "?", "?", "")
        elif event.Id == wx.ID_DELETE:
            for item in self.list.Selections:
                self.list.DeleteItem(self.list.ItemToRow(item))

    def on_menu(self, event: wx.MenuEvent, dv_item: wx.dataview.DataViewItem):
        print("on_menu")
        if event.Id == wx.ID_DELETE:
            print("delete")
            # self.list.DeleteItem(self.list.ItemToRow(dv_item))
            for item in self.list.Selections:
                self.list.DeleteItem(self.list.ItemToRow(item))

    def on_context_menu(self, event: wx.dataview.DataViewEvent):
        print("on_context_menu")

        item = event.Item

        menu = wx.Menu()
        menu.Append(wx.ID_DELETE, "&Delete")
        menu.Bind(wx.EVT_MENU, lambda event, dv_item=item: self.on_menu(event, dv_item))
        self.PopupMenu(menu, event.GetPosition())