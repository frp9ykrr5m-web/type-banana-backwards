"""Reproduce the posted puzzles without executing code from issue bodies.

Only literal puzzle data is extracted. No network access or dependencies.
The audit deliberately does not invent missing clues or a final punchline.
"""
from __future__ import annotations

import argparse
import ast
from collections import deque
from math import lcm
from pathlib import Path
import json
import re

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HERE = Path(__file__).resolve().parent


def literal_assignment(body: str, name: str):
    """Read a literal assignment even when surrounding pasted Python is invalid."""
    match = re.search(rf"^{re.escape(name)}\s*=\s*(.*)", body, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing assignment: {name}")
    lines = body[match.start(1):].splitlines()
    for end in range(1, len(lines) + 1):
        try:
            return ast.literal_eval("\n".join(lines[:end]))
        except (SyntaxError, ValueError):
            pass
    raise ValueError(f"No valid literal assignment: {name}")


def caesar_decode(text: str, shift: int) -> str:
    return "".join(ALPHABET[(ALPHABET.index(c) - shift) % 26] if c in ALPHABET else c for c in text)


def keyed_alphabet(keyword: str) -> str:
    letters = "".join(dict.fromkeys(c for c in keyword.upper() if c in ALPHABET))
    return letters + "".join(c for c in ALPHABET if c not in letters)


def keyed_decode(ciphertext: str, keyword: str) -> str:
    table = dict(zip(keyed_alphabet(keyword), ALPHABET))
    return "".join(table.get(c, c) for c in ciphertext)


def spiral_read(rows: list[str], punctuation: bool = False) -> str:
    matrix = [row.split() for row in rows]
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("Grid must be a non-empty rectangle")
    out = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        out.extend(matrix[top][left:right + 1]); top += 1
        out.extend(matrix[row][right] for row in range(top, bottom + 1)); right -= 1
        if top <= bottom:
            out.extend(matrix[bottom][col] for col in range(right, left - 1, -1)); bottom -= 1
        if left <= right:
            out.extend(matrix[row][left] for row in range(bottom, top - 1, -1)); left += 1
    return "".join(c for c in out if c.isalpha() or (punctuation and c in "!?.,"))


def shortest_paths(graph: dict[str, list[str]], start: str, goal: str) -> list[list[str]]:
    queue = deque([[start]])
    found = []
    best = None
    while queue:
        path = queue.popleft()
        if best is not None and len(path) > best:
            break
        if path[-1] == goal:
            best = len(path); found.append(path); continue
        for neighbor in graph[path[-1]]:
            if neighbor not in path:
                queue.append(path + [neighbor])
    return found


def solve_congruences(items: list[tuple[int, int]]) -> int | None:
    period = lcm(*(modulus for _, modulus in items))
    return next((x for x in range(1, period + 1) if all(x % m == r % m for r, m in items)), None)


def witness_truths(box: int) -> list[bool]:
    return [box != 1, box == 2, box != 2, box == 4, box != 4]


def parity(row: str, initial: int = 0) -> int:
    if not row or any(bit not in "01" for bit in row):
        raise ValueError("Expected a non-empty binary row")
    result = initial
    for bit in row:
        result ^= int(bit)
    return result


def audit_debugger(body: str) -> dict:
    data = {k: literal_assignment(body, k) for k in ("stage1", "stage2", "stage3", "grid")}
    words = data["stage2"].split(" / ")
    numbers = " ".join("".join(ALPHABET[int(n) - 1] for n in word.split()) for word in words)
    letters = spiral_read(data["grid"])
    with_punctuation = spiral_read(data["grid"], punctuation=True)
    return {
        "stage1_shift": 3,
        "stage1_as_posted": caesar_decode(data["stage1"], 3),
        "stage2": numbers,
        "stage3_with_supplied_key_KEY": keyed_decode(data["stage3"], "KEY"),
        "stage3_with_stage2_word_HIDDEN": keyed_decode(data["stage3"], "HIDDEN"),
        "stage4_letters_only": letters,
        "stage4_posted_function": with_punctuation,
        "stage5_letters_only": letters[::-1][::2],
        "stage5_posted_function": with_punctuation[::-1][::2],
        "complete": False,
        "blockers": [
            "Stage 1 contains '[' and FOLH; shift 3 gives a corrupted clue rather than NEXT CLUE.",
            "Stage 2 does not identify an unambiguous keyword; the supplied code separately hard-codes KEY.",
            "The supplied keyed ciphertext and spiral do not yield the promised final sentence.",
            "Stage 4 prose says letters only, but the supplied function keeps punctuation; the two final transforms differ.",
        ],
    }


def audit_archive(body: str) -> dict:
    names = ("lock1", "lock2", "lock3_keyword", "lock3_cipher", "graph", "congruences", "book_phrase", "lock8_letters", "bit_rows")
    d = {name: literal_assignment(body, name) for name in names}
    decoded_per_row = " ".join("".join(ALPHABET[(n - row[0]) % 26] for n in row[1:]) for row in d["lock2"])
    decoded_shift5 = " ".join("".join(ALPHABET[(n - 5) % 26] for n in row[1:]) for row in d["lock2"])
    x = solve_congruences(d["congruences"])
    paths = shortest_paths(d["graph"], "A", "Z")
    bits = [parity(row) for row in d["bit_rows"]]
    return {
        "lock1_shift": 3,
        "lock1": caesar_decode(d["lock1"], 3),
        "lock1_instruction_key": len("SHIFT"),
        "lock2_row_shift_values": [row[0] for row in d["lock2"]],
        "lock2_per_row_shift": decoded_per_row,
        "lock2_using_previous_answer_5": decoded_shift5,
        "lock3_with_supplied_keyword_TRACE": keyed_decode(d["lock3_cipher"], d["lock3_keyword"]),
        "lock4_first_BFS_route": "".join(paths[0]),
        "lock4_shortest_edge_count": len(paths[0]) - 1,
        "lock4_number_of_shortest_routes": len(paths),
        "lock5_truth_counts_boxes_1_to_4": [sum(witness_truths(b)) for b in range(1, 5)],
        "lock5_valid_boxes": [b for b in range(1, 5) if sum(witness_truths(b)) == 1],
        "lock6_smallest_positive_x": x,
        "lock7_word_count": len(d["book_phrase"].split()),
        "lock7_direct_index_valid": 1 <= x <= len(d["book_phrase"].split()),
        "lock8_anagrams": ["TRACE", "REACT", "CATER", "CARET", "CARTE", "CRATE"],
        "lock9_correct_parity": bits,
        "lock9_letters": "".join("AB"[n] for n in bits),
        "lock9_posted_initial_23": [parity(row, initial=23) for row in d["bit_rows"]],
        "complete": False,
        "blockers": [
            "Lock 1 implies key 5, but Lock 2 embeds 3 in every row; neither interpretation yields a readable clue.",
            "Lock 3 hard-codes TRACE rather than a valid answer from Lock 2; decoding its ciphertext gives no usable instruction.",
            "Lock 5 is logically impossible: Bo/Cy guarantee one truth and Dee/Eli guarantee another, so there are always at least two truths.",
            f"Lock 6 yields {x}, outside the {len(d['book_phrase'].split())}-word Lock 7 phrase. No rule says to split its digits or wrap the index.",
            "The supplied parity function starts at 23 instead of 0, producing 22/23 rather than binary parity.",
            "Lock 10 cannot be assembled from missing/contradictory answers; a final punchline is not determined by the posted data.",
        ],
    }


def audit_all(snapshots: list[dict]) -> dict:
    results = {}
    for issue in snapshots:
        number = issue["number"]
        if number == 2:
            results[str(number)] = audit_debugger(issue["body"])
        elif number in (3, 4, 5):
            results[str(number)] = audit_archive(issue["body"])
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshots", type=Path, default=HERE / "issue_snapshots.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit_all(json.loads(args.snapshots.read_text(encoding="utf-8")))
    content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
