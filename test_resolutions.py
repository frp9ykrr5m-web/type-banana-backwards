import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pledge
from puzzle_audit import (
    audit_all, caesar_decode, keyed_alphabet, literal_assignment,
    parity, solve_congruences, spiral_read, witness_truths,
)


class PuzzleAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshots = json.loads(Path("issue_snapshots.json").read_text(encoding="utf-8"))
        cls.results = audit_all(cls.snapshots)

    def test_literal_data_does_not_execute_issue_code(self):
        body = "x = [2, 3]\nraise RuntimeError('do not run issue bodies')\n"
        self.assertEqual(literal_assignment(body, "x"), [2, 3])
        with self.assertRaises(ValueError):
            literal_assignment("x = __import__('os').system('unsafe')", "x")

    def test_literal_reader_handles_invalid_surrounding_python(self):
        self.assertEqual(literal_assignment("NOT PYTHON\nx = [\n1, 2,\n]\nnot valid!", "x"), [1, 2])

    def test_debugger_corrupted_cipher_is_preserved(self):
        self.assertEqual(self.results["2"]["stage1_as_posted"], "THE NE[T CLIE IS IN THE NUMBERS")

    def test_keyed_alphabet_is_bijection(self):
        self.assertEqual(keyed_alphabet("KEY"), "KEYABCDFGHIJLMNOPQRSTUVWXZ")
        self.assertEqual(len(set(keyed_alphabet("KEY"))), 26)

    def test_debugger_numeric_clue(self):
        self.assertEqual(self.results["2"]["stage2"], "THE KEY IS STILL HIDDEN")

    def test_spiral_instructions_and_code_are_distinguished(self):
        data = self.results["2"]
        self.assertEqual(data["stage4_letters_only"], "THEPEOTWASTIUZZLNAS")
        self.assertEqual(data["stage4_posted_function"], "THEPEOT!WASTIUZZLNAS")
        self.assertEqual(data["stage5_letters_only"], "SNZUTATEET")
        self.assertEqual(data["stage5_posted_function"], "SNZUTA!OPH")

    def test_spiral_rejects_ragged_grids(self):
        with self.assertRaises(ValueError):
            spiral_read(["A B", "C"])

    def test_archive_variants_have_identical_puzzle_data_results(self):
        self.assertEqual(self.results["3"], self.results["4"])
        self.assertEqual(self.results["4"], self.results["5"])

    def test_archive_caesar_and_number_key_conflict(self):
        self.assertEqual(self.results["3"]["lock1_instruction_key"], 5)
        self.assertEqual(self.results["3"]["lock2_row_shift_values"], [3, 3, 3])
        self.assertEqual(self.results["3"]["lock2_per_row_shift"], "TEHEA PIMH DHAPA")

    def test_shortest_route(self):
        self.assertEqual(self.results["3"]["lock4_first_BFS_route"], "ADGJMPSVYZ")
        self.assertEqual(self.results["3"]["lock4_shortest_edge_count"], 9)

    def test_witnesses_are_impossible_for_any_box(self):
        for box in range(-2, 10):
            self.assertGreaterEqual(sum(witness_truths(box)), 2)
        self.assertEqual(self.results["3"]["lock5_valid_boxes"], [])

    def test_congruences_and_minimality(self):
        items = [(2, 3), (3, 5), (2, 7), (9, 11)]
        self.assertEqual(solve_congruences(items), 548)
        self.assertTrue(all(548 % modulus == remainder for remainder, modulus in items))
        self.assertFalse(any(all(x % modulus == remainder for remainder, modulus in items) for x in range(1, 548)))
        self.assertFalse(self.results["3"]["lock7_direct_index_valid"])

    def test_unsatisfiable_congruences_terminate(self):
        self.assertIsNone(solve_congruences([(0, 2), (1, 2)]))

    def test_real_parity_matches_count_mod_two(self):
        for n in range(256):
            row = format(n, "08b")
            self.assertEqual(parity(row), row.count("1") % 2)
        self.assertEqual(self.results["3"]["lock9_letters"], "AABBABBB")
        self.assertEqual(set(self.results["3"]["lock9_posted_initial_23"]), {22, 23})

    def test_audit_does_not_claim_invalid_puzzles_complete(self):
        self.assertEqual(set(self.results), {"2", "3", "4", "5"})
        self.assertTrue(all(not item["complete"] and item["blockers"] for item in self.results.values()))


class PledgeTests(unittest.TestCase):
    def test_exactly_52_complete_numbered_repetitions(self):
        paragraphs = pledge.render().strip().split("\n\n")
        self.assertEqual(len(paragraphs), 52)
        for i, paragraph in enumerate(paragraphs, 1):
            self.assertEqual(paragraph, f"{i:02d}. {pledge.PLEDGE}")

    def test_generated_deliverable_matches_program(self):
        self.assertEqual(Path("pledge_52.txt").read_text(encoding="utf-8"), pledge.render())

    def test_slow_mode_sleeps_for_every_character(self):
        with patch("pledge.render", return_value="test\n"), patch("pledge.time.sleep") as sleep, patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(pledge.main(["--slow", "--delay", "0.2"]), 0)
            self.assertEqual(out.getvalue(), "test\n")
            self.assertEqual(sleep.call_count, 5)
            sleep.assert_called_with(0.2)

    def test_file_output(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "pledge.txt"
            self.assertEqual(pledge.main(["--output", str(dest)]), 0)
            self.assertEqual(dest.read_text(encoding="utf-8"), pledge.render())


if __name__ == "__main__":
    unittest.main()
