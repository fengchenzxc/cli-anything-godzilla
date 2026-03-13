"""
Shell management module for cli-anything-godzilla.

Provides shell entity definition and CRUD operations.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime

from cli_anything.godzilla.core.project import get_current_project


@dataclass
class ShellEntity:
    """Represents a webshell entity in Godzilla."""

    id: str = ""
    url: str = ""
    password: str = ""
    secret_key: str = ""
    payload: str = "JavaDynamicPayload"
    cryption: str = "xor"
    encoding: str = "UTF-8"
    headers: Dict[str, List[str]] = field(default_factory=dict)
    req_left: str = ""
    req_right: str = ""
    conn_timeout: int = 60000
    read_timeout: int = 60000
    proxy_type: str = "NO_PROXY"
    proxy_host: str = ""
    proxy_port: int = 0
    remark: str = ""
    note: str = ""
    create_time: str = ""
    update_time: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShellEntity":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            password=data.get("password", ""),
            secret_key=data.get("secret_key", ""),
            payload=data.get("payload", "JavaDynamicPayload"),
            cryption=data.get("cryption", "xor"),
            encoding=data.get("encoding", "UTF-8"),
            headers=data.get("headers", {}),
            req_left=data.get("req_left", ""),
            req_right=data.get("req_right", ""),
            conn_timeout=data.get("conn_timeout", 60000),
            read_timeout=data.get("read_timeout", 60000),
            proxy_type=data.get("proxy_type", "NO_PROXY"),
            proxy_host=data.get("proxy_host", ""),
            proxy_port=data.get("proxy_port", 0),
            remark=data.get("remark", ""),
            note=data.get("note", ""),
            create_time=data.get("create_time", ""),
            update_time=data.get("update_time", ""),
        )

    def get_summary(self) -> str:
        """Get a brief summary of this shell."""
        return f"{self.id[:8]}... | {self.url} | {self.payload} | {self.cryption}"


# Supported payload types
PAYLOAD_TYPES = [
    "JavaDynamicPayload",
    "CSharpDynamicPayload",
    "PhpDynamicPayload",
]

# Supported encryption types
ENCRYPTION_TYPES = [
    "xor",
    "aes128",
    "aes256",
    "base64",
    "hex",
    "raw",
    "rsa",
]

# Supported encoding types
ENCODING_TYPES = [
    "UTF-8",
    "GBK",
    "GB2312",
    "BIG5",
    "GB18030",
    "ISO-8859-1",
    "latin1",
]

# Proxy types
PROXY_TYPES = [
    "NO_PROXY",
    "HTTP",
    "HTTPS",
    "SOCKS4",
    "SOCKS5",
]


def add_shell(
    url: str,
    password: str,
    secret_key: str = "",
    payload: str = "JavaDynamicPayload",
    cryption: str = "xor",
    encoding: str = "UTF-8",
    headers: Optional[Dict[str, List[str]]] = None,
    req_left: str = "",
    req_right: str = "",
    conn_timeout: int = 60000,
    read_timeout: int = 60000,
    proxy_type: str = "NO_PROXY",
    proxy_host: str = "",
    proxy_port: int = 0,
    remark: str = "",
    note: str = "",
) -> ShellEntity:
    """Add a new shell to the current project.

    Args:
        url: Shell URL
        password: Shell password
        secret_key: Secret key for encryption
        payload: Payload type (JavaDynamicPayload, CSharpDynamicPayload, PhpDynamicPayload)
        cryption: Encryption type (xor, aes128, aes256, base64, hex, raw, rsa)
        encoding: Character encoding
        headers: HTTP headers dictionary
        req_left: Left request wrapper
        req_right: Right request wrapper
        conn_timeout: Connection timeout in milliseconds
        read_timeout: Read timeout in milliseconds
        proxy_type: Proxy type (NO_PROXY, HTTP, HTTPS, SOCKS4, SOCKS5)
        proxy_host: Proxy host
        proxy_port: Proxy port
        remark: Shell remark
        note: Shell note

    Returns:
        The created ShellEntity

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    shell_data = {
        "url": url,
        "password": password,
        "secret_key": secret_key,
        "payload": payload,
        "cryption": cryption,
        "encoding": encoding,
        "headers": headers or {},
        "req_left": req_left,
        "req_right": req_right,
        "conn_timeout": conn_timeout,
        "read_timeout": read_timeout,
        "proxy_type": proxy_type,
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "remark": remark,
        "note": note,
    }

    shell_id = project.db.add_shell(shell_data)
    shell_data["id"] = shell_id

    # Set create/update time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    shell_data["create_time"] = now
    shell_data["update_time"] = now

    project.mark_modified()

    return ShellEntity.from_dict(shell_data)


def update_shell(shell_id: str, **kwargs) -> bool:
    """Update an existing shell (supports partial ID matching).

    Args:
        shell_id: Shell ID or partial ID to update
        **kwargs: Shell properties to update

    Returns:
        True if update was successful

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    # Resolve partial ID to full ID
    shell = get_shell(shell_id)
    if not shell:
        return False

    full_id = shell.id

    # Get existing shell data
    existing = project.db.get_shell(full_id)
    if not existing:
        return False

    # Merge updates
    existing.update(kwargs)

    success = project.db.update_shell(full_id, existing)

    if success:
        project.mark_modified()

    return success


def remove_shell(shell_id: str) -> bool:
    """Remove a shell from the project (supports partial ID matching).

    Args:
        shell_id: Shell ID or partial ID to remove

    Returns:
        True if removal was successful

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    # Resolve partial ID to full ID
    shell = get_shell(shell_id)
    if not shell:
        return False

    success = project.db.remove_shell(shell.id)

    if success:
        project.mark_modified()

    return success


def list_shells(group_id: Optional[str] = None) -> List[ShellEntity]:
    """List all shells in the current project.

    Args:
        group_id: Optional group ID to filter by

    Returns:
        List of ShellEntity objects

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    shells = project.db.list_shells(group_id)
    return [ShellEntity.from_dict(s) for s in shells]


def get_shell(shell_id: str) -> Optional[ShellEntity]:
    """Get a specific shell by ID (supports partial ID matching).

    Args:
        shell_id: Shell ID or partial ID to retrieve

    Returns:
        ShellEntity or None if not found

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    # Try exact match first
    shell_data = project.db.get_shell(shell_id)
    if shell_data:
        return ShellEntity.from_dict(shell_data)

    # Try partial ID matching
    shells = project.db.list_shells()
    matches = [s for s in shells if s['id'].startswith(shell_id)]

    if len(matches) == 1:
        return ShellEntity.from_dict(matches[0])
    elif len(matches) > 1:
        # Multiple matches, return None (ambiguous)
        return None

    return None


def test_shell(shell_id: str) -> Dict[str, Any]:
    """Test connectivity to a shell (supports partial ID matching).

    Args:
        shell_id: Shell ID or partial ID to test

    Returns:
        Dictionary with test results

    Raises:
        RuntimeError: If no project is open
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    shell = get_shell(shell_id)
    if not shell:
        return {"success": False, "error": f"Shell not found: {shell_id}"}

    # Import backend for testing
    from cli_anything.godzilla.utils.godzilla_backend import test_shell_connection

    return test_shell_connection(shell)


def export_shells(output_path: str, shell_ids: Optional[List[str]] = None) -> bool:
    """Export shells to a JSON file.

    Args:
        output_path: Path to save the export
        shell_ids: Optional list of shell IDs to export (all if None)

    Returns:
        True if export was successful
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    if shell_ids:
        shells = [get_shell(sid) for sid in shell_ids]
        shells = [s.to_dict() for s in shells if s]
    else:
        shells = [s.to_dict() for s in list_shells()]

    with open(output_path, 'w') as f:
        json.dump({"shells": shells}, f, indent=2)

    return True


def import_shells(input_path: str, overwrite: bool = False) -> int:
    """Import shells from a JSON file.

    Args:
        input_path: Path to the import file
        overwrite: Whether to overwrite existing shells with same ID

    Returns:
        Number of shells imported
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    with open(input_path, 'r') as f:
        data = json.load(f)

    shells = data.get("shells", [])
    imported = 0

    for shell_data in shells:
        shell_id = shell_data.get("id")
        if shell_id:
            existing = get_shell(shell_id)
            if existing and not overwrite:
                continue

            # Remove ID to generate new one or update existing
            if not overwrite:
                shell_data.pop("id", None)

            if existing and overwrite:
                update_shell(shell_id, **shell_data)
            else:
                add_shell(**shell_data)
            imported += 1

    return imported
