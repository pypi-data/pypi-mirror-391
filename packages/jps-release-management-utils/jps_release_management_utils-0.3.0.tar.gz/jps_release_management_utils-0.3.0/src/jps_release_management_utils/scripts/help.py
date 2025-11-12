#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
help.py

Lists all available CLI tools in the jps-release-management-utils package
along with their purpose and usage examples.

This script provides a unified help command for developers and release
managers to understand the purpose of each entrypoint utility included
in this package.

Usage:
    jps-release-management-utils-help
"""

import textwrap


def main() -> None:
    """Display help for all entrypoint scripts in this package."""
    help_text = textwrap.dedent(
        """
    🧰 jps-release-management-utils — Available Commands
    ====================================================

    jps-release-management-utils-full-release
        Perform a complete release process:
        - Validates repository state
        - Bumps version (major/minor/patch)
        - Updates CHANGELOG.md
        - Commits, tags, and optionally pushes changes
        Example:
            jps-release-management-utils-full-release --minor

    jps-release-management-utils-update-changelog
        Generates or previews CHANGELOG.md entries based on recent commits.
        Example:
            jps-release-management-utils-update-changelog v1.3.0 --preview

    jps-release-management-utils-release-project
        Handles packaging and version tagging for individual projects.
        Typically invoked by full_release.py.
        Example:
            jps-release-management-utils-release-project v1.3.0

    jps-release-management-utils-help
        Displays this overview of all available commands.

    ----------------------------------------------------
    Tip: Run each command with '--help' to see detailed options.
    """
    )

    print(help_text)


if __name__ == "__main__":
    main()
