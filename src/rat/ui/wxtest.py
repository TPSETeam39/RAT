import wx
import wx.dataview

from .role_editor import Role, RoleEditorPanel
from rat.role_assignment_calculator.genders import Gender


class WxApp(wx.App):
    def __init__(self):
        super().__init__(redirect=False)
        self.frame = TestWindow()
        self.frame.Show()


class TestWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Test")

        self.SetMinSize((800, 500))

        self.panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.role_editor = RoleEditorPanel(self.panel)
        sizer.Add(self.role_editor, 1, wx.EXPAND | wx.ALL, 10)

        # Test data
        self.role_editor.add_role(Role(None, "Role 1", Gender.FEMALE))
        self.role_editor.add_role(Role(None, "Role 2", Gender.MALE))
        self.role_editor.add_role(Role(None, "Role 3", Gender.NON_BINARY))

        self.panel.SetSizerAndFit(sizer)
        self.Fit()


if __name__ == "__main__":
    app = WxApp()
    app.MainLoop()
