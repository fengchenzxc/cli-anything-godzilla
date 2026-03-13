# GODZILLA.md - Software-Specific SOP for cli-anything-godzilla

## Software Analysis

### Overview
Godzilla is a Java-based webshell management tool used for security testing and penetration testing. It provides a GUI interface for managing webshells across multiple targets.

### Backend Engine
- **Primary JAR**: `Godzilla15.jar` (or similar version)
- **Language**: Java
- **UI Framework**: Swing
- **Database**: SQLite
- **Configuration**: YAML (C2 Profiles)

### Data Model

#### Database Schema
```sql
-- Shell storage
CREATE TABLE shell (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    password TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    payload TEXT NOT NULL,
    cryption TEXT NOT NULL,
    encoding TEXT NOT NULL,
    headers TEXT NOT NULL,
    req_left TEXT NOT NULL,
    req_right TEXT NOT NULL,
    conn_timeout INTEGER NOT NULL,
    read_timeout INTEGER NOT NULL,
    proxy_type TEXT NOT NULL,
    proxy_host TEXT NOT NULL,
    proxy_port INTEGER NOT NULL,
    remark TEXT NOT NULL,
    note TEXT,
    create_time TEXT NOT NULL,
    update_time TEXT NOT NULL
)

-- Shell environment variables
CREATE TABLE shellEnv (
    shellId TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT
)

-- Plugin registry
CREATE TABLE plugin (
    pluginJarFile TEXT PRIMARY KEY
)

-- Settings
CREATE TABLE seting (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)

-- Shell groups
CREATE TABLE shellGroup (
    groupId TEXT PRIMARY KEY
)
```

#### C2Profile Schema
```yaml
supportPayload: ["JavaDynamicPayload", "CSharpDynamicPayload", "PhpDynamicPayload"]
enabledStaticPayload: false
enabledCustomGenerate: false
customGenerate:
  template: ""
  params: {}
staticVars: {}
basicConfig:
  userAgent: "Mozilla/5.0..."
  urlParamName: "pass"
coreConfig:
  requestBodyType: "multipart/form-data"
  responseCharset: "UTF-8"
requestEncryptionChain: "hex"
responseDecryptionChain: "hex"
request:
  method: "POST"
  headers: {}
  body_params: {}
response:
  regexPattern: ""
  encoding: "UTF-8"
payloadConfigs: {}
pluginConfigs: {}
```

### GUI Actions to CLI Commands Mapping

| GUI Action | CLI Command | Description |
|------------|-------------|-------------|
| New Project | `project new` | Create a new project |
| Open Project | `project open` | Open an existing project |
| Save Project | `project save` | Save project configuration |
| Add Shell | `shell add` | Add a new webshell |
| Edit Shell | `shell update` | Update shell configuration |
| Remove Shell | `shell remove` | Remove a webshell |
| Test Connection | `shell test` | Test shell connectivity |
| Load Profile | `profile load` | Load a C2 profile |
| Validate Profile | `profile validate` | Validate profile configuration |

### Supported Payload Types
- `JavaDynamicPayload` - Java-based webshells
- `CSharpDynamicPayload` - ASP.NET webshells
- `PhpDynamicPayload` - PHP webshells

### Supported Encryption Methods
- `xor` - XOR encryption (default)
- `aes128` - AES-128 encryption
- `aes256` - AES-256 encryption
- `base64` - Base64 encoding
- `hex` - Hexadecimal encoding
- `raw` - No encryption
- `rsa` - RSA encryption

### Supported Encodings
- `UTF-8` - Default
- `GBK` - Chinese
- `GB2312` - Chinese simplified
- `BIG5` - Traditional Chinese
- `GB18030` - Chinese extended
- `ISO-8859-1` - Latin-1
- `latin1` - Latin-1 alias
- `UTF16` - Unicode UTF-16
- `ascii` - ASCII
- `cp850` - Code page 850

## CLI Architecture

### Command Groups
1. **project** - Project management
   - `new` - Create new project
   - `open` - Open existing project
   - `info` - Show project info
   - `list` - List all projects
   - `close` - Close current project
   - `save` - Save project config

2. **shell** - Shell management
   - `add` - Add new shell
   - `get` - Get shell details
   - `list` - List all shells
   - `update` - Update shell
   - `remove` - Remove shell
   - `test` - Test connectivity
   - `export` - Export shells
   - `import` - Import shells

3. **profile** - C2 Profile management
   - `list` - List profiles
   - `load` - Load profile
   - `validate` - Validate profile

4. **repl** - Interactive mode

### State Model
- **Project State**: In-memory Project object with database connection
- **Session State**: Current project reference, modification flag
- **Persistence**: SQLite database per project

### Output Format
- **Human-readable**: Tables, colored messages via ReplSkin
- **Machine-readable**: JSON via `--json` flag

## Implementation Notes

### Backend Integration
The CLI integrates with the Godzilla JAR for actual operations
- Shell testing
- Command execution
- File operations

### Key Implementation Patterns
1. **Database Operations**: Use GodzillaDatabase class for all DB operations
2. **Profile Loading**: Parse YAML files with PyYAML
3. **Shell Management**: ShellEntity dataclass for type-safe operations
4. **REPL Mode**: PromptToolkit-based interactive interface

### Error Handling
- Clear error messages for agents to self-correct
- Graceful degradation when JAR is not found
- Validation of all user inputs

## Testing Strategy
- Unit tests for core modules with synthetic data
- E2E tests for full workflows with real databases
- Subprocess tests for installed CLI command
