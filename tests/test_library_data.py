"""Tests for the core.library_data package database contract."""

from core.library_data import LIBRARY_CATEGORIES

REQUIRED_KEYS = {"name", "description", "install_cmd"}


def test_categories_is_non_empty_dict():
    assert isinstance(LIBRARY_CATEGORIES, dict)
    assert LIBRARY_CATEGORIES


def test_every_category_is_non_empty_list_of_dicts():
    for category, packages in LIBRARY_CATEGORIES.items():
        assert isinstance(category, str) and category.strip()
        assert isinstance(packages, list) and packages, f"category {category!r} is empty"
        for pkg in packages:
            assert isinstance(pkg, dict), f"{category}: {pkg!r} is not a dict"


def test_every_package_has_required_non_empty_string_fields():
    for category, packages in LIBRARY_CATEGORIES.items():
        for pkg in packages:
            missing = REQUIRED_KEYS - pkg.keys()
            assert not missing, f"{category}/{pkg.get('name')!r} missing {missing}"
            for key in REQUIRED_KEYS:
                value = pkg[key]
                assert isinstance(value, str) and value.strip(), \
                    f"{category}/{pkg.get('name')!r} has bad {key!r}"


def test_install_commands_use_pip_install_prefix():
    for packages in LIBRARY_CATEGORIES.values():
        for pkg in packages:
            assert pkg["install_cmd"].startswith("pip install "), \
                f"{pkg['name']!r}: {pkg['install_cmd']!r}"


def test_package_names_have_no_surrounding_whitespace():
    for packages in LIBRARY_CATEGORIES.values():
        for pkg in packages:
            assert pkg["name"] == pkg["name"].strip()
