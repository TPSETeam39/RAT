import wx
import wx.dataview

from .editor import Student

class OutputPanel(wx.Panel):
    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_ROLE = 3

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        
        self.init_layout()
        self.bind_event_handlers()

        self.list.AppendColumn("ID")
        self.list.AppendColumn("Last Name")
        self.list.AppendColumn("First Name")
        self.list.AppendColumn("Role")

    def init_layout(self):
        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.list = wx.dataview.TreeListCtrl(self)
        top_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizerAndFit(top_sizer)

    def bind_event_handlers(self):
        pass

    def clear(self):
        self.list.DeleteAllItems()

    def load_group(self, group_name: str, students: list[Student]):
        group_root = self.list.AppendItem(self.list.RootItem, group_name)

        for student in students:
            item = self.list.AppendItem(group_root, str(student.id))
            self.list.SetItemText(item, self.COL_LAST_NAME, student.last_name)
            self.list.SetItemText(item, self.COL_FIRST_NAME, student.first_name)
            self.list.SetItemText(item, self.COL_ROLE, "?")
