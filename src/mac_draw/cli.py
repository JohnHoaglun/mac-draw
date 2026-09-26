"""Human-friendly command-line entry point for the local picture client."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .bridge import BridgeClient, BridgeError
from .config import ConfigurationError, SAMPLE_CONFIG, load_config, safe_config_summary
from .storage import save_asset

_COMMANDS = {"draw", "edit", "config"}
_NATURAL_DRAW_PREFIX = re.compile(
    r"^\s*(?:draw|create|make|generate)\s+(?:a\s+|an\s+)?(?:picture|image)(?:\s+of)?\s+",
    re.IGNORECASE,
)


def _human_draw_argv(argv: list[str]) -> list[str]:
    """Turn `mac-draw "draw a picture of …"` into the normal draw command."""
    if not argv or argv[0] in _COMMANDS or argv[0].startswith("-"):
        return argv
    prompt = _NATURAL_DRAW_PREFIX.sub("", argv[0]).strip() or argv[0]
    return ["draw", prompt, *argv[1:]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mac-draw",
        description="Draw an image locally: mac-draw 'draw a picture of a red dragon at sunset'.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    draw = subparsers.add_parser("draw", help="Generate a new image.")
    draw.add_argument("prompt")
    draw.add_argument("--size", default="1024x1024")
    draw.add_argument("--seed", type=int)
    draw.add_argument("--session-id")
    draw.add_argument("--output-dir")
    draw.add_argument("--json", action="store_true", dest="as_json")

    edit = subparsers.add_parser("edit", help="Reserved until native image edits are enabled.")
    edit.add_argument("image", type=Path)
    edit.add_argument("prompt")
    edit.add_argument("--seed", type=int)
    edit.add_argument("--session-id")
    edit.add_argument("--output-dir")
    edit.add_argument("--json", action="store_true", dest="as_json")

    config = subparsers.add_parser("config", help="Inspect local client configuration.")
    config_subparsers = config.add_subparsers(dest="config_command", required=True)
    config_subparsers.add_parser("show", help="Show resolved configuration without secrets.")
    config_subparsers.add_parser("sample", help="Print a sample configuration file.")
    return parser


def _emit(value: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {item}")
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(_human_draw_argv(raw_argv))
    if args.command == "config":
        if args.config_command == "sample":
            print(SAMPLE_CONFIG, end="")
        else:
            _emit(safe_config_summary(), True)
        return 0
    if args.command == "edit":
        print("mac-draw: image editing is not enabled yet; use draw for a new image.", file=sys.stderr)
        return 2

    try:
        config = load_config()
    except ConfigurationError as exc:
        print(f"mac-draw: configuration error: {exc}", file=sys.stderr)
        return 1
    if args.output_dir:
        config = config.__class__(**{**config.__dict__, "output_dir": args.output_dir})

    try:
        result = BridgeClient(config).generate(
            prompt=args.prompt, size=args.size, seed=args.seed, session_id=args.session_id
        )
        asset = save_asset(
            config,
            image_bytes=result.image_bytes,
            prompt=args.prompt,
            seed=args.seed,
            session_id=args.session_id or result.metadata.get("session_id"),
            parent_image=None,
            bridge_metadata=result.metadata,
        )
    except (BridgeError, OSError, ValueError) as exc:
        print(f"mac-draw: {exc}", file=sys.stderr)
        return 1

    _emit({"status": "saved", **asset.__dict__}, args.as_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
