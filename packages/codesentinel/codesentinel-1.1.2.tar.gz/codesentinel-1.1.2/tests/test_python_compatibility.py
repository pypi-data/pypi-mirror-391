"""Tests ensuring packaging metadata matches declared Python support policy."""

import re
from pathlib import Path

EXPECTED_PYTHON_REQUIREMENT = ">=3.8"
EXPECTED_CLASSIFIERS = {
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
}


def _read_file(relative_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / relative_path).read_text(encoding="utf-8")


def _extract_python_requires(text: str) -> str:
    match = re.search(r"python_requires\s*=\s*\"([^\"]+)\"", text)
    return match.group(1) if match else ""


def _extract_requires_python(text: str) -> str:
    match = re.search(r"requires-python\s*=\s*\"([^\"]+)\"", text)
    return match.group(1) if match else ""


def _extract_classifiers(text: str) -> set:
    classifiers = set(re.findall(r"Programming Language :: Python :: ([0-9.]+)", text))
    return classifiers


def test_pyproject_python_requirement_matches_policy():
    """pyproject.toml must advertise the correct Python compatibility policy."""
    pyproject = _read_file("pyproject.toml")
    requires_python = _extract_requires_python(pyproject)
    assert requires_python == EXPECTED_PYTHON_REQUIREMENT, (
        "pyproject.toml requires-python mismatch"
    )

    classifiers = _extract_classifiers(pyproject)
    for version in EXPECTED_CLASSIFIERS:
        assert version in classifiers, f"Missing classifier for Python {version} in pyproject.toml"


def test_setup_python_requirement_matches_policy():
    """setup.py must stay in sync with official Python compatibility."""
    setup_text = _read_file("setup.py")
    python_requires = _extract_python_requires(setup_text)
    assert python_requires == EXPECTED_PYTHON_REQUIREMENT, (
        "setup.py python_requires mismatch"
    )

    classifiers = _extract_classifiers(setup_text)
    for version in EXPECTED_CLASSIFIERS:
        assert version in classifiers, f"Missing classifier for Python {version} in setup.py"
