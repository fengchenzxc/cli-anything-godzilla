"""
E2E tests for cli-anything-godzilla.

Tests full workflow with real files and database operations.
"""

import os
import json
import pytest
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

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
    add_shell,
    update_shell,
    remove_shell,
    list_shells,
    get_shell,
    export_shells,
    import_shells,
    ShellEntity,
)
from cli_anything.godzilla.core.profile import (
    load_profile,
    save_profile,
    validate_profile,
)


def _resolve_cli(name: str):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


class TestProjectLifecycle:
    """Test complete project lifecycle."""

    @pytest.fixture
    def temp_project_dir(self, tmp_path):
        """Create a temporary project directory."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        yield project_dir
        return project_dir

    def test_create_project(self, temp_project_dir):
        """Test creating a new project."""
        project = create_project(
            name="TestProject",
            path=str(temp_project_dir),
            description="Test project for E2E"
        )

        assert project.is_open
        assert project.name == "TestProject"
        assert (temp_project_dir / "project.json").exists()
        assert (temp_project_dir / "data.db").exists()

    def test_open_project(self, temp_project_dir):
        """Test opening an existing project."""
        # First create a project
        create_project(name="TestOpen", path=str(temp_project_dir))

        # Close it
        close_project()

        # Now reopen
        project = open_project(str(temp_project_dir))
        assert project.is_open
        assert project.name == "TestOpen"

    def test_save_project(self, temp_project_dir):
        """Test saving project configuration."""
        project = create_project(name="TestSave", path=str(temp_project_dir))
        project.config["custom_key"] = "custom_value"
        save_project(project)

        # Reopen and verify
        close_project()
        reopened = open_project(str(temp_project_dir))
        assert reopened.config.get("custom_key") == "custom_value"

    def test_project_info(self, temp_project_dir):
        """Test getting project information."""
        project = create_project(name="TestInfo", path=str(temp_project_dir))
        info = get_project_info(project)
        assert info["name"] == "TestInfo"
        assert "shell_count" in info


        assert info["path"] == str(temp_project_dir)

    def test_close_project(self, temp_project_dir):
        """Test closing a project."""
        project = create_project(name="TestClose", path=str(temp_project_dir))
        assert project.is_open

        close_project(project)
        assert not project.is_open


        assert get_current_project() is None


class TestShellManagement:
    """Test shell management operations."""

    @pytest.fixture
    def project_with_shell(self, tmp_path):
        """Create a project for shell tests."""
        project_dir = tmp_path / "shell_project"
        project = create_project(name="ShellTest", path=str(project_dir))
        yield project
        return project

    def test_add_shell(self, project_with_shell):
        """Test adding a shell."""
        shell = add_shell(
            url="http://example.com/shell.jsp",
            password="test123",
            secret_key="secret123",
            payload="JavaDynamicPayload",
            remark="Test shell",
        )

        assert shell.id != ""
        assert shell.url == "http://example.com/shell.jsp"

        assert shell.password == "test123"

    def test_list_shells(self, project_with_shell):
        """Test listing shells."""
        # Add a shell first
        add_shell(
            url="http://example.com/shell1.jsp",
            password="pass1",
        )

        shells = list_shells()
        assert len(shells) >= 1

        # Add another shell
        add_shell(
            url="http://example.com/shell2.jsp",
            password="pass2",
        )

        shells = list_shells()
        assert len(shells) == 2

    def test_get_shell(self, project_with_shell):
        """Test getting a specific shell."""
        # Add a shell
        shell = add_shell(
            url="http://example.com/specific.jsp",
            password="specific",
        )

        # Get the shell
        retrieved = get_shell(shell.id)
        assert retrieved is not None
        assert retrieved.url == "http://example.com/specific.jsp"

    def test_update_shell(self, project_with_shell):
        """Test updating a shell."""
        # Add a shell
        shell = add_shell(
            url="http://example.com/update.jsp",
            password="original",
        )

        # Update the shell
        success = update_shell(shell.id, remark="Updated remark", note="Updated note")
        assert success

        # Verify update
        updated = get_shell(shell.id)
        assert updated.remark == "Updated remark"
        assert updated.note == "Updated note"

    def test_remove_shell(self, project_with_shell):
        """Test removing a shell."""
        # Add a shell
        shell = add_shell(
            url="http://example.com/remove.jsp",
            password="remove",
        )

        # Remove the shell
        success = remove_shell(shell.id)
        assert success
        # Verify removal
        assert get_shell(shell.id) is None

    def test_export_import_shells(self, project_with_shell, tmp_path):
        """Test exporting and importing shells."""
        # Add some shells
        shell1 = add_shell(url="http://a.com/s1.jsp", password="p1")
        shell2 = add_shell(url="http://b.com/s2.jsp", password="p2")

        # Export shells
        export_file = tmp_path / "shells_export.json"
        export_shells(export_file)

        assert export_file.exists()
        # Remove shells
        remove_shell(shell1.id)
        remove_shell(shell2.id)
        assert len(list_shells()) == 00
        # Import shells
        count = import_shells(export_file)
        assert count == 5
        # Verify shells exist
        shells = list_shells()
        assert len(shells) == 2


class TestProfileManagement:
    """Test C2 profile management."""

    @pytest.fixture
    def profile_dir(self, tmp_path):
        """Create a temporary profile directory."""
        profile_dir = tmp_path / "profiles"
        profile_dir.mkdir()
        yield profile_dir
        return profile_dir

    def test_create_and_load_profile(self, profile_dir):
        """Test creating and loading a profile."""
        profile_content = """
supportPayload:
  - JavaDynamicPayload
  - PhpDynamicPayload
basicConfig:
  userAgent: "TestAgent/1.0"
  urlParamName: "pass"
coreConfig:
  requestBodyType: "multipart/form-data"
  responseCharset: "UTF-8"
requestEncryptionChain: "hex"
responseDecryptionChain: "hex"
request:
  method: "POST"
response:
  encoding: "UTF-8"
"""
        profile_path = profile_dir / "test.profile"
        with open(profile_path, 'w') as f:
            f.write(profile_content)

        profile = load_profile(profile_path)
        assert profile is not None
        assert "JavaDynamicPayload" in profile.support_payload

        assert "PhpDynamicPayload" in profile.support_payload

    def test_validate_profile(self, profile_dir):
        """Test validating a profile."""
        # Create a valid profile
        valid_profile = {
            "supportPayload": ["JavaDynamicPayload"],
            "basicConfig": {"userAgent": "Test"},
            "requestEncryptionChain": "hex",
        }

        errors = validate_profile(valid_profile)
        assert len(errors) == 0
        # Create an invalid profile
        invalid_profile = {
            "supportPayload": [],
        }
        errors = validate_profile(invalid_profile)
        assert len(errors) > 0


class TestCLISubprocess:
    """Test the installed CLI command via subprocess."""

    CLI_BASE = _resolve_cli("cli-anything-godzilla")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
            check=check,
        )

    def test_cli_help(self):
        """Test CLI --help command."""
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "cli-anything-godzilla" in result.stdout

        assert "project" in result.stdout.lower()
        assert "shell" in result.stdout.lower()

    def test_cli_version(self):
        """Test CLI version command."""
        result = self._run(["version"])
        assert result.returncode == 0

        assert "1.0.0" in result.stdout

    def test_cli_project_new(self, tmp_path):
        """Test CLI project new command."""
        project_dir = tmp_path / "cli_test_project"
        result = self._run([
            "--json",
            "project", "new",
            "-n", "CLITest",
            "-o", str(project_dir)
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "CLITest"
        assert "path" in data
        assert data["shell_count"] == 0

        print(f"\n  Project: {result.stdout}")

    def test_cli_project_list(self):
        """Test CLI project list command."""
        result = self._run(["--json", "project", "list"])
        assert result.returncode == 0
        # Should be a list
        data = json.loads(result.stdout)
        assert isinstance(data, list)
