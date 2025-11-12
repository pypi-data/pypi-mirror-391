import os, sys, inspect, uuid

_RUNCACHE: dict = {}

class Pyy:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
    def compile(self) -> str | None:
        try:
            with open(self.filename) as file:
                self.content: str = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"could not find file '{self.filename}'") from None
        compiled: str = ""
        for line in self.content.split("\n"):
            indentation: int = len(line) - len(line.lstrip())
            if line.strip().removeprefix("#").strip() == "pyy=false":
                if "--force" in sys.argv:
                    exec(self.content)
                    return None
                raise PermissionError("pyy does not have permission to run that file, rerun with --force to use base python instead when this error is raised. (pyy=false comment found)")
            elif line.lstrip().startswith("public def") or line.lstrip().startswith("public class") or line.lstrip().startswith("public async def"):
                public_Pyy = Pyy(f"{line.lstrip().removeprefix('public def ').removeprefix('public class ').removeprefix('public async def ').split('(')[0].split(':')[0]}.pyy")
                compiled += f"\n{' '*indentation}{line.lstrip().removeprefix('public ').removesuffix(':')}:\n{'\n'.join([' '*(indentation+4)+line2 for line2 in ['...']+public_Pyy.compile().split('\n')])}"
            elif line.lstrip().startswith("public post def") or line.lstrip().startswith("public post class") or line.lstrip().startswith("public post async def"):
                public_Pyy = Pyy(f"{line.lstrip().removeprefix('public post def ').removeprefix('public post class ').removeprefix('public post async def ').split('(')[0].split(':')[0]}.pyy")
                uid: str = str(uuid.uuid4())
                _RUNCACHE[uid] = public_Pyy
                compiled += f"\n{' '*indentation}from pyy import _RUNCACHE\n{' '*indentation}{line.lstrip().removeprefix('public post ').removesuffix(':')}:\n{' '*(indentation+4)}def post():\n{' '*(indentation+8)}exec(_RUNCACHE['{uid}'].compile())"
            elif line.lstrip().startswith("export def") and line.rstrip().endswith(":"):
                compiled += f"\n{' '*indentation}from pyy import export\n{' '*indentation}@export\n{' '*indentation}{line.strip().removeprefix('export ').removesuffix(':').strip()}():"
            elif line.lstrip().startswith("export") and line.rstrip().endswith(":"):
                compiled += f"\n{' '*indentation}from pyy import exportnr\n{' '*indentation}@exportnr\n{' '*indentation}def {line.strip().removeprefix('export').removesuffix(':').strip()}():"
            
            else:
                compiled += f"\n{line}"
        return compiled
    def __str__(self) -> str:
        return f"pyy=true"

NOTHING: int = 1
WARNING: int = 2
ERROR: int = 3

def is_pyy(__globals: dict, level: int = 1) -> bool:
    pyy: bool = "__pyy__" in __globals
    if level == 2 and not pyy:
        print("\033[92;1mwarning!\033[0m this script works better when run with pyy. learn more: https://github.com/by-semicolon/pyy")
        return pyy
    elif level == 3 and not pyy:
        raise RuntimeError("this script depends on and must be run with pyy. learn more: https://github.com/by-semicolon/pyy")
    else:
        return pyy

def exportnr(fn):
    uid: str = str(uuid.uuid4())
    _RUNCACHE[uid] = fn
    with open(f"{fn.__name__}.pyy", "w") as file:
        file.write(f"from pyy import _RUNCACHE\n_RUNCACHE['{uid}']()")

def export(fn):
    exportnr(fn)
    return fn

def wipe(fn):
    os.remove(f"{fn.__name__}.pyy")

def import_pyy(filename: str, __globals: dict) -> dict:
    filename = filename + ".py" if not filename.endswith(".py") else filename
    d: dict = {}
    exec(Pyy(filename).compile(), d)
    __globals[os.path.basename(filename).removesuffix(".py")] = type("PyyModule", (), d)