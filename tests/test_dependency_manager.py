"""Tests for core.dependency_manager parsing and tree building."""

import subprocess
from unittest import mock

from core.dependency_manager import DependencyManager


def _show(stdout, returncode=0):
    return mock.patch(
        "core.dependency_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=returncode,
                                                 stdout=stdout, stderr=""),
    )


def test_get_package_dependencies_parses_requires_line():
    with _show("Name: flask\nRequires: click, jinja2\nRequired-by: \n"):
        deps, error = DependencyManager().get_package_dependencies("flask")
    assert error is None
    assert deps == ["click", "jinja2"]


def test_get_package_dependencies_empty_requires():
    with _show("Name: leaf\nRequires:\n"):
        deps, error = DependencyManager().get_package_dependencies("leaf")
    assert error is None
    assert deps == []


def test_get_package_dependencies_not_installed():
    with _show("", returncode=1):
        deps, error = DependencyManager().get_package_dependencies("nope")
    assert deps is None
    assert error == "Package not installed"


def test_get_reverse_dependencies_parses_required_by():
    with _show("Required-by: app1, app2\n"):
        rev, error = DependencyManager().get_reverse_dependencies("click")
    assert error is None
    assert rev == ["app1", "app2"]


def test_build_dependency_tree_structure():
    mgr = DependencyManager()
    graph = {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}
    with mock.patch.object(mgr, "get_package_dependencies",
                           side_effect=lambda p: (graph.get(p, []), None)):
        tree = mgr.build_dependency_tree("a", max_depth=3)

    assert tree["name"] == "a"
    assert tree["depth"] == 0
    assert {child["name"] for child in tree["dependencies"]} == {"b", "c"}
    b = next(child for child in tree["dependencies"] if child["name"] == "b")
    assert [grand["name"] for grand in b["dependencies"]] == ["d"]


def test_build_dependency_tree_respects_max_depth():
    mgr = DependencyManager()
    graph = {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}
    with mock.patch.object(mgr, "get_package_dependencies",
                           side_effect=lambda p: (graph.get(p, []), None)):
        tree = mgr.build_dependency_tree("a", max_depth=1)

    assert tree["name"] == "a"
    assert tree["dependencies"] == []


def test_build_dependency_tree_does_not_revisit_cycles():
    mgr = DependencyManager()
    graph = {"a": ["b"], "b": ["a"]}
    with mock.patch.object(mgr, "get_package_dependencies",
                           side_effect=lambda p: (graph.get(p, []), None)):
        tree = mgr.build_dependency_tree("a", max_depth=5)

    # 'a' -> 'b' -> ('a' already visited, skipped); no infinite recursion.
    assert tree["name"] == "a"
    assert [child["name"] for child in tree["dependencies"]] == ["b"]
    b = tree["dependencies"][0]
    assert b["dependencies"] == []


def test_get_package_info_summary_parses_all_fields():
    with _show("Name: flask\nVersion: 2.0\nRequires: click\n"):
        info = DependencyManager().get_package_info_summary("flask")
    assert info == {"Name": "flask", "Version": "2.0", "Requires": "click"}


def test_get_package_info_summary_none_when_absent():
    with _show("", returncode=1):
        assert DependencyManager().get_package_info_summary("nope") is None


def test_find_circular_dependencies_detects_cycle():
    mgr = DependencyManager()
    graph = {"a": ["b"], "b": ["a"]}
    with mock.patch.object(mgr, "get_package_dependencies",
                           side_effect=lambda p: (graph.get(p, []), None)):
        cycles = mgr.find_circular_dependencies("a")

    assert cycles
    flat = [pkg for cycle in cycles for pkg in cycle]
    assert "a" in flat and "b" in flat


def test_find_circular_dependencies_empty_when_acyclic():
    mgr = DependencyManager()
    graph = {"a": ["b"], "b": ["c"], "c": []}
    with mock.patch.object(mgr, "get_package_dependencies",
                           side_effect=lambda p: (graph.get(p, []), None)):
        assert mgr.find_circular_dependencies("a") == []
