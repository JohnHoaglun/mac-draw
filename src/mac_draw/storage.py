"""Safe local vault writes for generated images and reproducibility metadata."""

from __future__ import annotations

import json
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import ClientConfig


@dataclass(frozen=True)
class SavedAsset:
    path: str
    metadata_path: str
    embed: str
    seed: int | None
    session_id: str | None
    parent_image: str | None


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (value[:56] or "image").strip("-")


def _write_atomically(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary_path = Path(handle.name)
        handle.write(data)
    temporary_path.replace(path)


def save_asset(
    config: ClientConfig,
    *,
    image_bytes: bytes,
    prompt: str,
    seed: int | None,
    session_id: str | None,
    parent_image: str | None,
    bridge_metadata: dict[str, Any],
) -> SavedAsset:
    """Write PNG and JSON sidecar atomically beneath the configured vault."""
    vault_path = config.vault_path.resolve()
    output_path = (vault_path / config.output_dir).resolve()
    if vault_path not in output_path.parents and output_path != vault_path:
        raise ValueError("Configured output directory escapes the vault")

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d-%H%M%S")
    stem = f"{timestamp}-{_slug(prompt)}"
    image_path = output_path / f"{stem}.png"
    sequence = 2
    while image_path.exists():
        image_path = output_path / f"{stem}-{sequence}.png"
        sequence += 1
    sidecar_path = image_path.with_suffix(".json")

    _write_atomically(image_path, image_bytes)
    relative_image = image_path.relative_to(vault_path).as_posix()
    relative_sidecar = sidecar_path.relative_to(vault_path).as_posix()
    asset = SavedAsset(
        path=relative_image,
        metadata_path=relative_sidecar,
        embed=f"![[{relative_image}]]",
        seed=seed,
        session_id=session_id,
        parent_image=parent_image,
    )
    metadata = {
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(),
        "prompt": prompt,
        "bridge": bridge_metadata,
        **asdict(asset),
    }
    _write_atomically(sidecar_path, (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return asset
