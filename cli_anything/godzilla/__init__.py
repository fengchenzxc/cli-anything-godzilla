"""
cli-anything-godzilla: CLI harness for Godzilla WebShell Manager.

This package provides a stateful CLI interface to the Godzilla security testing tool.
"""

__version__ = "1.0.0"
__author__ = "cli-anything"

from cli_anything.godzilla.core.project import (
    create_project,
    open_project,
    save_project,
    close_project,
    get_project_info,
    list_projects,
)
from cli_anything.godzilla.core.shell import (
    ShellEntity,
    add_shell,
    update_shell,
    remove_shell,
    list_shells,
    get_shell,
    test_shell,
)
from cli_anything.godzilla.core.profile import (
    C2Profile,
    load_profile,
    save_profile,
    list_profiles,
    validate_profile,
)

__all__ = [
    # Project management
    "create_project",
    "open_project",
    "save_project",
    "close_project",
    "get_project_info",
    "list_projects",
    # Shell management
    "ShellEntity",
    "add_shell",
    "update_shell",
    "remove_shell",
    "list_shells",
    "get_shell",
    "test_shell",
    # Profile management
    "C2Profile",
    "load_profile",
    "save_profile",
    "list_profiles",
    "validate_profile",
]
