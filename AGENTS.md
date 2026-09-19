# AGENTS.md

This file provides guidance to the AI agent when working with code in this repository.

Python Library Manager — a PyQt6 desktop GUI for bulk-installing Python packages. It is a GUI app; `python main.py` opens a window and cannot be exercised headless.

## Commands
- Run: `python main.py`
- Deps: `pip install -r requirements.txt` — note: this file is a full `pip freeze` (90+ pinned packages, some future-dated), not minimal. Actual runtime deps are `PyQt6`, `requests`, and `pywin32` (Windows only).
- Package (exe): single PyInstaller spec — `PythonLibraryManager.spec` (windowed, `console=False`). PyInstaller is NOT installed in the system Python; it lives in the repo-local `.build-libs/` (used via PYTHONPATH): `PYTHONPATH=.build-libs python -m PyInstaller --clean --noconfirm PythonLibraryManager.spec` — build with a Python that has PyQt6 installed. (There used to be a `PLM_debug.spec` console variant; it was removed — recreate with `--console` if ever needed.)
- Lint (CI, Python 3.10): only `flake8 . --select=E9,F63,F7,F82` fails the build (syntax errors / undefined names). Everything else is advisory (`--exit-zero`, max-line-length 127). Match this gate if you extend linting.
- Test: CI runs `pytest` — there IS a real suite: `tests/` has 6 modules (~500 lines, 53 cases) covering `core/` only, all Qt-free. Tests mock `subprocess.run`; `test_installer.py` locks in the no-`shell=True` security contract — run it before touching `core/installer.py`.
  - Single test: `pytest tests/test_installer.py::test_name` or `pytest -k keyword`.
  - `tests/conftest.py` inserts the repo root into `sys.path`, so `import core.*` works from any invocation directory.
  - `ui/` has zero coverage; don't add Qt-dependent tests expecting CI to pass (CI runs on ubuntu-latest).

## Architecture
- `core/` = platform logic with **no Qt imports**; `ui/` = PyQt6 widgets. Keep that boundary.
- `core/installer.py` builds pip commands as an **argument list, never `shell=True`**, and rewrites a leading `pip ` into `[python_executable, '-m', 'pip', ...]` via `shlex.split` to avoid injection. Preserve this pattern when editing install/uninstall. Python-version switching flows through `set_python_executable()`.
- Add/edit packages by editing the `LIBRARY_CATEGORIES` dict in `core/library_data.py` (list of `{name, description, install_cmd}` per category).

## UI conventions
- Features are embedded as tabs in `ui/main_window.py`, not popup dialogs; several `ui/*_dialog.py` files are legacy.
- Blue theme (`#3498db`) centralized in `ui/theme_manager.py`; buttons are text-only (no icons/emoji).
- i18n: user-facing strings go through `tr('key')` from `ui/i18n.py` (en/zh dicts; unknown keys fall back to English). When adding UI text, add the key to BOTH dicts and register the widget in `MainWindow.retranslate_ui()` so language switching reaches it. Category names translate via `tr('cat.' + name)`. Theme/language persist via `QSettings("DevTools", "Library Manager")`.

## Repo gotchas
- There is **no root `.gitignore`**. Committed bytecode was cleaned out (2026-09), but running the app/tests regenerates `__pycache__/*.pyc` (cpython-314 locally) as untracked noise in `git status`, along with `build/` after packaging — do not `git add -A` blindly.
- Frozen builds: in the packaged exe, `sys.executable` is the exe itself. Spawning it as if it were Python (e.g. `[sys.executable, '--version']`) recursively relaunches the GUI — an infinite process loop. `main.py` exits immediately on any dash-arg when frozen (`sys.frozen`), and core modules must get their interpreter from `core/runtime.default_python_executable()` (falls back to `python`/`py` on PATH) instead of `sys.executable`. A onefile exe legitimately shows exactly 2 processes (bootloader parent + app child); more means a spawn bug.
- Local dev runs a newer Python than CI: the working tree has cpython-314 `.pyc` while committed ones are cpython-311.
