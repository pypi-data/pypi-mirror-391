#!/usr/bin/env python3
"""
Tests for verifying version bump logic in release_project.py.
"""

import pathlib
import subprocess

import pytest


@pytest.fixture
def repo_with_version(tmp_path) -> pathlib.Path:
    """Create a temporary Git repository with .version file for bump testing.

    Args:
        tmp_path: pytest fixture providing a temporary directory

    Returns:
        Path to the temporary git repository
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Jaideep Sundaram"], cwd=repo_dir)
    subprocess.run(["git", "config", "user.email", "jai.python3@gmail.com"], cwd=repo_dir)

    (repo_dir / ".version").write_text("1.2.3\n")
    (repo_dir / "README.md").write_text("# Dummy Project\n")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)
    subprocess.run(["git", "tag", "v1.2.3"], cwd=repo_dir, check=True)

    return repo_dir


@pytest.mark.parametrize(
    "flag, expected",
    [
        ("--patch", "1.2.4"),
        ("--minor", "1.3.0"),
        ("--major", "2.0.0"),
    ],
)
def test_release_version_bump_flags(repo_with_version, flag, expected) -> None:
    """Validate that --patch, --minor, and --major flags bump correctly.

    Args:
        repo_with_version: pytest fixture providing a temp repo with .version
        flag: The version bump flag to test
        expected: The expected resulting version string
    """
    result = subprocess.run(
        [
            "python3",
            "-m",
            "jps_release_management_utils.scripts.release_project",
            flag,
            "--dry-run",
        ],
        cwd=repo_with_version,
        text=True,
        capture_output=True,
    )

    # Basic assertions
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout or "🧪" in result.stdout
    assert f"1.2.3 → {expected}" in result.stdout, f"Expected version bump to {expected} not found"
