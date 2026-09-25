"""Configuration loading for the macOS-local picture client."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("~/.config/picture/config.toml").expanduser()


class ConfigurationError(ValueError):
    """Raised when the client is not configured for a bridge and vault."""


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


def load_config(path: Path | None = None) -> ClientConfig:
    """Load configuration, allowing environment variables to override TOML."""
    config_path = path or config_path_from_environment()
    data = _read_toml(config_path)
    bridge = data.get("bridge", {})
    vault = data.get("vault", {})

    bridge_url = os.environ.get("PICTURE_BRIDGE_URL", bridge.get("url", "")).rstrip("/")
    vault_value = os.environ.get("PICTURE_VAULT_PATH", vault.get("path", ""))
    output_dir = os.environ.get("PICTURE_OUTPUT_DIR", vault.get("output_dir", "Attachments/gen"))
    key_env = bridge.get("api_key_env", "PICTURE_API_KEY")
    api_key = os.environ.get(key_env, "")
    timeout = int(os.environ.get("PICTURE_TIMEOUT_SECONDS", bridge.get("timeout_seconds", 180)))

    missing = []
    if not bridge_url:
        missing.append("bridge.url (or PICTURE_BRIDGE_URL)")
    if not vault_value:
        missing.append("vault.path (or PICTURE_VAULT_PATH)")
    if not api_key:
        missing.append(f"environment variable {key_env}")
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
    """Return a non-secret summary suitable for terminal or JSON output."""
    config_path = path or config_path_from_environment()
    data = _read_toml(config_path)
    bridge = data.get("bridge", {})
    vault = data.get("vault", {})
    key_env = bridge.get("api_key_env", "PICTURE_API_KEY")
    return {
        "config_path": str(config_path),
        "exists": config_path.exists(),
        "bridge_url": os.environ.get("PICTURE_BRIDGE_URL", bridge.get("url")),
        "vault_path": os.environ.get("PICTURE_VAULT_PATH", vault.get("path")),
        "output_dir": os.environ.get("PICTURE_OUTPUT_DIR", vault.get("output_dir", "Attachments/gen")),
        "api_key_environment_variable": key_env,
        "api_key_present": bool(os.environ.get(key_env)),
    }


SAMPLE_CONFIG = '''# Keep the API key in the macOS Keychain or environment, not in this file.\n\n[bridge]\nurl = "https://spark.local:8091"\napi_key_env = "PICTURE_API_KEY"\ntimeout_seconds = 180\n\n[vault]\npath = "/Users/johnhoaglun/Library/Mobile Documents/iCloud~md~obsidian/Documents/JH_Home_Obsidian"\noutput_dir = "Attachments/gen"\n'''
