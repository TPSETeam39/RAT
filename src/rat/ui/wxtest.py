import wx

from rat.io import StudentGender, RoleGender, Student, Role, GenderVetoOption
from rat.role_assignment_calculator.calculator import Calculator
from .editor import StudentInfoEditorPanel
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
        
        self.test_button = wx.Button(self.panel, label="Press me!")

        self.student_editor = StudentInfoEditorPanel(self.panel)

        # self.role_editor = StudentInfoEditorPanel(self.panel) # TODO: use role editor

        self.output_display = OutputPanel(self.panel)

        self._init_layout()
        self._bind_event_handlers()
    
    def _init_layout(self):
        upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        upper_sizer.Add(self.test_button)
        upper_sizer.Add(self.student_editor, 1, wx.EXPAND | wx.ALL)
        # upper_sizer.Add(self.role_editor, 1, wx.EXPAND | wx.ALL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(upper_sizer, 1, wx.EXPAND | wx.ALL)
        main_sizer.Add(self.output_display, 1, wx.EXPAND | wx.ALL)

        self.panel.SetSizerAndFit(main_sizer)
        self.Fit()

    def _bind_event_handlers(self):
        self.Bind(wx.EVT_BUTTON, self._on_button, self.test_button)
    
    def _on_button(self, event: wx.Event):
        roles = set()
        for i in range(0, 30):
            roles.add(Role(i, f"Role {i}", RoleGender.MALE))

        students = set()
        for student in self.student_editor.get_students():
            students.add(Student(student.id, StudentGender.NON_BINARY, student.first_name, student.last_name, GenderVetoOption.NO_VETOES))
        
        calc = Calculator(roles, students)
        assignments = calc.calculate_role_assignments()

        self.output_display.clear()
        self.output_display.load_group("Group 1", assignments)
