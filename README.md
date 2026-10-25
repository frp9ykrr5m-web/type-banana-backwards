# Type Banana Backwards — issue resolutions

This repository contains reproducible results for issues #2–#6. It uses only the Python standard library and never executes the code pasted into an issue.

## Run

```sh
python puzzle_audit.py
python last_debugger_repaired.py
python -m unittest -v
```

`issue_snapshots.json` preserves the statements that were audited. `audit_results.json` contains the exact machine-readable results; [RESOLUTIONS.md](RESOLUTIONS.md) explains what they mean.

## Issue #6: 52 repetitions

The complete numbered text is in [pledge_52.txt](pledge_52.txt). It contains exactly 52 complete repetitions. To print them with a deliberately slow typewriter effect:

```sh
python pledge.py --slow
```

The default delay is 0.20 seconds per character. Use `--delay 0.5` for a slower pace, or Ctrl+C to stop. The repository does not automatically start this long-running output.

## Status

| Issue | Result |
| --- | --- |
| #2 — The Last Debugger | Original data audited; a separately labeled coherent repaired edition now solves to `THE BUG WAS YOU.` |
| #3 — The Archive of Ten Locks | Determinate locks solved; contradictions and the missing final chain documented. |
| #4 — 2 1/2 | Same literal puzzle data and results as #3; invalid pasted Python is handled as data. |
| #5 — 2 1/2 .2 | Same literal puzzle data and results as #3; the larger number in the print label does not change the computation. |
| #6 — happy bumpy bugger | Complete 52-repetition artifact plus optional slow-output program. |

The repaired edition in `last_debugger_repaired.py` deliberately chooses a new punchline; it does not pretend that answer was recoverable from the original inputs. The original audit remains available. The Archive puzzle issues #3–#5 still need corrected clues.
