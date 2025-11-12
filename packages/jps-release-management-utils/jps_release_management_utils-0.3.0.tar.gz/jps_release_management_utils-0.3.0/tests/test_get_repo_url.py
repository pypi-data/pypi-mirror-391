import src.jps_release_management_utils.scripts.update_changelog as uc


def test_get_repo_url_converts_ssh_to_https(monkeypatch) -> None:
    """Ensure SSH-style git URLs are converted to HTTPS form.

    Args:
        monkeypatch: pytest fixture to patch functions
    """
    # Simulate git returning an SSH-style URL
    monkeypatch.setattr(
        uc,
        "run_git_command",
        lambda args: "git@github.com:jai-python3/jps-release-management-utils.git",
    )

    result = uc.get_repo_url()
    assert (
        result == "https://github.com/jai-python3/jps-release-management-utils"
    ), f"Expected HTTPS format, got: {result}"


def test_get_repo_url_strips_dot_git_suffix(monkeypatch) -> None:
    """Ensure trailing .git is stripped from the URL.

    Args:
        monkeypatch: pytest fixture to patch functions
    """
    monkeypatch.setattr(
        uc,
        "run_git_command",
        lambda args: "https://github.com/jai-python3/jps-release-management-utils.git",
    )

    result = uc.get_repo_url()
    assert (
        result == "https://github.com/jai-python3/jps-release-management-utils"
    ), f"Expected .git stripped, got: {result}"


def test_get_repo_url_handles_missing_remote(monkeypatch) -> None:
    """If no remote URL is found, should fall back to placeholder.

    Args:
        monkeypatch: pytest fixture to patch functions
    """
    monkeypatch.setattr(uc, "run_git_command", lambda args: "")

    result = uc.get_repo_url()
    assert result == "(unknown repository)", f"Expected fallback placeholder, got: {result}"


def test_get_repo_url_handles_exception(monkeypatch) -> None:
    """If git command fails entirely, should return placeholder.

    Args:
        monkeypatch: pytest fixture to patch functions
    """

    def raise_exception(args):
        raise RuntimeError("git not found")

    monkeypatch.setattr(uc, "run_git_command", raise_exception)

    result = uc.get_repo_url()
    assert result == "(unknown repository)", f"Expected fallback placeholder, got: {result}"
