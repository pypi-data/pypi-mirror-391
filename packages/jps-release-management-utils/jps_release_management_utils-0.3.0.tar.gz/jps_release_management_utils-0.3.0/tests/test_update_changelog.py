import subprocess


def test_update_changelog_preview(temp_repo) -> None:
    """Ensures preview mode runs and includes expected output.

    Args:
        temp_repo: pytest fixture providing a temporary git repo
    """
    result = subprocess.run(
        [
            "python3",
            "-m",
            "jps_release_management_utils.scripts.update_changelog",
            "1.1.0",
            "--preview",
        ],
        cwd=temp_repo,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "✅ Above entries would be added" in result.stdout
    assert "1.1.0" in result.stdout


def test_update_changelog_creates_file(temp_repo) -> None:
    """Ensures full update writes CHANGELOG.md content.

    Args:
        temp_repo: pytest fixture providing a temporary git repo
    """
    # Ensure docs/ exists in the temporary repository
    (temp_repo / "docs").mkdir(exist_ok=True)

    # Run update_changelog.py WITHOUT --preview so it writes the file
    result = subprocess.run(
        [
            "python3",
            "-m",
            "jps_release_management_utils.scripts.update_changelog",
            "1.1.0",
        ],
        cwd=temp_repo,
        text=True,
        capture_output=True,
        check=True,
    )

    # Ensure the changelog file exists
    changelog = temp_repo / "docs" / "CHANGELOG.md"
    assert changelog.exists(), "CHANGELOG.md was not created in docs/"

    # Validate changelog contents
    content = changelog.read_text()
    assert "1.1.0" in content, "Version header missing in changelog"
    assert "CHANGELOG updated" in result.stdout or "✅" in result.stdout
