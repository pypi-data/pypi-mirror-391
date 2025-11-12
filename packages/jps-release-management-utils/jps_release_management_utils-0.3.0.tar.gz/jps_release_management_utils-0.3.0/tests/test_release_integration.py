#!/usr/bin/env python3
"""
Integration test for the full release_project.py flow (non-dry-run).
Runs in an isolated temporary repo — no network push occurs.
"""

import os
import subprocess


def test_release_integration_local(tmp_path) -> None:
    """Run a full local release and verify commit, tag, and .version update.

    Args:
        tmp_path: pytest fixture providing a temporary directory
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Jaideep Sundaram"], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "config", "user.email", "jai.python3@gmail.com"], cwd=repo_dir, check=True
    )

    # Setup version and dummy file
    version_file = repo_dir / ".version"
    readme_file = repo_dir / "README.md"
    pyproject_file = repo_dir / "pyproject.toml"
    version_file.write_text("1.2.3\n")
    readme_file.write_text("# Dummy Project\n")

    pyproject_file.write_text(
        "[project]\n"
        "name = 'dummy'\n"
        "version = '1.2.3'\n"
    )
    subprocess.run(["git", "add", ".version", "README.md", "pyproject.toml"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    # Add a fake 'origin' to prevent real pushes
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.com/fake.git"], cwd=repo_dir, check=True
    )

    # === PATCH 'git push' WITHOUT POLLUTING REPO ===
    fake_bin_dir = tmp_path / "fake_bin"
    fake_bin_dir.mkdir()
    fake_git = fake_bin_dir / "git"
    fake_git.write_text(
        "#!/bin/bash\n"
        'if echo "$@" | grep -q "push"; then exit 0; fi\n'
        'exec /usr/bin/git "$@"\n'
    )
    fake_git.chmod(0o755)

    # Update PATH: fake git first, then system dirs
    system_path = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    env = {
        "PATH": f"{fake_bin_dir}{os.pathsep}{system_path}",
        "GIT_CONFIG_NOSYSTEM": "1",  # Avoid system gitconfig interference
    }

    result = subprocess.run(
        ["python3", "-m", "jps_release_management_utils.scripts.release_project", "--minor"],
        cwd=repo_dir,
        text=True,
        capture_output=True,
        env=env,
    )

    # === Debug Output ===
    print("=== SCRIPT STDOUT ===\n", result.stdout)
    print("=== SCRIPT STDERR ===\n", result.stderr)
    print("=== ENV PATH ===\n", env["PATH"])

    # === Assertions ===
    assert (
        result.returncode == 0
    ), f"Script failed with code {result.returncode}\nSTDERR: {result.stderr}"

    assert "Bumping version" in result.stdout
    assert "Release complete" in result.stdout

    # Verify .version file updated
    new_version = version_file.read_text().strip()
    assert new_version == "1.3.0", f"Expected 1.3.0, got '{new_version}'"

    # Verify Git tag created
    tags_output = subprocess.run(
        ["git", "tag", "--list"], cwd=repo_dir, capture_output=True, text=True, check=True
    ).stdout
    assert "v1.3.0" in tags_output, f"Tag v1.3.0 not found. Tags:\n{tags_output}"

    # Verify commit message
    log_output = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert "Release v1.3.0" in log_output, f"Expected release commit, got:\n{log_output}"
