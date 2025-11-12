#!/usr/bin/env python3
"""Full release orchestration utility for the jps-release-management-utils package.


This module automates the end-to-end release workflow for Python projects,
replacing legacy Makefile-based steps with a streamlined, script-driven process.


The release process includes:
1. Repository validation to ensure a clean working state.
2. Semantic version bumping (patch, minor, or major).
3. Automatic changelog update based on recent commits.
4. Git commit and annotated tag creation for the new version.
5. Optional push of commits and tags to the remote origin.
6. Final release summary with CI/CD workflow URL for verification.


This script is designed to be executed from the command line and can operate in
both dry-run and full-release modes. It is invoked as part of a coordinated
release management suite that includes `release_project.py` and
`update_changelog.py`.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------
def run(cmd, cwd=None, capture=False, quiet=False, check=True):
    """Run shell command with pretty output and error handling.

    Args:
        cmd (list[str]): Command and its arguments to execute.
        cwd (Path | None): Working directory in which to run the command.
        capture (bool): Whether to capture and return command output.
        quiet (bool): Whether to suppress printed command output.
        check (bool): Whether to exit if the command returns a non-zero status.

    Returns:
        subprocess.CompletedProcess: The completed process object.
    """
    display = " ".join(cmd)
    if not quiet:
        print(f"👉 {display}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=capture,
    )
    if check and result.returncode != 0:
        print(f"❌ Command failed: {display}")
        if result.stderr:
            print(result.stderr.strip())
        sys.exit(result.returncode)
    return result


def read_version_file(repo_root):
    """Return current version from .version file.

    Args:
        repo_root (Path): Path to the repository root containing the .version file.

    Returns:
        str: The version string read from the .version file.
    """
    version_file = repo_root / ".version"
    if not version_file.exists():
        print("❌ .version file missing.")
        sys.exit(1)
    return version_file.read_text().strip()


def find_repo_root(start: Path = Path(__file__).resolve()) -> Path:
    """Walk upward until .git or pyproject.toml is found.

    Args:
        start (Path): Starting path to search upward from.

    Returns:
        Path: Path to the repository root directory.
    """
    for parent in [start, *start.parents]:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    print("❌ Unable to locate repository root.")
    sys.exit(1)


# -----------------------------------------------------------------------------
# Main release orchestration
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Perform a full software release workflow.")
    parser.add_argument(
        "--part",
        required=True,
        choices=["patch", "minor", "major"],
        help="Version part to bump.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the release process without making permanent changes.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Perform all steps locally but skip git push operations.",
    )

    args = parser.parse_args()
    repo_root = find_repo_root()

    # ✅ Determine actual script directory (inside src/.../scripts)
    script_dir = Path(__file__).resolve().parent
    release_script = script_dir / "release_project.py"
    changelog_script = script_dir / "update_changelog.py"

    print("🚀 Starting full release orchestration...\n")

    # -------------------------------------------------------------------------
    # 1️⃣ Verify repo cleanliness (reuse logic from release_project.py)
    # -------------------------------------------------------------------------
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print("❌ Working directory not clean. Commit or stash changes before releasing.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 2️⃣ Perform version bump (dry-run or real)
    # -------------------------------------------------------------------------
    cmd = ["python3", str(release_script), f"--{args.part}"]
    if args.dry_run:
        cmd.append("--dry-run")
    run(cmd, cwd=repo_root)

    if args.dry_run:
        print("\n🧪 Dry-run complete. Skipping changelog and commit steps.\n")
        sys.exit(0)

    # -------------------------------------------------------------------------
    # 3️⃣ Read bumped version
    # -------------------------------------------------------------------------
    new_version = read_version_file(repo_root)
    print(f"\n🔢 New version detected: {new_version}")

    # -------------------------------------------------------------------------
    # 4️⃣ Update changelog
    # -------------------------------------------------------------------------
    print("🗒️  Updating CHANGELOG.md...")
    chg = subprocess.run(
        ["python3", str(changelog_script), new_version],
        cwd=repo_root,
        text=True,
    )

    if chg.returncode == 2:
        # update_changelog.py uses exit code 2 for "no new commits since last release"
        print("ℹ️ No new commits since last release — skipping commit, tag, and push.")
        sys.exit(0)
    elif chg.returncode != 0:
        print("❌ Changelog update failed.")
        if chg.stderr:
            print(chg.stderr.strip())
        sys.exit(chg.returncode)

    # -------------------------------------------------------------------------
    # 5️⃣ Commit + tag
    # -------------------------------------------------------------------------
    print("\n📦 Committing and tagging release...")
    run(["git", "add", ".version", "docs/CHANGELOG.md", "pyproject.toml"], cwd=repo_root)

    # Try initial commit, capture possible markdownlint modification
    result = subprocess.run(
        ["git", "commit", "-m", f"Release v{new_version}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0 and "files were modified" in (result.stdout + result.stderr):
        print("⚙️  Detected markdownlint auto-fix — re-staging files and retrying commit...")
        subprocess.run(["git", "add", "docs/CHANGELOG.md"], cwd=repo_root, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Release v{new_version}"],
            cwd=repo_root,
            check=True,
        )
    elif result.returncode != 0:
        print(f"❌ Command failed: git commit\n{result.stdout}\n{result.stderr}")
        sys.exit(result.returncode)

    # -------------------------------------------------------------------------
    # 6️⃣ Push (optional)
    # -------------------------------------------------------------------------
    if args.no_push:
        print("🚫 Skipping push (local-only release).")
    else:
        print("\n🚀 Pushing commits and tags to origin...")
        run(["git", "push", "origin", "main"], cwd=repo_root)
        run(["git", "push", "origin", f"v{new_version}"], cwd=repo_root)

    # -------------------------------------------------------------------------
    # 7️⃣ Final summary
    # -------------------------------------------------------------------------
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
    )
    remote_url = result.stdout.strip()

    org = None
    repo_name = None

    if remote_url:
        match = re.search(r"github\\.com[:/](?P<org>[^/]+)/(?P<repo>[^/.]+)", remote_url)
        if match:
            org = match.group("org")
            repo_name = match.group("repo")

    if not org:
        org = "unknown-org"
    if not repo_name:
        repo_name = Path(repo_root).name

    print("\n✅ Release workflow complete!")
    print(f"   Version: v{new_version}")
    print(
        f"   CI workflow: https://github.com/{org}/{repo_name}/actions/workflows/publish-to-pypi.yml\n"  # noqa: E501
    )


if __name__ == "__main__":
    main()
