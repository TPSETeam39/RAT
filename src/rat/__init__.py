import sys
import traceback

from .ui import RATApp

def excepthook(type, value, tb):
    print("Uncaught exception:")
    traceback.print_exception(type, value, tb)
sys.excepthook = excepthook

def main() -> None:
    app = RATApp()
    app.MainLoop()
