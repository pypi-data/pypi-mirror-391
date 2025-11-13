from pathlib import Path
from importlib.resources import files
import textwrap

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")

def copy_resource(src: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(src)
    content = files('flecsi_sandbox._auxiliary_files').joinpath(src).read_text()
    print(content)
    write(dest / src, content)
