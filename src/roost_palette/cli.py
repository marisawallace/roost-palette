"""roost-palette CLI.

House shape (spec §10): `build_parser()` returns the parser, subcommands dispatch
through `match`, `main(argv)` so tests call it directly. Keep --help/--version instant
— no heavy top-level imports; lazy-import inside handlers.
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roost-palette",
        description="Terminal color palette for the roost fleet: intent-named ANSI roles.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('roost-palette')}"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("swatch", help="print each color role's name in its own color")

    return parser


def _swatch() -> int:
    from roost_palette import detect

    palette = detect()
    for role in ("error", "success", "warn", "info", "heading", "dim"):
        print(getattr(palette, role)(role))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    match args.command:
        case "swatch":
            return _swatch()
        case _:
            build_parser().print_help(sys.stderr)
            return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
