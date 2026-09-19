"""Tests for core.package_version_manager pure/parsing logic."""

import subprocess
from unittest import mock

from core.package_version_manager import PackageVersionManager


def _run_mock(stdout, returncode=0):
    return mock.patch(
        "core.package_version_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=returncode,
                                                 stdout=stdout, stderr=""),
    )


def test_compare_versions_orders_correctly():
    mgr = PackageVersionManager()
    assert mgr.compare_versions("1.0.0", "2.0.0") == -1
    assert mgr.compare_versions("2.0.0", "1.0.0") == 1
    assert mgr.compare_versions("1.0", "1.0") == 0


def test_compare_versions_invalid_input_returns_zero():
    # Unparseable versions must not raise; current behaviour returns 0.
    assert PackageVersionManager().compare_versions("not-a-version", "1.0") == 0


def test_sort_versions_descending():
    mgr = PackageVersionManager()
    assert mgr.sort_versions(["1.0", "3.0", "2.0"]) == ["3.0", "2.0", "1.0"]


def test_sort_versions_invalid_returns_input_unchanged():
    mgr = PackageVersionManager()
    bad = ["zebra", "apple"]
    assert mgr.sort_versions(bad) == bad


def test_get_available_versions_parses_list():
    out = "numpy (1.26.0)\nAvailable versions: 1.26.0, 1.25.0, 1.24.0\n"
    with _run_mock(out):
        versions, error = PackageVersionManager().get_available_versions("numpy")
    assert error is None
    assert versions == ["1.26.0", "1.25.0", "1.24.0"]


def test_get_available_versions_error_on_failure():
    with _run_mock("", returncode=1):
        versions, error = PackageVersionManager().get_available_versions("nope")
    assert versions == []
    assert error is not None


def test_get_latest_version_returns_first_available():
    with _run_mock("Available versions: 2.0, 1.0, 0.5\n"):
        assert PackageVersionManager().get_latest_version("pkg") == "2.0"


def test_get_installed_version_parses_show_output():
    out = "Name: numpy\nVersion: 1.26.0\nSummary: arrays\n"
    with _run_mock(out):
        assert PackageVersionManager().get_installed_version("numpy") == "1.26.0"


def test_get_installed_version_none_when_absent():
    with _run_mock("", returncode=1):
        assert PackageVersionManager().get_installed_version("nope") is None
