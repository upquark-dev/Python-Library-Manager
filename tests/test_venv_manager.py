"""Tests for core.venv_manager pure path helpers (no subprocess/filesystem writes)."""

import os

from core.venv_manager import VirtualEnvManager


def _manager(system):
    mgr = VirtualEnvManager()
    mgr.system = system
    return mgr


def test_get_venv_python_windows():
    mgr = _manager("Windows")
    assert mgr.get_venv_python("/x/env") == os.path.join("/x/env", "Scripts", "python.exe")


def test_get_venv_python_posix():
    mgr = _manager("Linux")
    assert mgr.get_venv_python("/x/env") == os.path.join("/x/env", "bin", "python")


def test_get_activate_command_windows():
    mgr = _manager("Windows")
    assert mgr.get_activate_command("/x/env") == os.path.join("/x/env", "Scripts", "activate.bat")


def test_get_activate_command_posix_is_sourced():
    mgr = _manager("Linux")
    cmd = mgr.get_activate_command("/x/env")
    assert cmd.startswith("source ")
    assert cmd.endswith(os.path.join("bin", "activate"))


def test_is_valid_venv_false_for_plain_directory(tmp_path):
    assert _manager("Windows")._is_valid_venv(str(tmp_path)) is False


def test_is_valid_venv_true_when_python_and_activate_exist(tmp_path):
    mgr = _manager("Linux")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python").write_text("", encoding="utf-8")
    (bin_dir / "activate").write_text("", encoding="utf-8")
    assert mgr._is_valid_venv(str(tmp_path)) is True
