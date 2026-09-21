#!/usr/bin/env python3
"""Package a QMplus checkpoint zip for one phase.

Usage:
    python scripts/make_checkpoint.py L1|L2|L3

Requires reproduce.py to have been run first (results.json + figures/).
The brief note is taken from docs/checkpoint_notes/<PHASE>_note.md.
Output: checkpoints/G06_<PHASE>_Checkpoint.zip (group read from results.json).
"""
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONTENTS = {
    "L1": ["results.json", "figures/L1_correction_sweep.png"],
    "L2": ["results.json", "figures/L2_model_fit.png", "figures/L2_trajectory.png"],
    "L3": ["results.json", "figures/L3_map.png", "figures/L3_method.png"],
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in CONTENTS:
        sys.exit("usage: make_checkpoint.py L1|L2|L3")
    phase = sys.argv[1]

    results = json.loads((ROOT / "results.json").read_text())
    group = results["group"]
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
        cwd=ROOT,
    ).stdout.strip()
    assert results["pipeline_commit"] == commit, (
        f"results.json was produced by {results['pipeline_commit'][:8]} but HEAD is "
        f"{commit[:8]}: rerun reproduce.py and commit before packaging"
    )

    note = ROOT / "docs" / "checkpoint_notes" / f"{phase}_note.md"
    assert note.exists(), f"missing brief note: {note}"

    out_dir = ROOT / "checkpoints"
    out_dir.mkdir(exist_ok=True)
    zip_path = out_dir / f"{group}_{phase}_Checkpoint.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in CONTENTS[phase]:
            f = ROOT / rel
            assert f.exists(), f"missing {rel}: run reproduce.py first"
            z.write(f, f.name)
        z.write(note, f"{phase}_note.md")
        z.writestr("commit_hash.txt", commit + "\n")
    print(f"wrote {zip_path}")


if __name__ == "__main__":
    main()
