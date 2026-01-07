import wx


class TestFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(TestFrame, self).__init__(*args, **kw)

        self.CreateStatusBar()
        self.SetStatusText("Hi")


def main():
    app = wx.App()
    frm = TestFrame(None, title="Hi")
    frm.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
