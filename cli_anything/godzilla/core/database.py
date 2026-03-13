"""
Database module for cli-anything-godzilla.

Provides SQLite database operations for managing Godzilla shells, profiles, and settings.
Mirrors the Godzilla's core.C0805Db class structure with camelCase column names.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


class GodzillaDatabase:
    """SQLite database manager for Godzilla CLI."""

    SHELL_TABLE = """
    CREATE TABLE IF NOT EXISTS shell (
        id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        password TEXT NOT NULL,
        secretKey TEXT NOT NULL,
        payload TEXT NOT NULL,
        cryption TEXT NOT NULL,
        encoding TEXT NOT NULL,
        headers TEXT NOT NULL,
        reqLeft TEXT NOT NULL,
        reqRight TEXT NOT NULL,
        connTimeout INTEGER NOT NULL,
        readTimeout INTEGER NOT NULL,
        proxyType TEXT NOT NULL,
        proxyHost TEXT NOT NULL,
        proxyPort INTEGER NOT NULL,
        remark TEXT NOT NULL,
        note TEXT,
        createTime TEXT NOT NULL,
        updateTime TEXT NOT NULL
    )
    """

    SHELL_ENV_TABLE = """
    CREATE TABLE IF NOT EXISTS shellEnv (
        shellId TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT
    )
    """

    PLUGIN_TABLE = """
    CREATE TABLE IF NOT EXISTS plugin (
        pluginJarFile TEXT PRIMARY KEY
    )
    """

    SETTING_TABLE = """
    CREATE TABLE IF NOT EXISTS seting (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """

    SHELL_GROUP_TABLE = """
    CREATE TABLE IF NOT EXISTS shellGroup (
        groupId TEXT PRIMARY KEY
    )
    """

    def __init__(self, db_path: str):
        """Initialize the database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        self._conn = sqlite3.connect(str(self.db_path))
        cursor = self._conn.cursor()

        # Create tables if they don't exist
        cursor.execute(self.SHELL_TABLE)
        cursor.execute(self.SHELL_ENV_TABLE)
        cursor.execute(self.PLUGIN_TABLE)
        cursor.execute(self.SETTING_TABLE)
        cursor.execute(self.SHELL_GROUP_TABLE)
        cursor.close()
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ==================== Shell Operations ====================

    def add_shell(self, shell_data: Dict[str, Any]) -> str:
        """Add a new shell to the database.

        Args:
            shell_data: Dictionary containing shell configuration

        Returns:
            The generated shell ID
        """
        shell_id = shell_data.get('id') or self._generate_uuid()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO shell (
                id, url, password, secretKey, payload, cryption, encoding,
                headers, reqLeft, reqRight, connTimeout, readTimeout,
                proxyType, proxyHost, proxyPort, remark, note, createTime, updateTime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shell_id,
            shell_data.get('url', ''),
            shell_data.get('password', ''),
            shell_data.get('secret_key', ''),
            shell_data.get('payload', 'JavaDynamicPayload'),
            shell_data.get('cryption', 'xor'),
            shell_data.get('encoding', 'UTF-8'),
            json.dumps(shell_data.get('headers', {})),
            shell_data.get('req_left', ''),
            shell_data.get('req_right', ''),
            shell_data.get('conn_timeout', 60000),
            shell_data.get('read_timeout', 60000),
            shell_data.get('proxy_type', 'NO_PROXY'),
            shell_data.get('proxy_host', ''),
            shell_data.get('proxy_port', 0),
            shell_data.get('remark', ''),
            shell_data.get('note', ''),
            now,
            now
        ))
        cursor.close()
        self._conn.commit()
        return shell_id

    def update_shell(self, shell_id: str, shell_data: Dict[str, Any]) -> bool:
        """Update an existing shell.

        Args:
            shell_id: The shell ID to update
            shell_data: Dictionary containing updated shell configuration

        Returns:
            True if update was successful
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self._conn.cursor()
        cursor.execute("""
            UPDATE shell SET
                url = ?, password = ?, secretKey = ?, payload = ?,
                cryption = ?, encoding = ?, headers = ?, reqLeft = ?,
                reqRight = ?, connTimeout = ?, readTimeout = ?,
                proxyType = ?, proxyHost = ?, proxyPort = ?,
                remark = ?, note = ?, updateTime = ?
            WHERE id = ?
        """, (
            shell_data.get('url', ''),
            shell_data.get('password', ''),
            shell_data.get('secret_key', ''),
            shell_data.get('payload', 'JavaDynamicPayload'),
            shell_data.get('cryption', 'xor'),
            shell_data.get('encoding', 'UTF-8'),
            json.dumps(shell_data.get('headers', {})),
            shell_data.get('req_left', ''),
            shell_data.get('req_right', ''),
            shell_data.get('conn_timeout', 60000),
            shell_data.get('read_timeout', 60000),
            shell_data.get('proxy_type', 'NO_PROXY'),
            shell_data.get('proxy_host', ''),
            shell_data.get('proxy_port', 1),
            shell_data.get('remark', ''),
            shell_data.get('note', ''),
            now,
            shell_id
        ))
        affected = cursor.rowcount > 0
        cursor.close()
        self._conn.commit()
        return affected

    def remove_shell(self, shell_id: str) -> bool:
        """Remove a shell from the database.

        Args:
            shell_id: The shell ID to remove

        Returns:
            True if removal was successful
        """
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM shell WHERE id = ?", (shell_id,))
        affected = cursor.rowcount > 0
        cursor.close()
        self._clear_shell_env(shell_id)
        self._conn.commit()
        return affected

    def get_shell(self, shell_id: str) -> Optional[Dict[str, Any]]:
        """Get a shell by ID.

        Args:
            shell_id: The shell ID to retrieve

        Returns:
            Dictionary containing shell data or None
        """
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT id, url, password, secretKey, payload, cryption, encoding,
                   headers, reqLeft, reqRight, connTimeout, readTimeout,
                   proxyType, proxyHost, proxyPort, remark, note, createTime, updateTime
            FROM shell WHERE id = ?
        """, (shell_id,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return self._row_to_shell_dict(row)
        return None

    def list_shells(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all shells, optionally filtered by group.

        Args:
            group_id: Optional group ID to filter by

        Returns:
            List of shell dictionaries
        """
        shells = []

        cursor = self._conn.cursor()
        if group_id and group_id != "/":
            cursor.execute("""
                SELECT s.id, s.url, s.password, s.secretKey, s.payload, s.cryption, s.encoding,
                       s.headers, s.reqLeft, s.reqRight, s.connTimeout, s.readTimeout,
                       s.proxyType, s.proxyHost, s.proxyPort, s.remark, s.note, s.createTime, s.updateTime
                FROM shellEnv e
                LEFT JOIN shell s ON e.shellId = s.id
                WHERE e.key = 'ENV_GROUP_ID' AND e.value LIKE ?
            """, (f"%{group_id}%",))
            rows = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT id, url, password, secretKey, payload, cryption, encoding,
                       headers, reqLeft, reqRight, connTimeout, readTimeout,
                       proxyType, proxyHost, proxyPort, remark, note, createTime, updateTime
                FROM shell
            """)
            rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            shells.append(self._row_to_shell_dict(row))

        return shells

    def _row_to_shell_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert a database row to a shell dictionary."""
        # Handle headers - could be JSON or plain text format
        headers_raw = row[7]
        if headers_raw:
            try:
                headers = json.loads(headers_raw)
            except (json.JSONDecodeError, ValueError):
                # Plain text format, convert to dict
                headers = {}
                for line in headers_raw.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
        else:
            headers = {}

        return {
            'id': row[0],
            'url': row[1],
            'password': row[2],
            'secret_key': row[3],
            'payload': row[4],
            'cryption': row[5],
            'encoding': row[6],
            'headers': headers,
            'req_left': row[8],
            'req_right': row[9],
            'conn_timeout': row[10],
            'read_timeout': row[11],
            'proxy_type': row[12],
            'proxy_host': row[13],
            'proxy_port': row[14],
            'remark': row[15],
            'note': row[16],
            'create_time': row[17],
            'update_time': row[18]
        }

    # ==================== Shell Environment Operations ====================

    def set_shell_env(self, shell_id: str, key: str, value: str) -> bool:
        """Set an environment variable for a shell."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO shellEnv (shellId, key, value)
            VALUES (?, ?, ?)
        """, (shell_id, key, value))
        cursor.close()
        self._conn.commit()
        return True

    def get_shell_env(self, shell_id: str, key: str) -> Optional[str]:
        """Get an environment variable for a shell."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT value FROM shellEnv WHERE shellId = ? AND key = ?
        """, (shell_id, key))
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None

    def _clear_shell_env(self, shell_id: str) -> None:
        """Clear all environment variables for a shell."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM shellEnv WHERE shellId = ?", (shell_id,))
        cursor.close()

    # ==================== Group Operations ====================

    def add_group(self, group_id: str) -> bool:
        """Add a new shell group."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("INSERT INTO shellGroup (groupId) VALUES (?)", (group_id,))
            cursor.close()
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_group(self, group_id: str, default_group: str = "/") -> bool:
        """Remove a group and move shells to default group."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM shellGroup WHERE groupId LIKE ?", (f"%{group_id}%",))
        cursor.execute("""
            UPDATE shellEnv SET value = ?
            WHERE key = 'ENV_GROUP_ID' AND value LIKE ?
        """, (default_group, f"%{group_id}%"))
        cursor.close()
        self._conn.commit()
        return True

    def list_groups(self) -> List[str]:
        """List all shell groups."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT groupId FROM shellGroup")
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result

    # ==================== Setting Operations ====================

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT value FROM seting WHERE key = ?", (key,))
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else default

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value."""
        cursor = self._conn.cursor()
        existing = self.get_setting(key)
        if existing:
            cursor.execute("UPDATE seting SET value = ? WHERE key = ?", (value, key))
        else:
            cursor.execute("INSERT INTO seting (key, value) VALUES (?, ?)", (key, value))
        cursor.close()
        self._conn.commit()
        return True

    def remove_setting(self, key: str) -> bool:
        """Remove a setting."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM seting WHERE key = ?", (key,))
        affected = cursor.rowcount > 0
        cursor.close()
        self._conn.commit()
        return affected

    # ==================== Plugin Operations ====================

    def add_plugin(self, jar_path: str) -> bool:
        """Register a plugin JAR file."""
        try:
            cursor = self._conn.cursor()
            cursor.execute("INSERT INTO plugin (pluginJarFile) VALUES (?)", (jar_path,))
            cursor.close()
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_plugin(self, jar_path: str) -> bool:
        """Remove a plugin JAR file."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM plugin WHERE pluginJarFile = ?", (jar_path,))
        affected = cursor.rowcount > 0
        cursor.close()
        self._conn.commit()
        return affected

    def list_plugins(self) -> List[str]:
        """List all registered plugin JAR files."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT pluginJarFile FROM plugin")
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a UUID for shell IDs."""
        import uuid
        return str(uuid.uuid4())
