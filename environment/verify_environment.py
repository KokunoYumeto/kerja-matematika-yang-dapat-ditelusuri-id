"""Fail closed unless the pinned container has the complete rebuild closure."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pypdf


EXPECTED_QUARTO = "1.9.37"
EXPECTED_PYTHON = (3, 13, 9)
EXPECTED_PYPDF = "6.12.2"
REQUIRED_COMMANDS = ("quarto", "xelatex", "kpsewhich")
REQUIRED_TEX_FILES = (
    "scrreprt.cls",
    "unicode-math.sty",
    "fontspec.sty",
    "lmodern.sty",
    "amsmath.sty",
    "amssymb.sty",
    "microtype.sty",
    "fancyhdr.sty",
    "fancyvrb.sty",
    "framed.sty",
    "longtable.sty",
    "booktabs.sty",
    "babel.sty",
    "tcolorbox.sty",
    "fontawesome5.sty",
    "bookmark.sty",
    "caption.sty",
    "subcaption.sty",
    "xurl.sty",
    "amsthm.sty",
    "lmsans10-bold.otf",
    "lmroman10-regular.otf",
    "latinmodern-math.otf",
    "FontAwesome5Free-Solid-900.otf",
    "msam10.pfb",
)


def output(command: list[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()


def main() -> None:
    missing_commands = [name for name in REQUIRED_COMMANDS if shutil.which(name) is None]
    if missing_commands:
        raise RuntimeError(f"missing commands: {missing_commands}")
    quarto = output(["quarto", "--version"]).splitlines()[0].strip()
    if quarto != EXPECTED_QUARTO:
        raise RuntimeError(f"Quarto {quarto!r}, expected {EXPECTED_QUARTO!r}")
    if sys.version_info[:3] != EXPECTED_PYTHON:
        raise RuntimeError(f"Python {sys.version_info[:3]!r}, expected {EXPECTED_PYTHON!r}")
    if pypdf.__version__ != EXPECTED_PYPDF:
        raise RuntimeError(f"pypdf {pypdf.__version__!r}, expected {EXPECTED_PYPDF!r}")

    tex_files = {}
    for name in REQUIRED_TEX_FILES:
        resolved = output(["kpsewhich", name])
        if not resolved or not Path(resolved).is_file():
            raise RuntimeError(f"TeX closure missing {name!r}")
        tex_files[name] = resolved

    payload = {
        "status": "PASS",
        "python": ".".join(map(str, sys.version_info[:3])),
        "pypdf": pypdf.__version__,
        "quarto": quarto,
        "xelatex": output(["xelatex", "--version"]).splitlines()[0],
        "tex_files": tex_files,
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
