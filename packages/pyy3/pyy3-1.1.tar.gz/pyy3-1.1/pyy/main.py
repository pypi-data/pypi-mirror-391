import sys, os
from . import Pyy

def run() -> None:
    Pyy = Pyy(sys.argv[1])
    compiled: str | None = Pyy.compile()
    if compiled:
        (print if "--debug" in sys.argv else exec)(compiled, {"__file__": os.path.abspath(sys.argv[1]), "__pyy__": Pyy})