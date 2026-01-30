import wx
import wx.dataview

from rat.io import RoleAssignment

class OutputPanel(wx.Panel):
    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_ROLE = 3

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        
        self.init_layout()
        self.bind_event_handlers()

        self.list.AppendColumn("ID", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("Last Name", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("First Name", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("Role", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)

    def init_layout(self):
        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.list = wx.dataview.TreeListCtrl(self)
        top_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizerAndFit(top_sizer)

    def bind_event_handlers(self):
        pass

    def clear(self):
        self.list.DeleteAllItems()

    def load_group(self, group_name: str, assignments: set[RoleAssignment]):
        group_root = self.list.AppendItem(self.list.RootItem, group_name)

        for assignment in assignments:
            item = self.list.AppendItem(group_root, str(assignment.student.id))
            self.list.SetItemText(item, self.COL_LAST_NAME, assignment.student.last_name)
            self.list.SetItemText(item, self.COL_FIRST_NAME, assignment.student.first_name)
            self.list.SetItemText(item, self.COL_ROLE, assignment.assigned_role.name)
        
        self.list.Expand(group_root)
