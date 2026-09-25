import unittest

from mac_draw.cli import build_parser


class CliTests(unittest.TestCase):
    def test_draw_defaults(self) -> None:
        args = build_parser().parse_args(["draw", "a dragon"])
        self.assertEqual(args.command, "draw")
        self.assertEqual(args.size, "1024x1024")
        self.assertIsNone(args.output_dir)


if __name__ == "__main__":
    unittest.main()
