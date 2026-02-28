import wx
import wx.dataview

from rat.io import Student, Role

class OutputPanel(wx.Panel):
    """
    A simple output display for student-to-role assignments, grouped and displayed as a tree.
    """

    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_ROLE = 3

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        
        self.list = wx.dataview.TreeListCtrl(self)
        self.list.AppendColumn("Student ID", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("Last Name", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("First Name", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.list.AppendColumn("Role", flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)

        self._init_layout()
        self._bind_event_handlers()

    def _init_layout(self):
        main_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        main_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(main_sizer)

    def _bind_event_handlers(self):
        pass

    def clear(self):
        """
        Clears all elements from the output display.
        """
        self.list.DeleteAllItems()

    def load_group(self, group_name: str, assignments: dict[Student, Role]):
        """
        Loads a list of assignments into the output display as a group.
        
        :param group_name: The name of the group.
        :type group_name: str
        :param assignments: The student-to-role assignments for the group.
        :type assignments: dict[Student, Role]
        """
        group_root = self.list.AppendItem(self.list.RootItem, group_name)

        for student, role in assignments.items():
            item = self.list.AppendItem(group_root, str(student.id))
            self.list.SetItemText(item, self.COL_LAST_NAME, student.last_name)
            self.list.SetItemText(item, self.COL_FIRST_NAME, student.first_name)
            self.list.SetItemText(item, self.COL_ROLE, role.name)
        
        self.list.Expand(group_root)
