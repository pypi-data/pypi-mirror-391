#!/usr/bin/env python3
"""
release_project.py

Automates semantic version bumping, tagging, and pushing to GitHub for Python projects.
This script is part of the jps-release-management-utils suite and serves as the
core component for managing consistent versioning across repositories.

It performs the following actions:
    1. Validates that the working directory is clean.
    2. Detects the current version from `.version` or `pyproject.toml`.
    3. Bumps the version (major, minor, or patch).
    4. Writes the new version to `.version`.
    5. Creates a Git commit and annotated tag.
    6. Pushes both the commit and tag to the remote repository.

Supports dry-run mode and simple shorthand flags like --minor, --patch, and --major.

Usage:
    python3 scripts/release_project.py --minor [--dry-run]
    python3 scripts/release_project.py --part minor [--dry-run]
"""

import argparse
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path


def update_version_in_dot_version(new_version: str) -> bool:
    """Update the .version file with the new version.

    Args:
        new_version (str): The new version string to write.

    Returns:
        bool: True if the version was updated, False otherwise.
    """
    version_path = Path(".version")
    if not version_path.exists():
        print("⚠️  .version file not found — skipping version update in this file.")
        return False

    try:
        version_path.write_text(new_version + "\n")
        return True
    except OSError as e:
        print(f"❌ Failed to update .version: {e}")
        return False


def update_version_in_pyproject_toml(new_version: str) -> bool:
    """Update the version in pyproject.toml if it exists.

    Args:
        new_version (str): The new version string to write.

    Returns:
        bool: True if the version was updated, False otherwise.
    """
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("⚠️  pyproject.toml not found — skipping version update in this file.")
        return False

    lines = pyproject_path.read_text().splitlines()
    updated_lines = []
    updated = False
    in_project_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            # Detect when we enter or leave [project]
            in_project_section = stripped == "[project]"
        elif in_project_section and stripped.startswith("version"):
            line = f'version = "{new_version}"'
            updated = True
        updated_lines.append(line)

    if not updated:
        print("⚠️  No version line found under [project] section.")
        return False

    try:
        pyproject_path.write_text("\n".join(updated_lines) + "\n")
        return True
    except OSError as e:
        print(f"❌ Failed to update pyproject.toml: {e}")
        return False


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> str:
    """Run a shell command and return its stdout text.

    Args:
        cmd (list[str]): The command and its arguments to execute.
        cwd (Path | None): The working directory where the command is executed.
        check (bool): Whether to raise an error and exit if the command fails.

    Returns:
        str: The captured stdout output from the executed command.
    """
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()


def is_dirty_repo() -> bool:
    """Check if the git working directory has uncommitted changes.

    Returns:
        bool: True if there are uncommitted changes, False otherwise.
    """
    result = run(["git", "status", "--porcelain"], check=False)
    return bool(result)


def get_current_version() -> str:
    """Retrieve the current project version from .version or pyproject.toml.

    Returns:
        str: The current semantic version string.
    """
    if Path(".version").exists():
        return Path(".version").read_text().strip()
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        version = data.get("project", {}).get("version")
        if version:
            return version
    print("❌ Unable to find current version in .version or pyproject.toml")
    sys.exit(1)


def bump_version(version: str, part: str) -> str:
    """Return the next semantic version string.

    Args:
        version (str): The current semantic version string.
        part (str): The version component to bump (major, minor, or patch).

    Returns:
        str: The next semantic version string after the bump.
    """
    major, minor, patch = [int(x) for x in version.split(".")]
    if part == "major":
        major += 1
        minor = patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        print(f"❌ Unknown part: {part}")
        sys.exit(1)
    return f"{major}.{minor}.{patch}"


def tag_exists(tag: str) -> bool:
    """Check if a git tag already exists.

    Args:
        tag (str): The tag name to check.

    Returns:
        bool: True if the tag exists, False otherwise.
    """
    result = subprocess.run(["git", "rev-parse", tag], capture_output=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Automate software release management.")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--part", choices=["patch", "minor", "major"], help="Version part to bump")
    group.add_argument("--patch", action="store_true", help="Bump patch version (x.y.Z)")
    group.add_argument("--minor", action="store_true", help="Bump minor version (x.Y.0)")
    group.add_argument("--major", action="store_true", help="Bump major version (X.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate release without changes")
    args = parser.parse_args()

    # Derive part argument if shorthand flag used
    part = args.part or (
        "patch" if args.patch else "minor" if args.minor else "major" if args.major else None
    )
    if not part:
        print("❌ You must specify one of --part, --patch, --minor, or --major.")
        parser.print_help()
        sys.exit(2)

    if is_dirty_repo():
        print("❌ Working directory not clean. Commit or stash changes before releasing.")
        sys.exit(1)

    current_version = get_current_version()
    new_version = bump_version(current_version, part)
    today = date.today().isoformat()

    print(f"🔢 Bumping version: {current_version} → {new_version}")
    if args.dry_run:
        print("🧪 [DRY RUN] Skipping commit, tag, push, and changelog update.")
        sys.exit(0)

    if tag_exists(f"v{new_version}"):
        print(f"⚠️  Tag v{new_version} already exists — aborting release.")
        sys.exit(1)

    dot_version_ok = update_version_in_dot_version(new_version)
    pyproject_ok = update_version_in_pyproject_toml(new_version)

    if dot_version_ok and pyproject_ok:
        print("✅ Updated versions in .version and pyproject.toml.")
    elif dot_version_ok:
        print("✅ Updated .version (pyproject.toml skipped).")
    elif pyproject_ok:
        print("✅ Updated pyproject.toml (no .version file found).")
    else:
        print("⚠️  No version files updated.")

    # Commit, tag, and push
    run(["git", "add", ".version", "pyproject.toml"])
    run(["git", "commit", "-m", f"Release v{new_version}"])
    run(
        [
            "git",
            "tag",
            "-a",
            f"v{new_version}",
            "-m",
            f"Release v{new_version}\n\nReleased on {today}",
        ]
    )
    run(["git", "push", "origin", "main"])
    run(["git", "push", "origin", f"v{new_version}"])

    print("✅ Release complete.")
    print(f"📦 Version: v{new_version}")
    print(f"📅 Date: {today}")
    print("🚀 Tag pushed to GitHub.")


if __name__ == "__main__":
    main()
