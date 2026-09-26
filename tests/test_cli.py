import unittest

from mac_draw.cli import _human_draw_argv, build_parser


class CliTests(unittest.TestCase):
    def test_explicit_draw_defaults(self) -> None:
        args = build_parser().parse_args(["draw", "a dragon"])
        self.assertEqual(args.command, "draw")
        self.assertEqual(args.size, "1024x1024")

    def test_human_draw_sentence_becomes_draw_command(self) -> None:
        args = build_parser().parse_args(
            _human_draw_argv(["draw a picture of a red dragon over a sunset field"])
        )
        self.assertEqual(args.command, "draw")
        self.assertEqual(args.prompt, "a red dragon over a sunset field")

    def test_existing_command_is_unchanged(self) -> None:
        self.assertEqual(_human_draw_argv(["config", "show"]), ["config", "show"])


if __name__ == "__main__":
    unittest.main()
