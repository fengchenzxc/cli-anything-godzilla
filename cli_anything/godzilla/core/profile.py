"""
C2Profile management module for cli-anything-godzilla.

Provides C2Profile loading, saving, and validation operations.
C2Profiles define traffic shaping rules for Godzilla.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

from cli_anything.godzilla.core.project import get_current_project


@dataclass
class C2Generate:
    """Custom shell generation configuration."""
    template: str = ""
    params: Dict[str, str] = field(default_factory=dict)


@dataclass
class BasicConfig:
    """Basic C2Profile configuration."""
    # Request headers
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    # URL parameters
    url_param_name: str = "pass"


@dataclass
class CoreConfig:
    """Core C2Profile configuration."""
    # Request body
    request_body_type: str = "multipart/form-data"
    # Response handling
    response_charset: str = "UTF-8"


@dataclass
class C2Request:
    """Request configuration for C2Profile."""
    # Request method
    method: str = "POST"
    # Custom headers
    headers: Dict[str, str] = field(default_factory=dict)


    # Body parameters
    body_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class C2Response:
    """Response configuration for C2Profile."""
    # Response parsing
    regex_pattern: str = ""
    # Response encoding
    encoding: str = "UTF-8"


@dataclass
class C2Profile:
    """Represents a Godzilla C2Profile configuration."""

    name: str = "default"
    support_payload: List[str] = field(default_factory=lambda: ["JavaDynamicPayload"])
    enabled_static_payload: bool = False
    enabled_custom_generate: bool = False
    custom_generate: C2Generate = field(default_factory=C2Generate)
    static_vars: Dict[str, str] = field(default_factory=dict)
    basic_config: BasicConfig = field(default_factory=BasicConfig)
    core_config: CoreConfig = field(default_factory=CoreConfig)
    request_encryption_chain: str = "hex"
    response_decryption_chain: str = "hex"
    request: C2Request = field(default_factory=C2Request)
    response: C2Response = field(default_factory=C2Response)
    payload_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    plugin_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to YAML-serializable dictionary."""
        return {
            "name": self.name,
            "supportPayload": self.support_payload,
            "enabledStaticPayload": self.enabled_static_payload,
            "enabledCustomGenerate": self.enabled_custom_generate,
            "customGenerate": {
                "template": self.custom_generate.template,
                "params": self.custom_generate.params,
            },
            "staticVars": self.static_vars,
            "basicConfig": {
                "userAgent": self.basic_config.user_agent,
                "urlParamName": self.basic_config.url_param_name,
            },
            "coreConfig": {
                "requestBodyType": self.core_config.request_body_type,
                "responseCharset": self.core_config.response_charset,
            },
            "requestEncryptionChain": self.request_encryption_chain,
            "responseDecryptionChain": self.response_decryption_chain,
            "request": {
                "method": self.request.method,
                "headers": self.request.headers,
                "bodyParams": self.request.body_params,
            },
            "response": {
                "regexPattern": self.response.regex_pattern,
                "encoding": self.response.encoding,
            },
            "payloadConfigs": self.payload_configs,
            "pluginConfigs": self.plugin_configs,
        }

    @classmethod
    def from_yaml_dict(cls, data: Dict[str, Any]) -> "C2Profile":
        """Create from YAML-parsed dictionary."""
        custom_gen = C2Generate(
            template=data.get("customGenerate", {}).get("template", ""),
            params=data.get("customGenerate", {}).get("params", {})
        )
        basic_cfg = BasicConfig(
            user_agent=data.get("basicConfig", {}).get("userAgent", ""),
            url_param_name=data.get("basicConfig", {}).get("urlParamName", "pass"),
        )
        core_cfg = CoreConfig(
            request_body_type=data.get("coreConfig", {}).get("requestBodyType", "multipart/form-data"),
            response_charset=data.get("coreConfig", {}).get("responseCharset", "UTF-8"),
        )

        c2request = C2Request(
            method=data.get("request", {}).get("method", "POST"),
            headers=data.get("request", {}).get("headers", {}),
            body_params=data.get("request", {}).get("bodyParams", {}),
        )
        c2response = C2Response(
            regex_pattern=data.get("response", {}).get("regexPattern", ""),
            encoding=data.get("response", {}).get("encoding", "UTF-8"),
        )

        return cls(
            name=data.get("name", "default"),
            support_payload=data.get("supportPayload", ["JavaDynamicPayload"]),
            enabled_static_payload=data.get("enabledStaticPayload", False),
            enabled_custom_generate=data.get("enabledCustomGenerate", False),
            custom_generate=custom_gen,
            static_vars=data.get("staticVars", {}),
            basic_config=basic_cfg,
            core_config=core_cfg,
            request_encryption_chain=data.get("requestEncryptionChain", "hex"),
            response_decryption_chain=data.get("responseDecryptionChain", "hex"),
            request=c2request,
            response=c2response,
            payload_configs=data.get("payloadConfigs", {}),
            plugin_configs=data.get("pluginConfigs", {}),
        )


def load_profile(name: str) -> Optional[C2Profile]:
    """Load a C2Profile by name.

    Args:
        name: Profile name (without .profile extension)

    Returns:
        C2Profile instance or None if not found
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    profile_dir = project.project_path / "profile"
    profile_file = profile_dir / f"{name}.profile"

    if not profile_file.exists():
        return None

    with open(profile_file, 'r', encoding='utf-8') as f:
        content = f.read()

    data = yaml.safe_load(content)
    if not data:
        return None

    return C2Profile.from_yaml_dict(data)


def save_profile(profile: C2Profile) -> bool:
    """Save a C2Profile.

    Args:
        profile: C2Profile to save

    Returns:
        True if save was successful
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    profile_dir = project.project_path / "profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    profile_file = profile_dir / f"{profile.name}.profile"

    with open(profile_file, 'w', encoding='utf-8') as f:
        yaml.dump(profile.to_yaml_dict(), f, default_flow_style=False)

    return True


def list_profiles() -> List[str]:
    """List all available profiles.

    Returns:
        List of profile names
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    profile_dir = project.project_path / "profile"
    if not profile_dir.exists():
        return []

    profiles = []
    for item in profile_dir.iterdir():
        if item.is_file() and item.suffix == ".profile":
            profiles.append(item.stem)

    return profiles


def delete_profile(name: str) -> bool:
    """Delete a profile.

    Args:
        name: Profile name to delete

    Returns:
        True if deletion was successful
    """
    project = get_current_project()
    if not project or not project.is_open:
        raise RuntimeError("No project open. Use 'project open' first.")

    profile_dir = project.project_path / "profile"
    profile_file = profile_dir / f"{name}.profile"

    if not profile_file.exists():
        return False

    profile_file.unlink()
    return True


def validate_profile(profile: Any) -> Dict[str, Any]:
    """Validate a C2Profile configuration.

    Args:
        profile: C2Profile object or dict to validate

    Returns:
        Dictionary with validation results including 'errors' list
    """
    errors = []
    warnings = []

    # Handle both dict and C2Profile object
    if isinstance(profile, dict):
        profile_dict = profile
    else:
        profile_dict = profile.to_dict() if hasattr(profile, 'to_dict') else {}

    # Check required fields
    if not profile_dict.get('name'):
        errors.append("Profile name is required")

    support_payload = profile_dict.get('supportPayload', [])
    if not support_payload:
        errors.append("At least one supportPayload is required")

    # Validate encryption chains
    valid_encryptions = ["aes128", "aes256", "base64", "hex", "raw", "rsa", "xor"]
    req_enc = profile_dict.get('requestEncryptionChain', '')
    if req_enc and req_enc not in valid_encryptions:
        warnings.append(f"Unknown request encryption: {req_enc}")

    resp_dec = profile_dict.get('responseDecryptionChain', '')
    if resp_dec and resp_dec not in valid_encryptions:
        warnings.append(f"Unknown response decryption: {resp_dec}")

    # Validate payload types
    valid_payloads = ["JavaDynamicPayload", "CSharpDynamicPayload", "PhpDynamicPayload"]
    for payload in support_payload:
        if payload not in valid_payloads:
            warnings.append(f"Unknown payload type: {payload}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def create_default_profile() -> C2Profile:
    """Create a default C2Profile configuration.

    Returns:
        A default C2Profile instance
    """
    return C2Profile(
        name="default",
        support_payload=["JavaDynamicPayload", "CSharpDynamicPayload", "PhpDynamicPayload"],
        enabled_static_payload=False,
        enabled_custom_generate=False,
        custom_generate=C2Generate(),
        static_vars={},
        basic_config=BasicConfig(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url_param_name="pass",
        ),
        core_config=CoreConfig(
            request_body_type="multipart/form-data",
            response_charset="UTF-8",
        ),
        request_encryption_chain="hex",
        response_decryption_chain="hex",
        request=C2Request(
            method="POST",
            headers={},
            body_params={},
        ),
        response=C2Response(
            regex_pattern="",
            encoding="UTF-8",
        ),
        payload_configs={},
        plugin_configs={},
    )
