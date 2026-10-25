"""Generate exactly 52 repetitions; optionally print with a slow typewriter effect."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

PLEDGE = (
    "I pledge allegiance to the Flag of the United States of America, "
    "and to the Republic for which it stands, one Nation under God, indivisible, "
    "with liberty and justice for all."
)
REPETITIONS = 52


def render() -> str:
    return "\n\n".join(f"{i:02d}. {PLEDGE}" for i in range(1, REPETITIONS + 1)) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slow", action="store_true", help="Pause between characters (Ctrl+C stops immediately)")
    parser.add_argument("--delay", type=float, default=0.20, help="Seconds per character in --slow mode (default: 0.20)")
    parser.add_argument("--output", type=Path, help="Write the complete text to a file instead of the terminal")
    args = parser.parse_args(argv)
    if args.delay < 0:
        parser.error("--delay must not be negative")
    text = render()
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    elif args.slow:
        try:
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(args.delay)
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            return 130
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
