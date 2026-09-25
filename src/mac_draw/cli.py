"""Command-line entry point for the local picture client.

The initial scaffold deliberately exposes the user-facing command surface before
binding it to a deployed image bridge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
    draw.add_argument("--output-dir", default="Attachments/gen")
    draw.add_argument("--json", action="store_true", dest="as_json")

    edit = subparsers.add_parser("edit", help="Edit an existing local image.")
    edit.add_argument("image", type=Path)
    edit.add_argument("prompt")
    edit.add_argument("--seed", type=int)
    edit.add_argument("--session-id")
    edit.add_argument("--output-dir", default="Attachments/gen")
    edit.add_argument("--json", action="store_true", dest="as_json")

    config = subparsers.add_parser("config", help="Inspect local client configuration.")
    config_subparsers = config.add_subparsers(dest="config_command", required=True)
    config_subparsers.add_parser("show", help="Show the resolved configuration without secrets.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "config":
        print(json.dumps({"status": "not configured", "config_path": "~/.config/picture/config.toml"}))
        return 0

    # The API client is added only after the authenticated bridge contract exists.
    request = {
        "operation": args.command,
        "prompt": args.prompt,
        "size": getattr(args, "size", None),
        "seed": args.seed,
        "session_id": args.session_id,
        "output_dir": args.output_dir,
    }
    if args.command == "edit":
        request["image"] = str(args.image)

    message = "Image bridge is not configured or deployed yet."
    if args.as_json:
        print(json.dumps({"status": "pending_bridge", "request": request, "message": message}))
    else:
        print(message)
        print("Request preview:")
        print(json.dumps(request, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
