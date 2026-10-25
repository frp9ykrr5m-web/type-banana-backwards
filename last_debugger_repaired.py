"""A coherent repaired edition of issue #2, not a recovered original answer.

The original inputs remain unchanged in issue_snapshots.json and puzzle_audit.py.
This edition deliberately chooses a NEW punchline: THE BUG WAS YOU.
Every stage is connected and solved deterministically without interactive input.
"""
from __future__ import annotations

import json

from puzzle_audit import ALPHABET, caesar_decode, keyed_decode, spiral_read

STAGE1 = "WKH QHAW FOXH LV LQ WKH QXPEHUV"
STAGE2 = "21 19 5 / 8 9 4 4 5 14 / 1 19 / 20 8 5 / 11 5 25"
# HIDDEN is supplied by Stage 2. Mapping A-Z through that keyed alphabet
# encodes SPIRAL as the following ciphertext:
STAGE3 = "SPFRHK"
# Stage 3 supplies the clockwise SPIRAL route. Ignore '#'; keep letters.
GRID = [
    "X U X O X",
    "U X B X Y",
    "X T # E X",
    "G X H X S",
    "X W X A X",
]


def solve() -> dict[str, str | int]:
    candidates = [(shift, caesar_decode(STAGE1, shift)) for shift in range(26)]
    # This puzzle's clue grammar supplies a deterministic candidate check.
    shift, first = next((s, text) for s, text in candidates if text == "THE NEXT CLUE IS IN THE NUMBERS")
    second = " ".join("".join(ALPHABET[int(n) - 1] for n in word.split()) for word in STAGE2.split(" / "))
    words = second.split()
    if words[:1] != ["USE"] or words[2:] != ["AS", "THE", "KEY"]:
        raise ValueError("Stage 2 must name the keyword")
    keyword = words[1]
    route = keyed_decode(STAGE3, keyword)
    if route != "SPIRAL":
        raise ValueError("Stage 3 must specify the grid route")
    fourth = spiral_read(GRID)
    letters = fourth[::-1][::2]
    # Repaired Stage 5 explicitly gives the word lengths 3, 3, 3, 3.
    if len(letters) != 12:
        raise ValueError("Stage 5 requires exactly twelve extracted letters")
    punchline = " ".join(letters[i:i + 3] for i in range(0, 12, 3)) + "."
    return {"shift": shift, "stage1": first, "stage2": second, "keyword": keyword, "stage3": route, "stage4": fourth, "stage5_letters": letters, "punchline": punchline}


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
