"""HTTP client for the image bridge contract."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import ClientConfig


class BridgeError(RuntimeError):
    """Raised when the bridge cannot accept or complete a request."""


@dataclass(frozen=True)
class ImageResult:
    image_bytes: bytes
    metadata: dict[str, Any]


class BridgeClient:
    """Talk to the authenticated LAN bridge using a small OpenAI-like contract."""

    def __init__(self, config: ClientConfig) -> None:
        self.config = config

    def generate(self, *, prompt: str, size: str, seed: int | None, session_id: str | None) -> ImageResult:
        payload: dict[str, Any] = {"prompt": prompt, "size": size}
        if seed is not None:
            payload["seed"] = seed
        if session_id:
            payload["session_id"] = session_id
        return self._post("/v1/images/generations", payload)

    def edit(
        self,
        *,
        prompt: str,
        image_bytes: bytes,
        image_name: str,
        seed: int | None,
        session_id: str | None,
    ) -> ImageResult:
        payload: dict[str, Any] = {
            "prompt": prompt,
            "image_b64": base64.b64encode(image_bytes).decode("ascii"),
            "image_name": image_name,
        }
        if seed is not None:
            payload["seed"] = seed
        if session_id:
            payload["session_id"] = session_id
        return self._post("/v1/images/edits", payload)

    def _post(self, endpoint: str, payload: dict[str, Any]) -> ImageResult:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.config.bridge_url + endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:  # noqa: S310 -- configured LAN endpoint
                raw_response = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise BridgeError(f"Bridge returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise BridgeError(f"Could not reach image bridge: {exc.reason}") from exc

        try:
            response_data = json.loads(raw_response)
            encoded_image = response_data["data"][0]["b64_json"]
            image_bytes = base64.b64decode(encoded_image, validate=True)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BridgeError("Bridge response did not contain data[0].b64_json") from exc
        if not image_bytes:
            raise BridgeError("Bridge returned an empty image")
        metadata = response_data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {"bridge_metadata": metadata}
        return ImageResult(image_bytes=image_bytes, metadata=metadata)
