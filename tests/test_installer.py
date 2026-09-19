"""Tests for core.installer.PackageInstaller.

These lock in the security-critical behaviour: pip commands are always built as
an argument list (never ``shell=True``) and a leading ``pip `` is rewritten to
``[python_executable, '-m', 'pip', ...]`` via shlex.split.
"""

import subprocess
import sys
from unittest import mock

from core.installer import PackageInstaller


def _completed(returncode=0, stdout="", stderr=""):
    """A side_effect callable that mimics subprocess.run -> CompletedProcess."""
    def _run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args")
        return subprocess.CompletedProcess(args=cmd, returncode=returncode,
                                           stdout=stdout, stderr=stderr)
    return _run


def test_default_python_executable_is_current_interpreter():
    assert PackageInstaller().python_executable == sys.executable


def test_set_python_executable_overrides_target():
    installer = PackageInstaller()
    installer.set_python_executable("/opt/custom/python")
    assert installer.python_executable == "/opt/custom/python"


def test_install_package_builds_module_pip_argument_list():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=_completed(stdout="ok")) as run:
        success, output = installer.install_package("pip install numpy")

    assert success is True
    assert output == "ok"
    assert run.call_args.args[0] == [sys.executable, "-m", "pip", "install", "numpy"]
    assert run.call_args.kwargs.get("shell") is not True


def test_install_package_uses_selected_python_executable():
    installer = PackageInstaller()
    installer.set_python_executable("/opt/custom/python")
    with mock.patch("core.installer.subprocess.run", side_effect=_completed()) as run:
        installer.install_package("pip install numpy")
    assert run.call_args.args[0][0] == "/opt/custom/python"


def test_install_package_does_not_interpret_shell_metacharacters():
    """Shell metacharacters must be passed to pip as literal args, never executed."""
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=_completed(returncode=1, stderr="err")) as run:
        success, _ = installer.install_package("pip install foo && rm -rf /")

    assert success is False
    args = run.call_args.args[0]
    assert isinstance(args, list)
    assert run.call_args.kwargs.get("shell") is not True
    assert args == [sys.executable, "-m", "pip", "install", "foo", "&&", "rm", "-rf", "/"]


def test_install_package_non_pip_command_passthrough():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run", side_effect=_completed()) as run:
        installer.install_package("conda install foo")
    assert run.call_args.args[0] == ["conda", "install", "foo"]


def test_install_package_failure_returns_combined_output():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=_completed(returncode=1, stdout="o", stderr="e")):
        success, output = installer.install_package("pip install nope")
    assert success is False
    assert output == "oe"


def test_install_package_timeout_is_reported():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=subprocess.TimeoutExpired(cmd="pip", timeout=300)):
        success, output = installer.install_package("pip install slow")
    assert success is False
    assert "timed out" in output


def test_uninstall_package_builds_yes_flag_argument_list():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run", side_effect=_completed()) as run:
        installer.uninstall_package("PyQt6-WebEngine extra")
    assert run.call_args.args[0] == [
        sys.executable, "-m", "pip", "uninstall", "-y", "pyqt6-webengine"
    ]


def test_check_installed_reflects_returncode():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run", side_effect=_completed(returncode=0)):
        assert installer.check_installed("numpy") is True
    with mock.patch("core.installer.subprocess.run", side_effect=_completed(returncode=1)):
        assert installer.check_installed("numpy") is False


def test_list_installed_returns_stdout_on_success():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=_completed(stdout="numpy 1.0")):
        ok, out = installer.list_installed()
    assert ok is True
    assert out == "numpy 1.0"


def test_get_python_info_parses_version():
    installer = PackageInstaller()
    with mock.patch("core.installer.subprocess.run",
                    side_effect=_completed(stdout="Python 3.10.5\n")):
        info = installer.get_python_info()
    assert info == {"path": sys.executable, "version": "3.10.5"}
