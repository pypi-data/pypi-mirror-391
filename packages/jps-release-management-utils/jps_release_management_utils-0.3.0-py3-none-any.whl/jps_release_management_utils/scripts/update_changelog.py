#!/usr/bin/env python3
"""Generates or previews a CHANGELOG.md section for the current version
using git commit history.

Captures only the first line (subject) from each commit message.

Usage:
    python scripts/update_changelog.py <version> [--preview] [--no-wrap]

Additional details:
    - Detects the previous tag to compute the range of commits.
    - Supports colorized terminal preview and Markdown file output.
    - Honors markdownlint MD013 line-length via project config or env var.
"""

import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

# -------------------------------------------------------------
# ANSI color constants (auto-disable if not a TTY)
# -------------------------------------------------------------
ENABLE_COLOR = sys.stdout.isatty()
YELLOW = "\033[1;33m" if ENABLE_COLOR else ""
CYAN = "\033[1;36m" if ENABLE_COLOR else ""
GREEN = "\033[1;32m" if ENABLE_COLOR else ""
RESET = "\033[0m" if ENABLE_COLOR else ""


# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
def detect_markdownlint_line_length() -> int:
    """Detect markdownlint MD013 line-length from .markdownlint.yml or .markdownlint.json.

    Returns:
        int: The maximum line length to use when wrapping markdown lines.
    """
    default_limit = 150
    cwd = Path.cwd()

    # Environment variable override
    env_limit = os.getenv("CHANGELOG_WRAP_LIMIT")
    if env_limit and env_limit.isdigit():
        print(
            f"{CYAN}🧩 Using line length from environment variable CHANGELOG_WRAP_LIMIT={env_limit}{RESET}"
        )
        return int(env_limit)

    # Search for markdownlint configuration files in project root
    yml_path = cwd / ".markdownlint.yml"
    yaml_path = cwd / ".markdownlint.yaml"
    json_path = cwd / ".markdownlint.json"

    try:
        if yml_path.exists() or yaml_path.exists():
            import yaml  # Only used if PyYAML is installed

            config_path = yml_path if yml_path.exists() else yaml_path
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # Possible keys: MD013, "MD013/line-length"
            for key in ("MD013", "MD013/line-length"):
                if key in data and isinstance(data[key], dict):
                    val = data[key].get("line_length") or data[key].get("line-length")
                    if isinstance(val, int):
                        print(f"{CYAN}🧩 Detected markdownlint line length limit: {val}{RESET}")
                        return val
            print(
                f"{YELLOW}⚠️  MD013 line-length not specified — defaulting to {default_limit}{RESET}"
            )
            return default_limit

        elif json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key in ("MD013", "MD013/line-length"):
                if key in data and isinstance(data[key], dict):
                    val = data[key].get("line_length") or data[key].get("line-length")
                    if isinstance(val, int):
                        print(f"{CYAN}🧩 Detected markdownlint line length limit: {val}{RESET}")
                        return val
            print(
                f"{YELLOW}⚠️  MD013 line-length not specified — defaulting to {default_limit}{RESET}"
            )
            return default_limit

        else:
            print(
                f"{YELLOW}⚠️  No .markdownlint configuration found — defaulting to {default_limit}{RESET}"
            )

    except Exception as e:
        print(
            f"{YELLOW}⚠️  Failed to parse markdownlint config ({e}) — defaulting to {default_limit}{RESET}"
        )

    return default_limit


MAX_LINE_LENGTH = detect_markdownlint_line_length()


# -------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------
def run_git_command(args: List[str]) -> str:
    """Execute a git command and return stdout as text.

    Args:
        args (List[str]): Positional arguments for the underlying ``git`` invocation.

    Returns:
        str: The standard output of the git command with trailing whitespace removed.
    """
    result = subprocess.run(
        ["git", "--no-pager", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def get_repo_url() -> str:
    """Return the repository HTTPS URL from git config.

    Returns:
        str: HTTPS-style repository URL (SSH converted) or "(unknown repository)".
    """
    try:
        url = run_git_command(["config", "--get", "remote.origin.url"])
        if not url:
            return "(unknown repository)"
        # Convert SSH form (git@github.com:user/repo.git) → HTTPS
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        if url.endswith(".git"):
            url = url[:-4]
        return url
    except Exception:
        return "(unknown repository)"


def get_previous_tag() -> Optional[str]:
    """Return the previous version tag (before the latest one), or None if not available.

    Returns:
        Optional[str]: The previous semantic version tag (e.g., ``v1.2.2``), or ``None``
            when only one or no version tags exist.
    """
    try:
        # Ensure tags are fetched locally — critical in CI environments or shallow clones
        subprocess.run(
            ["git", "fetch", "--tags", "--force"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Get all tags sorted by creation date (newest first)
        tags_output = run_git_command(["tag", "--sort=-creatordate", "--merged", "HEAD"])
        tags = [t.strip() for t in tags_output.splitlines() if t.strip()]

        # Filter only semantic-style version tags (vX.Y or vX.Y.Z)
        version_tags = [t for t in tags if t.startswith("v")]

        if len(version_tags) >= 2:
            prev_tag = version_tags[1]
            print(f"🏷️  Previous tag detected: {prev_tag}")
            return prev_tag
        elif len(version_tags) == 1:
            print("ℹ️  Only one tag found — treating this as the first release.")
            return None
        else:
            print("⚠️  No version tags found in this repository.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to retrieve previous tag: {e}")
        return None


def get_commits(since_tag: Optional[str] = None) -> List[Dict[str, str]]:
    """Retrieve commit summaries since a given tag (or all commits if no tag).

    Args:
        since_tag (Optional[str]): Tag to use as the lower bound (``<tag>..HEAD``). If ``None``,
            retrieves commits reachable from ``HEAD``.

    Returns:
        List[Dict[str, str]]: A newest-first list of commit dicts with keys ``hash``,
        ``date``, ``author``, and ``subject``.
    """
    fmt = "%h%x1f%ad%x1f%an%x1f%s%x1e"

    # Construct commit range: from tag..HEAD, or entire history if no tag exists
    range_spec = f"{since_tag}..HEAD" if since_tag else "HEAD"

    args = [
        "log",
        range_spec,
        f"--pretty=format:{fmt}",
        "--date=short",
        "--no-color",
    ]
    output = run_git_command(args)
    entries: List[Dict[str, str]] = []

    for raw in output.strip().split("\x1e"):
        if not raw.strip():
            continue
        parts = raw.split("\x1f")
        if len(parts) < 4:
            continue

        short_hash, commit_date, author, subject = parts[:4]
        entries.append(
            {
                "hash": short_hash.strip(),
                "date": commit_date.strip(),
                "author": author.strip(),
                "subject": subject.strip(),
            }
        )

    # 🧠 Explicitly return newest-first (same as git log order)
    # (Reversing is unnecessary unless you're sorting oldest-first)
    return entries


# -------------------------------------------------------------
# Formatting functions
# -------------------------------------------------------------
def wrap_markdown_line(line: str, enable_wrap: bool = True) -> str:
    """Wrap markdown bullet lines to comply with markdownlint MD013.

    Args:
        line (str): The candidate markdown line (expected to start with "- ").
        enable_wrap (bool): If ``True``, wrap to the configured line length.

    Returns:
        str: The wrapped line if applicable, otherwise the original ``line``.
    """
    if not enable_wrap or not line.startswith("- "):
        return line
    return textwrap.fill(
        line,
        width=MAX_LINE_LENGTH,
        subsequent_indent="  ",  # indent wrapped lines under bullet
        replace_whitespace=False,
    )


def format_changelog_entries(
    entries: List[Dict[str, str]],
    repo_url: str,
    color: bool = False,
    enable_wrap: bool = True,
) -> str:
    """Format commit entries into Markdown or colorized terminal output.

    Args:
        entries (List[Dict[str, str]]): Commit dictionaries to render.
        repo_url (str): Base repository URL used to build commit links.
        color (bool): If ``True``, include ANSI color codes for terminal preview.
        enable_wrap (bool): If ``True``, wrap markdown lines to MD013 length.

    Returns:
        str: The formatted list of entries as Markdown or ANSI-colored text.
    """
    lines: List[str] = []
    for e in entries:
        commit_link = f"[({e['hash']})]({repo_url}/commit/{e['hash']})"
        if color:
            # Add ANSI colors for terminal preview only
            lines.append(
                f"- {YELLOW}[{e['date']}] {RESET}"
                f"{GREEN}{e['author']}{RESET} "
                f"{CYAN}{commit_link}{RESET}: {e['subject']}"
            )
        else:
            # Plain Markdown (no ANSI escapes)
            raw_line = f"- [{e['date']}] {e['author']} {commit_link}: {e['subject']}"
            lines.append(wrap_markdown_line(raw_line, enable_wrap=enable_wrap))
    return "\n".join(lines) + "\n"


def build_changelog_section(
    version: str,
    repo_url: str,
    preview: bool = False,
    enable_wrap: bool = True,
) -> str:
    """Generate the full changelog text for the specified release version.

    Args:
        version (str): Release version (e.g., ``v1.2.3``). A leading ``v`` is expected.
        repo_url (str): GitHub repository URL used for commit links.
        preview (bool): If ``True``, indicates that output is for terminal preview.
        enable_wrap (bool): If ``True``, wrap markdown lines according to MD013.

    Returns:
        str: Fully-rendered changelog section, including header and entry list.
    """
    today = date.today().strftime("%Y-%m-%d")
    prev_tag = get_previous_tag()

    # 🧩 Retrieve commits since the previous tag (or all commits if none exist)
    entries = get_commits(prev_tag)

    # 🚫 Abort early if there are no commits since last release
    if not entries:
        print("⚠️  No new commits since last release — skipping changelog update.")
        sys.exit(2)

    # Display mode context
    if preview:
        print("🧾 Previewing changelog entries since last tag...")
    else:
        print("🧾 Updating CHANGELOG.md...")

    # Header section
    if prev_tag:
        header_note = f"- Changes since {prev_tag}\n"
    else:
        header_note = "- Initial release (no previous tags found)\n"

    # Format commit list
    body = format_changelog_entries(entries, repo_url, color=preview, enable_wrap=enable_wrap)

    # Compose full changelog section
    header = f"## [{version}] - {today}\n{header_note}\n"
    section = header + body

    # 🧩 Log summary for traceability
    print(f"✅ Generated changelog section for version {version}")
    print(f"   Commits listed: {len(entries)}")
    if prev_tag:
        print(f"   Based on previous tag: {prev_tag}")
    else:
        print("   No previous tag found (initial release).")

    return section


def prepend_to_file(path: Path, text: str) -> None:
    """Prepend text to a file, preserving a top-level # Changelog heading.

    Args:
        path (Path): Destination changelog file path.
        text (str): The changelog section to prepend.

    Returns:
        None
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Changelog\n\n" + text)
        return

    existing = path.read_text().splitlines()
    if existing and existing[0].startswith("# Changelog"):
        # Insert after the top-level header
        updated = [existing[0], ""] + text.strip().splitlines() + [""] + existing[1:]
        path.write_text("\n".join(updated))
    else:
        # Fallback if no header present
        path.write_text("# Changelog\n\n" + text + "\n" + "\n".join(existing))


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
def main() -> None:
    """Main entry point for changelog updates and previews."""

    args = sys.argv[1:]

    if not args:
        print("❌ Missing version argument.")
        print("Usage: update_changelog.py <version> [--preview] [--no-wrap]")
        sys.exit(1)

    # Detect preview and no-wrap flags, separate version argument
    preview = "--preview" in args
    no_wrap = "--no-wrap" in args
    enable_wrap = not no_wrap

    version_args = [a for a in args if not a.startswith("--")]

    if not version_args:
        print("❌ Missing version argument (expected something like v1.2.3).")
        sys.exit(1)

    raw_version = version_args[0]

    # ✅ Accept "1.2.3" or "v1.2.3" but normalize to "v1.2.3"
    semver_pattern = re.compile(r"^v?\d+\.\d+\.\d+$")
    if not semver_pattern.match(raw_version):
        print(f"❌ Invalid version format: '{raw_version}'")
        print("Expected something like: 1.2.3 or v1.2.3")
        sys.exit(1)

    version = raw_version if raw_version.startswith("v") else f"v{raw_version}"

    repo_url = get_repo_url()

    # Build changelog
    changelog_section = build_changelog_section(
        version, repo_url, preview=preview, enable_wrap=enable_wrap
    )

    if preview:
        print(changelog_section)
        print("✅ Above entries would be added to the next changelog section.")
    else:
        # ✅ Ensure docs/ directory exists before writing CHANGELOG.md
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)

        changelog_path = docs_dir / "CHANGELOG.md"
        prepend_to_file(changelog_path, changelog_section)
        print(f"✅ CHANGELOG updated at {changelog_path}")
        if enable_wrap:
            print(
                f"{CYAN}   Wrapped lines to maximum {MAX_LINE_LENGTH} characters (markdownlint MD013){RESET}"
            )
        else:
            print(f"{YELLOW}⚠️  Wrapping disabled (--no-wrap flag used){RESET}")


if __name__ == "__main__":
    main()
