"""Command-line entry point for the local picture client."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .bridge import BridgeClient, BridgeError
from .config import ConfigurationError, SAMPLE_CONFIG, load_config, safe_config_summary
from .storage import save_asset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="picture",
        description="Create and edit images through a configured LAN image bridge.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    draw = subparsers.add_parser("draw", help="Generate a new image.")
    draw.add_argument("prompt")
    draw.add_argument("--size", default="1024x1024")
    draw.add_argument("--seed", type=int)
    draw.add_argument("--session-id")
    draw.add_argument("--output-dir")
    draw.add_argument("--json", action="store_true", dest="as_json")

    edit = subparsers.add_parser("edit", help="Edit an existing local image.")
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
        return
    if isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {item}")
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "config":
        if args.config_command == "sample":
            print(SAMPLE_CONFIG, end="")
        else:
            _emit(safe_config_summary(), True)
        return 0

    try:
        config = load_config()
    except ConfigurationError as exc:
        print(f"picture: configuration error: {exc}", file=sys.stderr)
        return 1
    if args.output_dir:
        config = config.__class__(**{**config.__dict__, "output_dir": args.output_dir})

    bridge = BridgeClient(config)
    try:
        if args.command == "draw":
            result = bridge.generate(
                prompt=args.prompt, size=args.size, seed=args.seed, session_id=args.session_id
            )
            parent_image = None
        else:
            source_path = args.image.expanduser().resolve()
            if not source_path.is_file():
                print(f"picture: image not found: {source_path}", file=sys.stderr)
                return 1
            result = bridge.edit(
                prompt=args.prompt,
                image_bytes=source_path.read_bytes(),
                image_name=source_path.name,
                seed=args.seed,
                session_id=args.session_id,
            )
            try:
                parent_image = source_path.relative_to(config.vault_path).as_posix()
            except ValueError:
                parent_image = str(source_path)
        asset = save_asset(
            config,
            image_bytes=result.image_bytes,
            prompt=args.prompt,
            seed=args.seed,
            session_id=args.session_id or result.metadata.get("session_id"),
            parent_image=parent_image,
            bridge_metadata=result.metadata,
        )
    except (BridgeError, OSError, ValueError) as exc:
        print(f"picture: {exc}", file=sys.stderr)
        return 1

    payload = {"status": "saved", **asset.__dict__}
    _emit(payload, args.as_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
