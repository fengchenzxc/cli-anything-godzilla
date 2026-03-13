# cli-anything-godzilla

[English](README.md) | [简体中文](README_CN.md)

CLI harness for Godzilla Security Testing Tool

## Installation

### Prerequisites

- Python 3.12+ (tested with Python 3.12.8)
- Java Runtime Environment (JRE) 11+
- Godzilla JAR file (Godzilla15.jar or placed in Godzilla installation directory)

### Install the CLI

```bash
# From PyPI (when published)
pip install cli-anything-godzilla

# Or install locally for development
cd /tmp/哥斯拉402Godzilla/agent-harness
pip install -e .
```

### Verify Installation

```bash
which cli-anything-godzilla
cli-anything-godzilla --help
```

## Usage

### Start Interactive REPL Mode

```bash
# Start with no arguments (enter REPL mode)
cli-anything-godzilla

# Or specify a project
cli-anything-godzilla -p /path/to/project.json
```

### Create a New Project

```bash
cli-anything-godzilla project new -n "My Project" -d "Project description"
```

### Open an Existing Project

```bash
cli-anything-godzilla project open /path/to/project.json
```

### Manage Shells

```bash
# Add a shell
cli-anything-godzilla shell add -u http://target.com/shell.jsp -p password

# List all shells
cli-anything-godzilla shell list

# Get shell details
cli-anything-godzilla shell get <shell-id>

# Test shell connectivity
cli-anything-godzilla shell test <shell-id>

# Update shell configuration
cli-anything-godzilla shell update <shell-id> --remark "Updated remark"

# Remove a shell
cli-anything-godzilla shell remove <shell-id>
```

### Manage C2 Profiles

```bash
# List available profiles
cli-anything-godzilla profile list

# Load a profile
cli-anything-godzilla profile load /path/to/profile.yml

# Validate a profile
cli-anything-godzilla profile validate /path/to/profile.yml
```

## JSON Output Mode

All commands support `--json` flag for machine-readable output:

```bash
cli-anything-godzilla --json shell list
```

## REPL Commands

When in interactive mode, type these commands:

| Command | Description |
|--------|-------------|
| `help` | Show available commands |
| `exit` | Exit REPL mode |
| `project info` | Show project information |
| `project list` | List all projects |
| `shell list` | List all shells |
| `shell get <id>` | Get shell details |
| `shell add <url> <password>` | Add new shell |
| `shell test <id>` | Test shell connectivity |
| `profile list` | List C2 profiles |

## Configuration

### Project Configuration

Projects are stored as JSON files with the following structure
```json
{
    "name": "Project Name",
    "description": "Project description",
    "version": "1.0.0",
    "created": "2024-01-01T00:00:00",
    "modified": "2024-01-01T00:00:00",
    "default_payload": "JavaDynamicPayload",
    "default_cryption": "xor",
    "default_encoding": "UTF-8"
}
```

### Shell Configuration

Shells are stored in SQLite database with the following structure
- id: Unique identifier
- url: Shell URL
- password: Shell password
- secret_key: Encryption secret key
- payload: Payload type
- cryption: Encryption method
- encoding: Character encoding
- headers: HTTP headers
- proxy_type: Proxy type
- proxy_host: Proxy host
- proxy_port: Proxy port

### C2 Profile Configuration

C2 profiles are YAML files with traffic shaping rules
```yaml
supportPayload:
  - JavaDynamicPayload
  - CSharpDynamicPayload
  - PhpDynamicPayload
basicConfig:
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  urlParamName: "pass"
coreConfig:
  requestBodyType: "multipart/form-data"
  responseCharset: "UTF-8"
requestEncryptionChain: "hex"
responseDecryptionChain: "hex"
```

## Running Tests

```bash
# Run unit tests
cd /tmp/哥斯拉402Godzilla/agent-harness
python3.12 -m pytest cli_anything/godzilla/tests/test_core.py -v

# Run E2E tests
python3.12 -m pytest cli_anything/godzilla/tests/test_full_e2e.py -v -s

# Run with force-installed mode
CLI_ANYTHING_FORCE_INSTALLED=1 python3.12 -m pytest cli_anything/godzilla/tests/ -v -s
```

## Development

### Project Structure

```
cli_anything/godzilla/
├── __init__.py
├── godzilla_cli.py      # Main CLI entry point
├── core/
│   ├── __init__.py
│   ├── project.py       # Project management
│   ├── shell.py         # Shell management
│   ├── profile.py       # C2 Profile management
│   └── database.py      # Database operations
├── utils/
│   ├── __init__.py
│   ├── godzilla_backend.py  # Godzilla JAR integration
│   └── repl_skin.py         # REPL interface
└── tests/
    ├── TEST.md
    ├── test_core.py
    └── test_full_e2e.py
```

## License

MIT License
