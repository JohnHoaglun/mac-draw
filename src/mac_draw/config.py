"""Configuration and macOS Keychain access for the local picture client."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("~/.config/picture/config.toml").expanduser()
DEFAULT_KEYCHAIN_SERVICE = "mac-draw-image-bridge"


class ConfigurationError(ValueError):
    """Raised when the bridge or local vault is not configured."""


@dataclass(frozen=True)
class ClientConfig:
    bridge_url: str
    api_key: str
    vault_path: Path
    output_dir: str = "Attachments/gen"
    timeout_seconds: int = 180
    config_path: Path = DEFAULT_CONFIG_PATH

    @property
    def output_path(self) -> Path:
        return self.vault_path / self.output_dir


def config_path_from_environment() -> Path:
    return Path(os.environ.get("PICTURE_CONFIG", DEFAULT_CONFIG_PATH)).expanduser()


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _keychain_password(service: str) -> str:
    """Read a local macOS Keychain item without ever printing its value."""
    if sys.platform != "darwin":
        return ""
    result = subprocess.run(
        ["security", "find-generic-password", "-a", os.environ.get("USER", ""), "-s", service, "-w"],
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.rstrip("\r\n") if result.returncode == 0 else ""


def _keychain_item_exists(service: str) -> bool:
    if sys.platform != "darwin":
        return False
    result = subprocess.run(
        ["security", "find-generic-password", "-a", os.environ.get("USER", ""), "-s", service],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def load_config(path: Path | None = None) -> ClientConfig:
    """Load config; environment overrides the local Keychain, then TOML settings."""
    config_path = path or config_path_from_environment()
    data = _read_toml(config_path)
    bridge = data.get("bridge", {})
    vault = data.get("vault", {})

    bridge_url = os.environ.get("PICTURE_BRIDGE_URL", bridge.get("url", "")).rstrip("/")
    vault_value = os.environ.get("PICTURE_VAULT_PATH", vault.get("path", ""))
    output_dir = os.environ.get("PICTURE_OUTPUT_DIR", vault.get("output_dir", "Attachments/gen"))
    key_env = bridge.get("api_key_env", "PICTURE_API_KEY")
    keychain_service = bridge.get("keychain_service", DEFAULT_KEYCHAIN_SERVICE)
    api_key = os.environ.get(key_env, "") or _keychain_password(keychain_service)
    timeout = int(os.environ.get("PICTURE_TIMEOUT_SECONDS", bridge.get("timeout_seconds", 180)))

    missing = []
    if not bridge_url:
        missing.append("bridge.url (or PICTURE_BRIDGE_URL)")
    if not vault_value:
        missing.append("vault.path (or PICTURE_VAULT_PATH)")
    if not api_key:
        missing.append(f"Keychain item {keychain_service!r} or environment variable {key_env}")
    if missing:
        raise ConfigurationError("Missing " + ", ".join(missing) + f". Configure {config_path}.")

    vault_path = Path(vault_value).expanduser().resolve()
    if not vault_path.is_dir():
        raise ConfigurationError(f"Vault path does not exist or is not a directory: {vault_path}")
    output_path = Path(output_dir)
    if output_path.is_absolute() or ".." in output_path.parts:
        raise ConfigurationError("vault.output_dir must be a relative path inside the vault")
    if timeout <= 0:
        raise ConfigurationError("bridge.timeout_seconds must be positive")

    return ClientConfig(
        bridge_url=bridge_url,
        api_key=api_key,
        vault_path=vault_path,
        output_dir=output_dir,
        timeout_seconds=timeout,
        config_path=config_path,
    )


def safe_config_summary(path: Path | None = None) -> dict[str, object]:
    """Return a non-secret configuration summary suitable for terminal output."""
    config_path = path or config_path_from_environment()
    data = _read_toml(config_path)
    bridge = data.get("bridge", {})
    vault = data.get("vault", {})
    key_env = bridge.get("api_key_env", "PICTURE_API_KEY")
    keychain_service = bridge.get("keychain_service", DEFAULT_KEYCHAIN_SERVICE)
    return {
        "config_path": str(config_path),
        "exists": config_path.exists(),
        "bridge_url": os.environ.get("PICTURE_BRIDGE_URL", bridge.get("url")),
        "vault_path": os.environ.get("PICTURE_VAULT_PATH", vault.get("path")),
        "output_dir": os.environ.get("PICTURE_OUTPUT_DIR", vault.get("output_dir", "Attachments/gen")),
        "api_key_environment_variable": key_env,
        "api_key_present_in_environment": bool(os.environ.get(key_env)),
        "keychain_service": keychain_service,
        "keychain_item_present": _keychain_item_exists(keychain_service),
    }


SAMPLE_CONFIG = '''# The bridge token is read automatically from this macOS Keychain service.
# PICTURE_API_KEY remains an optional temporary override for automation.

[bridge]
url = "http://192.168.4.52:8092"
api_key_env = "PICTURE_API_KEY"
keychain_service = "mac-draw-image-bridge"
timeout_seconds = 180

[vault]
path = "/Users/johnhoaglun/Library/Mobile Documents/iCloud~md~obsidian/Documents/JH_Home_Obsidian"
output_dir = "Attachments/gen"
'''
