"""
Project management module for cli-anything-godzilla.

Provides project creation, opening, saving, and management operations.
A project represents a complete Godzilla workspace with its own database and configuration.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from cli_anything.godzilla.core.database import GodzillaDatabase


# Default project directory
DEFAULT_PROJECT_DIR = Path.home() / ".godzilla_cli"


class Project:
    """Represents a Godzilla CLI project."""

    def __init__(self, project_path: str):
        """Initialize a project.

        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "project.json"
        self.db_path = self.project_path / "data.db"
        self.config: Dict[str, Any] = {}
        self.db: Optional[GodzillaDatabase] = None
        self._modified = False

    def create(self, name: str = "Untitled", description: str = "") -> None:
        """Create a new project structure.

        Args:
            name: Project name
            description: Project description
        """
        # Create project directory
        self.project_path.mkdir(parents=True, exist_ok=True)

        # Create profiles directory
        (self.project_path / "profile").mkdir(exist_ok=True)

        # Create default configuration
        self.config = {
            "name": name,
            "description": description,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "default_payload": "JavaDynamicPayload",
            "default_cryption": "xor",
            "default_encoding": "UTF-8",
        }

        # Save configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        # Initialize database
        self.db = GodzillaDatabase(str(self.db_path))

    def open(self) -> bool:
        """Open an existing project.

        Returns:
            True if project was opened successfully
        """
        # Check if project path exists
        if not self.project_path.exists():
            return False

        # If config doesn't exist but database does, create default config
        # This allows opening original Godzilla projects
        if not self.config_path.exists():
            if self.db_path.exists():
                # Create default config for existing Godzilla project
                self.config = {
                    "name": self.project_path.name,
                    "description": "Imported Godzilla project",
                    "version": "1.0.0",
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "default_payload": "JavaDynamicPayload",
                    "default_cryption": "xor",
                    "default_encoding": "UTF-8",
                }
                # Save the config for future use
                self.project_path.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                return False
        else:
            # Load configuration
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

        # Open database
        self.db = GodzillaDatabase(str(self.db_path))
        return True

    def save(self) -> None:
        """Save project configuration."""
        self.config["modified"] = datetime.now().isoformat()
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        self._modified = False

    def close(self) -> None:
        """Close the project."""
        if self.db:
            self.db.close()
            self.db = None

    def get_info(self) -> Dict[str, Any]:
        """Get project information.

        Returns:
            Dictionary containing project metadata
        """
        return {
            "name": self.config.get("name", "Untitled"),
            "description": self.config.get("description", ""),
            "version": self.config.get("version", "1.0.0"),
            "path": str(self.project_path),
            "created": self.config.get("created", ""),
            "modified": self.config.get("modified", ""),
            "shell_count": len(self.db.list_shells()) if self.db else 0,
            "group_count": len(self.db.list_groups()) if self.db else 0,
        }

    @property
    def name(self) -> str:
        """Get project name."""
        return self.config.get("name", "Untitled")

    @property
    def is_open(self) -> bool:
        """Check if project is open."""
        return self.db is not None

    @property
    def is_modified(self) -> bool:
        """Check if project has unsaved changes."""
        return self._modified

    def mark_modified(self) -> None:
        """Mark project as having unsaved changes."""
        self._modified = True


# Global project registry
_current_project: Optional[Project] = None


def create_project(name: str, path: Optional[str] = None, description: str = "") -> Project:
    """Create a new Godzilla CLI project.

    Args:
        name: Project name
        path: Optional path for the project (defaults to ~/.godzilla_cli/<name>)
        description: Project description

    Returns:
        The created Project instance
    """
    global _current_project

    # Determine project path
    if path:
        project_path = Path(path)
    else:
        DEFAULT_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        project_path = DEFAULT_PROJECT_DIR / name

    # Create project
    project = Project(str(project_path))
    project.create(name=name, description=description)

    # Set as current project
    _current_project = project

    return project


def open_project(path: str) -> Project:
    """Open an existing Godzilla CLI project.

    Args:
        path: Path to the project directory

    Returns:
        The opened Project instance

    Raises:
        FileNotFoundError: If project doesn't exist
    """
    global _current_project

    project = Project(path)

    if not project.open():
        raise FileNotFoundError(f"Project not found: {path}")

    _current_project = project
    return project


def save_project(project: Optional[Project] = None) -> bool:
    """Save project configuration.

    Args:
        project: Project to save (defaults to current project)

    Returns:
        True if save was successful
    """
    global _current_project

    proj = project or _current_project
    if not proj:
        return False

    proj.save()
    return True


def close_project(project: Optional[Project] = None) -> bool:
    """Close a project.

    Args:
        project: Project to close (defaults to current project)

    Returns:
        True if close was successful
    """
    global _current_project

    proj = project or _current_project
    if not proj:
        return False

    proj.close()

    if proj == _current_project:
        _current_project = None

    return True


def get_project_info(project: Optional[Project] = None) -> Dict[str, Any]:
    """Get project information.

    Args:
        project: Project to get info for (defaults to current project)

    Returns:
        Dictionary containing project information
    """
    global _current_project

    proj = project or _current_project
    if not proj:
        return {"error": "No project open"}

    return proj.get_info()


def list_projects() -> List[Dict[str, Any]]:
    """List all projects in the default project directory.

    Returns:
        List of project information dictionaries
    """
    projects = []

    if not DEFAULT_PROJECT_DIR.exists():
        return projects

    for item in DEFAULT_PROJECT_DIR.iterdir():
        if item.is_dir():
            config_file = item / "project.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    projects.append({
                        "name": config.get("name", item.name),
                        "path": str(item),
                        "description": config.get("description", ""),
                        "created": config.get("created", ""),
                    })
                except (json.JSONDecodeError, IOError):
                    continue

    return projects


def get_current_project() -> Optional[Project]:
    """Get the currently active project.

    Returns:
        Current Project instance or None
    """
    return _current_project
