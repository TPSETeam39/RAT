import sys
import traceback

from .ui.wxtest import WxApp

def excepthook(type, value, tb):
    print("Uncaught exception:")
    traceback.print_exception(type, value, tb)
sys.excepthook = excepthook

def main() -> None:
    app = WxApp()
    app.MainLoop()
