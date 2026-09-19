"""Runtime environment helpers.

In a PyInstaller-frozen build, ``sys.executable`` is the frozen GUI exe, not
a Python interpreter. Spawning it (e.g. ``[sys.executable, '--version']``)
re-launches the whole application, which recursively spawns again — an
infinite process loop. Use ``default_python_executable()`` instead of
``sys.executable`` whenever a real interpreter is needed for subprocesses.
"""

import shutil
import sys


def is_frozen() -> bool:
    """True when running inside a PyInstaller-frozen executable."""
    return getattr(sys, 'frozen', False)


def default_python_executable() -> str:
    """Return a real Python interpreter path, never the frozen exe.

    Falls back to ``python``/``py`` found on PATH when frozen; returns an
    empty string if no interpreter can be located.
    """
    if is_frozen():
        return shutil.which('python') or shutil.which('py') or ''
    return sys.executable
