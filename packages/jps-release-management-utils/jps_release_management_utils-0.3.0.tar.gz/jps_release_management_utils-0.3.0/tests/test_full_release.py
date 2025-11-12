import os
import subprocess
import sys

import pytest

import jps_release_management_utils.scripts.full_release as full_release


def test_full_release_dry_run(monkeypatch, dummy_repo, capsys) -> None:
    """Dry run should skip commit and tagging steps.

    Args:
        monkeypatch: pytest fixture to patch functions
        dummy_repo: pytest fixture providing a temporary git repo
        capsys: pytest fixture to capture stdout/stderr
    """
    _real_run = subprocess.run  # preserve the real run()

    def fake_run(cmd, **kwargs):
        cwd = kwargs.get("cwd")
        if cwd:
            os.chdir(cwd)

        # Only fake out git commands — let others run normally
        if isinstance(cmd, (list, tuple)) and "git" in cmd:
            if "status" in cmd:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # For non-git subprocess calls, use the real run()
        return _real_run(cmd, **kwargs)

    # Patch subprocess and Path
    monkeypatch.setattr(full_release.subprocess, "run", fake_run)
    monkeypatch.setattr(
        full_release.Path, "resolve", lambda p=None: dummy_repo / "scripts" / "full_release.py"
    )

    os.chdir(dummy_repo)

    sys.argv = ["full_release.py", "--part", "minor", "--dry-run"]
    try:
        full_release.main()
    except SystemExit:
        pass

    out, err = capsys.readouterr()
    assert "Dry-run complete" in out or "🧪" in out


def test_full_release_blocks_dirty_repo(monkeypatch, dummy_repo, capsys) -> None:
    """Should abort if working directory is not clean.

    Args:
        monkeypatch: pytest fixture to patch functions
        dummy_repo: pytest fixture providing a temporary git repo
        capsys: pytest fixture to capture stdout/stderr
    """

    def fake_run(cmd, **kwargs):
        cwd = kwargs.get("cwd")
        if cwd:
            os.chdir(cwd)

        if "git" in cmd and "status" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="M Makefile\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(full_release.subprocess, "run", fake_run)
    monkeypatch.setattr(
        full_release.Path, "resolve", lambda p=None: dummy_repo / "scripts" / "full_release.py"
    )

    os.chdir(dummy_repo)

    sys.argv = ["full_release.py", "--part", "minor"]
    with pytest.raises(SystemExit):
        full_release.main()

    out, err = capsys.readouterr()
    assert "not clean" in out or "❌" in out


def test_full_release_local_success(monkeypatch, dummy_repo, capsys) -> None:
    """Successful release with --no-push should run expected commands.

    Args:
        monkeypatch: pytest fixture to patch functions
        dummy_repo: pytest fixture providing a temporary git repo
        capsys: pytest fixture to capture stdout/stderr
    """
    _real_run = subprocess.run  # preserve the real run()

    def fake_run(cmd, **kwargs):
        cwd = kwargs.get("cwd")
        if cwd:
            os.chdir(cwd)

        # Fake only git commands
        if isinstance(cmd, (list, tuple)) and "git" in cmd:
            if "status" in cmd:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # Run real subprocesses (release_project.py, update_changelog.py, etc.)
        return _real_run(cmd, **kwargs)

    monkeypatch.setattr(full_release.subprocess, "run", fake_run)
    monkeypatch.setattr(
        full_release.Path, "resolve", lambda p=None: dummy_repo / "scripts" / "full_release.py"
    )

    # force repo root resolution to the dummy repo
    monkeypatch.setattr(full_release, "find_repo_root", lambda: dummy_repo)

    (dummy_repo / ".version").write_text("1.3.0\n")

    os.chdir(dummy_repo)

    sys.argv = ["full_release.py", "--part", "minor", "--no-push"]
    try:
        full_release.main()
    except SystemExit:
        pass

    out, err = capsys.readouterr()
    assert "Skipping push" in out or "🚫" in out


def test_full_release_missing_version_file(monkeypatch, dummy_repo, capsys) -> None:
    """If .version is missing, full release should still succeed since release_project regenerates it.

    Args:
        monkeypatch: pytest fixture to patch functions
        dummy_repo: pytest fixture providing a temporary git repo
        capsys: pytest fixture to capture stdout/stderr
    """
    (dummy_repo / ".version").unlink()

    # Preserve the real subprocess.run
    real_run = subprocess.run

    def fake_run(cmd, **kwargs):
        cwd = kwargs.get("cwd")
        if cwd:
            os.chdir(cwd)

        # Only fake git commands
        if isinstance(cmd, (list, tuple)) and "git" in cmd:
            if "status" in cmd:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # Allow stubbed Python scripts to run normally using the real subprocess.run
        return real_run(cmd, **kwargs)

    monkeypatch.setattr(full_release.subprocess, "run", fake_run)
    monkeypatch.setattr(
        full_release.Path, "resolve", lambda p=None: dummy_repo / "scripts" / "full_release.py"
    )

    os.chdir(dummy_repo)
    sys.argv = ["full_release.py", "--part", "minor"]

    try:
        full_release.main()
    except SystemExit:
        pytest.fail("SystemExit should not be raised — release_project regenerates .version")

    out, _ = capsys.readouterr()
    assert "Release workflow complete" in out or "✅" in out
    assert (
        dummy_repo / ".version"
    ).exists(), "Expected .version to be regenerated by release_project"
