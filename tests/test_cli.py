from mac_draw.cli import build_parser


def test_draw_defaults() -> None:
    args = build_parser().parse_args(["draw", "a dragon"])
    assert args.command == "draw"
    assert args.size == "1024x1024"
    assert args.output_dir == "Attachments/gen"
