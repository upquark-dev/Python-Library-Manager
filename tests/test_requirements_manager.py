"""Tests for core.requirements_manager file parsing/validation (no subprocess)."""

import subprocess
from unittest import mock

from core.requirements_manager import RequirementsManager


def _freeze(stdout, returncode=0):
    return mock.patch(
        "core.requirements_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=returncode,
                                                 stdout=stdout, stderr=""),
    )


def test_parse_requirements_file_handles_mixed_lines(tmp_path):
    req = tmp_path / "req.txt"
    req.write_text("# comment\n\nrequests==2.34.2\nflask>=2.0\nnumpy\n", encoding="utf-8")

    ok, packages = RequirementsManager().parse_requirements_file(str(req))

    assert ok is True
    assert packages == [
        {"name": "requests", "version": "2.34.2", "line": "requests==2.34.2"},
        {"name": "flask", "version": ">=2.0", "line": "flask>=2.0"},
        {"name": "numpy", "version": "any", "line": "numpy"},
    ]


def test_parse_requirements_file_missing_file(tmp_path):
    ok, packages = RequirementsManager().parse_requirements_file(str(tmp_path / "nope.txt"))
    assert ok is False
    assert packages == []


def test_validate_requirements_accepts_pinned_file(tmp_path):
    req = tmp_path / "req.txt"
    req.write_text("requests==2.0\nflask>=1.0\n", encoding="utf-8")

    valid, _msg, errors = RequirementsManager().validate_requirements(str(req))

    assert valid is True
    assert errors == []


def test_validate_requirements_flags_malformed_line(tmp_path):
    req = tmp_path / "req.txt"
    req.write_text("this is not valid\n", encoding="utf-8")

    valid, _msg, errors = RequirementsManager().validate_requirements(str(req))

    assert valid is False
    assert len(errors) == 1
    assert errors[0].startswith("Line 1")


def test_validate_requirements_missing_file(tmp_path):
    valid, msg, errors = RequirementsManager().validate_requirements(str(tmp_path / "nope.txt"))
    assert valid is False
    assert msg == "File not found"
    assert errors == []


def test_export_requirements_with_versions_uses_freeze(tmp_path):
    out_file = tmp_path / "out.txt"
    with _freeze("requests==2.0\nflask==1.0\n") as run:
        ok, _msg = RequirementsManager().export_requirements(str(out_file), include_versions=True)

    assert ok is True
    assert out_file.read_text(encoding="utf-8") == "requests==2.0\nflask==1.0\n"
    assert run.call_args.args[0][-1] == "freeze"


def test_export_requirements_without_versions_strips_versions(tmp_path):
    out_file = tmp_path / "out.txt"
    with _freeze("requests==2.0\nflask==1.0\n") as run:
        ok, _msg = RequirementsManager().export_requirements(str(out_file), include_versions=False)

    assert ok is True
    assert out_file.read_text(encoding="utf-8") == "requests\nflask"
    assert "--format" in run.call_args.args[0]


def test_export_selected_packages_resolves_versions_from_freeze(tmp_path):
    out_file = tmp_path / "sel.txt"
    with _freeze("requests==2.0\nflask==1.0\nnumpy==1.26\n"):
        ok, _msg = RequirementsManager().export_selected_packages(
            str(out_file), ["requests", "MISSING"], include_versions=True)

    assert ok is True
    assert out_file.read_text(encoding="utf-8").split("\n") == ["requests==2.0", "MISSING"]


def test_export_selected_packages_without_versions(tmp_path):
    out_file = tmp_path / "sel.txt"
    ok, _msg = RequirementsManager().export_selected_packages(
        str(out_file), ["a", "b"], include_versions=False)

    assert ok is True
    assert out_file.read_text(encoding="utf-8") == "a\nb"


def test_export_selected_packages_empty_selection(tmp_path):
    ok, msg = RequirementsManager().export_selected_packages(
        str(tmp_path / "e.txt"), [], include_versions=False)

    assert ok is False
    assert msg == "No packages to export"
