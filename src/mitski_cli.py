"""Console-script entry points (declared in ``[project.scripts]`` of
``pyproject.toml``).

Each wrapper simply runs the matching file in ``scripts/`` as ``__main__``, so the
installed commands (``mitski-clean``, ``mitski-build``, ``mitski-figures``,
``mitski-3d``) behave exactly like ``python scripts/<name>.py`` and there is a
single source of truth for each step. This assumes an editable/source checkout
(``pip install -e .``), which is how the project is meant to be run.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    # src/mitski_cli.py -> repo root is two parents up; scripts/ lives there.
    return Path(__file__).resolve().parents[1] / "scripts"


def _run(script: str) -> None:
    path = _scripts_dir() / script
    if not path.exists():  # pragma: no cover - defensive
        raise FileNotFoundError(
            f"{path} not found; the console scripts require a source checkout "
            "(install with `pip install -e .`)."
        )
    # Preserve any CLI args the user passed after the command name.
    sys.argv = [str(path), *sys.argv[1:]]
    runpy.run_path(str(path), run_name="__main__")


def clean_lyrics() -> None:
    _run("clean_lyrics.py")


def build_dataset() -> None:
    _run("build_dataset.py")


def make_figures() -> None:
    _run("make_figures.py")


def make_3d() -> None:
    _run("make_3d.py")
