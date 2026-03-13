"""
Core modules for cli-anything-godzilla.
"""

from cli_anything.godzilla.core.project import (
    create_project,
    open_project,
    save_project,
    close_project,
    get_project_info,
    list_projects,
    get_current_project,
)
from cli_anything.godzilla.core.shell import (
    ShellEntity,
    add_shell,
    update_shell,
    remove_shell,
    list_shells,
    get_shell,
)
from cli_anything.godzilla.core.profile import (
    C2Profile,
    load_profile,
    validate_profile,
)