import wx

from rat.role_assignment_calculator.calculator import Calculator
from .student_editor import StudentInfoEditorPanel
from .role_editor import RoleEditorPanel
from .output_window import OutputWindow


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Role Assignment Tool")

        self.SetMinSize((400, 400))

        self.menu_bar = wx.MenuBar()
        test_menu = wx.Menu()
        test_menu.Append(0, "Hi")
        self.menu_bar.Append(test_menu, "&File")
        self.SetMenuBar(self.menu_bar)

        self.panel = wx.Panel(self)

        self.calc_button = wx.Button(self.panel, label="Assign Roles")

        self.student_editor = StudentInfoEditorPanel(self.panel)

        self.role_editor = RoleEditorPanel(self.panel)

        self._init_layout()
        self._bind_event_handlers()

    def _init_layout(self):
        upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        left_sizer.Add(
            wx.StaticText(self.panel, label="Students"),
            flag=wx.UP | wx.LEFT | wx.ALIGN_CENTER,
            border=5,
        )
        left_sizer.Add(self.student_editor, 1, wx.EXPAND | wx.ALL)
        right_sizer.Add(
            wx.StaticText(self.panel, label="Roles"),
            flag=wx.UP | wx.LEFT | wx.ALIGN_CENTER,
            border=5,
        )
        right_sizer.Add(self.role_editor, 1, wx.EXPAND | wx.ALL)

        upper_sizer.Add(left_sizer, 1, wx.EXPAND)
        upper_sizer.Add(right_sizer, 1, wx.EXPAND)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(upper_sizer, 1, wx.EXPAND | wx.ALL)
        main_sizer.Add(wx.StaticLine(self.panel))
        main_sizer.Add(self.calc_button, flag=wx.ALL | wx.ALIGN_RIGHT, border=5)

        self.panel.SetSizerAndFit(main_sizer)
        self.Fit()

    def _bind_event_handlers(self):
        self.Bind(wx.EVT_BUTTON, self._on_button, self.calc_button)

    def _on_button(self, event: wx.Event):
        roles = self.role_editor.get_roles()

        students = self.student_editor.get_students()

        calc = Calculator(roles, students)
        assignments = calc.calculate_role_assignments()

        OutputWindow(assignments).Show()
