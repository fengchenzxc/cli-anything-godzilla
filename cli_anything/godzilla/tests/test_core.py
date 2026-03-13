"""
Unit tests for cli-anything-godzilla core modules.

Tests core functionality with synthetic data, no external dependencies.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import modules to test
from cli_anything.godzilla.core.project import (
    Project,
    create_project,
    open_project,
    save_project,
    close_project,
    get_project_info,
    list_projects,
    get_current_project,
    _current_project,
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


class TestProject:
    """Test project management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")

    def teardown_method(self):
        """Clean up test fixtures."""
        global _current_project
        _current_project = None

    def test_create_project(self):
        """Test project creation."""
        project = create_project(
            name="test_project",
            path=self.project_path,
            description="Test project for unit tests"
        )

        assert project is not None
        assert project.name == "test_project"
        assert project.is_open
        assert os.path.exists(self.project_path)

        # Verify project files created
        assert os.path.exists(os.path.join(self.project_path, "project.json"))
        assert os.path.exists(os.path.join(self.project_path, "data.db"))

    def test_open_project(self):
        """Test opening existing project."""
        # First create a project
        create_project(
            name="test_project",
            path=self.project_path,
            description="Test project"
        )
        close_project()

        # Now open it
        project = open_project(self.project_path)
        assert project is not None
        assert project.is_open
        assert project.name == "test_project"

    def test_open_nonexistent_project(self):
        """Test opening non-existent project."""
        with pytest.raises(FileNotFoundError):
            open_project("/nonexistent/path")

    def test_save_project(self):
        """Test saving project configuration."""
        project = create_project(
            name="test_project",
            path=self.project_path,
        )

        # Modify config
        project.config["custom_field"] = "test_value"
        save_project(project)

        # Verify saved
        with open(os.path.join(self.project_path, "project.json"), 'r') as f:
            config = json.load(f)

        assert config["custom_field"] == "test_value"

    def test_close_project(self):
        """Test closing project."""
        project = create_project(
            name="test_project",
            path=self.project_path
        )

        assert project.is_open
        close_project(project)
        assert not project.is_open

    def test_get_project_info(self):
        """Test getting project info."""
        project = create_project(
            name="test_project",
            path=self.project_path,
            description="Test description"
        )

        info = get_project_info(project)
        assert info["name"] == "test_project"
        assert info["description"] == "Test description"
        assert "path" in info

    def test_list_projects(self):
        """Test listing projects."""
        # Create a test project in the default directory
        import uuid
        unique_name = f"test_project_list_{uuid.uuid4().hex[:8]}"
        project = create_project(
            name=unique_name,
            path=None,  # Use default path
        )

        projects = list_projects()
        assert isinstance(projects, list)
        assert len(projects) >= 1

        # Find our test project
        found = False
        for p in projects:
            if p["name"] == unique_name:
                found = True
                break
        assert found


class TestShell:
    """Test shell management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        global _current_project
        _current_project = None
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "shell_test_project")
        self.project = create_project(
            name="shell_test",
            path=self.project_path,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        global _current_project
        close_project()
        _current_project = None

    def test_add_shell(self):
        """Test adding a shell."""
        shell = add_shell(
            url="http://example.com/shell.jsp",
            password="test123",
            secret_key="secret",
            payload="JavaDynamicPayload",
        )

        assert shell is not None
        assert shell.id != ""
        assert shell.url == "http://example.com/shell.jsp"
        assert shell.payload == "JavaDynamicPayload"

    def test_add_shell_minimal(self):
        """Test adding shell with minimal params."""
        shell = add_shell(
            url="http://minimal.com/shell.jsp",
            password="pass",
        )

        assert shell is not None
        assert shell.url == "http://minimal.com/shell.jsp"

    def test_update_shell(self):
        """Test updating a shell."""
        shell = add_shell(
            url="http://example.com/update.jsp",
            password="test123",
        )

        # Update shell
        success = update_shell(
            shell.id,
            remark="Updated remark",
            note="Updated note"
        )

        assert success
        updated = get_shell(shell.id)
        assert updated.remark == "Updated remark"

    def test_update_nonexistent_shell(self):
        """Test updating non-existent shell."""
        success = update_shell(
            "nonexistent-id",
            remark="test"
        )

        assert not success

    def test_remove_shell(self):
        """Test removing a shell."""
        shell = add_shell(
            url="http://example.com/remove.jsp",
            password="test123",
        )

        shell_id = shell.id
        success = remove_shell(shell_id)
        assert success

        # Verify shell is gone
        removed = get_shell(shell_id)
        assert removed is None

    def test_remove_nonexistent_shell(self):
        """Test removing non-existent shell."""
        success = remove_shell("nonexistent-id")
        assert not success

    def test_list_shells(self):
        """Test listing shells."""
        # Add multiple shells
        add_shell(url="http://example.com/1.jsp", password="pass1")
        add_shell(url="http://example.com/2.jsp", password="pass2")

        shells = list_shells()
        assert len(shells) >= 2

    def test_list_shells_empty(self):
        """Test listing shells in empty project."""
        global _current_project
        close_project()

        # Create new empty project
        empty_path = os.path.join(self.temp_dir, "empty_project")
        empty_project = create_project(name="empty", path=empty_path)

        shells = list_shells()
        assert len(shells) == 0

    def test_get_shell(self):
        """Test getting a specific shell."""
        shell = add_shell(
            url="http://example.com/get.jsp",
            password="test123",
        )

        retrieved = get_shell(shell.id)
        assert retrieved is not None
        assert retrieved.id == shell.id

    def test_get_nonexistent_shell(self):
        """Test getting non-existent shell."""
        retrieved = get_shell("nonexistent-id")
        assert retrieved is None


class TestProfile:
    """Test C2Profile functionality."""

    def setup_method(self):
        """Set up test fixtures - create a project for profile tests."""
        global _current_project
        _current_project = None
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "profile_test_project")
        self.project = create_project(
            name="profile_test",
            path=self.project_path,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        global _current_project
        close_project()
        _current_project = None

    def test_load_profile(self, tmp_path):
        """Test loading a valid profile from project profile directory."""
        # Create profile in the project's profile directory
        project = get_current_project()
        profile_dir = project.project_path / "profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

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
  regexPattern: ""
  encoding: "UTF-8"
"""
        profile_path = profile_dir / "test.profile"
        profile_path.write_text(profile_content)

        profile = load_profile("test")
        assert profile is not None
        assert "JavaDynamicPayload" in profile.support_payload

    def test_load_invalid_profile(self, tmp_path):
        """Test loading an invalid profile."""
        # Create invalid profile in the project's profile directory
        project = get_current_project()
        profile_dir = project.project_path / "profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        profile_path = profile_dir / "invalid.profile"
        profile_path.write_text("invalid yaml content: [")

        # Should raise exception for invalid YAML
        with pytest.raises(Exception):
            load_profile("invalid")

    def test_validate_profile_valid(self):
        """Test validating a valid profile."""
        profile_data = {
            "name": "test_profile",
            "supportPayload": ["JavaDynamicPayload"],
            "basicConfig": {"userAgent": "Test"},
            "coreConfig": {"requestBodyType": "multipart/form-data"},
            "requestEncryptionChain": "hex",
            "responseDecryptionChain": "hex",
            "request": {"method": "POST"},
            "response": {"encoding": "UTF-8"},
        }

        result = validate_profile(profile_data)
        assert len(result.get("errors", [])) == 0

    def test_validate_profile_invalid(self):
        """Test validating an invalid profile."""
        profile_data = {
            "supportPayload": [],
            # Missing required fields
        }

        result = validate_profile(profile_data)
        assert len(result.get("errors", [])) > 0


class TestShellEntity:
    """Test ShellEntity dataclass."""

    def test_shell_entity_to_dict(self):
        """Test ShellEntity serialization."""
        shell = ShellEntity(
            id="test-id",
            url="http://example.com/shell.jsp",
            password="test123",
            payload="JavaDynamicPayload",
        )

        data = shell.to_dict()
        assert data["id"] == "test-id"
        assert data["url"] == "http://example.com/shell.jsp"

    def test_shell_entity_from_dict(self):
        """Test ShellEntity deserialization."""
        data = {
            "id": "test-id",
            "url": "http://example.com/shell.jsp",
            "password": "test123",
            "payload": "JavaDynamicPayload",
        }

        shell = ShellEntity.from_dict(data)
        assert shell.id == "test-id"
        assert shell.url == "http://example.com/shell.jsp"

    def test_shell_entity_get_summary(self):
        """Test ShellEntity summary."""
        shell = ShellEntity(
            id="test-id-12345",
            url="http://example.com/shell.jsp",
            password="test123",
            payload="JavaDynamicPayload",
        )

        summary = shell.get_summary()
        assert "test-id" in summary
        assert "shell.jsp" in summary


if __name__ == "__main__":
    pytest.main([__file__])
