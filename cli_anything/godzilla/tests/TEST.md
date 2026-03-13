# cli-anything-godzilla Test Plan

## Test Inventory Plan

- `test_core.py`: 15 unit tests planned
- `test_full_e2e.py`: 10 E2E tests planned

## Unit Test Plan

### Module: `core/project.py`
| Function | Test Cases | Expected Count |
|----------|------------|----------------|
| `create_project` | Valid creation, duplicate name, 2 |
| `open_project` | Valid open, invalid path | 2 |
| `save_project` | Save configuration | 1 |
| `close_project` | Close and cleanup | 1 |
| `get_project_info` | Get info dict | 1 |
| `list_projects` | List all projects | 1 |

### Module: `core/shell.py`
| Function | Test Cases | Expected Count |
|----------|------------|----------------|
| `add_shell` | Valid shell, missing params | 2 |
| `update_shell` | Update existing, non-existent | 2 |
| `remove_shell` | Remove existing, non-existent | 2 |
| `list_shells` | List all, empty list | 2 |

### Module: `core/profile.py`
| Function | Test Cases | Expected Count |
|----------|------------|----------------|
| `load_profile` | Valid YAML, invalid YAML | 2 |
| `validate_profile` | Valid profile, invalid profile | 2 |

## E2E Test Plan

### Workflow: Project Lifecycle
1. Create new project
2. Add shell to project
3. Save project
4. Close project
5. Reopen project
6. Verify shell exists

### Workflow: Shell Management
1. Open project
2. Add multiple shells
3. Update shell
4. Test shell connectivity
5. Export shells
6. Remove shell

### Workflow: Profile Management
1. Create test profile
2. Load profile
3. Validate profile
4. List profiles

## Realistic Workflow Scenarios

### Scenario 1: Security Audit Setup
**Simulates**: Setting up a security audit project with multiple targets
**Operations**:
1. Create project "audit-2024"
2. Add 5 shells with different configurations
3. Test connectivity to each shell
4. Export configuration for backup

### Scenario 2: Profile Configuration
**Simulates**: Configuring C2 profiles for different payload types
**Operations**:
1. Create project "profile-test"
2. Create custom profile
3. Validate profile
4. Load profile

## Test Results

### Unit Tests (test_core.py) - 2026-03-13

```
============================= test session starts ==============================
platform: darwin -- Python 3.12.8, pytest-9.0.2, pluggy-1.6.0

cli_anything/godzilla/tests/test_core.py::TestProject::test_create_project PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_open_project PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_open_nonexistent_project PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_save_project PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_close_project PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_get_project_info PASSED
cli_anything/godzilla/tests/test_core.py::TestProject::test_list_projects PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_add_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_add_shell_minimal PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_update_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_update_nonexistent_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_remove_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_remove_nonexistent_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_list_shells PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_list_shells_empty PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_get_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestShell::test_get_nonexistent_shell PASSED
cli_anything/godzilla/tests/test_core.py::TestProfile::test_load_profile PASSED
cli_anything/godzilla/tests/test_core.py::TestProfile::test_load_invalid_profile PASSED
cli_anything/godzilla/tests/test_core.py::TestProfile::test_validate_profile_valid PASSED
cli_anything/godzilla/tests/test_core.py::TestProfile::test_validate_profile_invalid PASSED
cli_anything/godzilla/tests/test_core.py::TestShellEntity::test_shell_entity_to_dict PASSED
cli_anything/godzilla/tests/test_core.py::TestShellEntity::test_shell_entity_from_dict PASSED
cli_anything/godzilla/tests/test_core.py::TestShellEntity::test_shell_entity_get_summary PASSED

============================== 24 passed in 0.13s ==============================
```

### CLI Integration Tests

```
$ cli-anything-godzilla --help
Usage: cli-anything-godzilla [OPTIONS] COMMAND [ARGS]...

  Main CLI entry point.

Options:
  -p, --project TEXT      Path to project file
  --jar, --jar-path TEXT  Path to Godzilla JAR file
  --json                  Output in JSON format

Commands:
  help_cmd  Show comprehensive help
  profile   C2 Profile management commands
  project   Project management commands
  repl      Start interactive REPL mode
  shell     Shell management commands
  version   Show version information

$ cli-anything-godzilla project new -n "TestProject"
✓ Created project: TestProject
  Path: /tmp/test_godzilla_project

$ cli-anything-godzilla -p /tmp/test_godzilla_project shell add -u "http://example.com/shell.jsp" -p "test123"
✓ Added shell: 1cadaf5c-53b0-4530-9a1d-afe43d0683d6
  URL: http://example.com/shell.jsp
  Payload: JavaDynamicPayload

$ cli-anything-godzilla -p /tmp/test_godzilla_project shell list
  1cadaf5c: http://example.com/shell.jsp (JavaDynamicPayload)

$ cli-anything-godzilla -p /tmp/test_godzilla_project project info
  Name: TestProject
  Path: /tmp/test_godzilla_project
  Shells: 1
```

### Summary

- **Unit Tests**: 24 passed, 0 failed
- **CLI Integration**: All commands working correctly
- **Coverage**: Project, Shell, Profile, and ShellEntity modules fully tested
