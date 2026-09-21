# QXU6028 Polymer Devices — Virtual Lab (Group G06)

Reproducible analysis pipeline for the graphene-on-sapphire characterisation
coursework: L1 forward carrier counting, L2 zero-D inverse (DoS class, gap,
Fermi-level trajectory), L3 two-D uniformity map, and the Session 3 blind test.

## Setup

```bash
python -m pip install -r requirements.txt   # numpy, pandas, matplotlib
```

Raw data live in `data/regular_G06/` and are sha256-verified against the
supplied manifest on every load. Never edit files in `data/`.

## Reproduce every number and figure

```bash
python reproduce.py --data-dir data/regular_G06 --spec <THRESHOLD>
```

- Writes `results.json` (schema of the supplied `results_template.json`),
  `diagnostics.json`, and `figures/*.png`. These are build artifacts: they are
  git-ignored and regenerated at the current HEAD, so `pipeline_commit` always
  matches the commit that produced them.
- `--spec` is the L3 pass/fail threshold announced in Session 3; without it the
  pass/fail fields stay null and a warning is printed.
- `--seed` (default 12345) controls the L2 bootstrap and L3 noise ensemble.
- `pipeline_commit` is filled from `git rev-parse HEAD` automatically.
- All phase gates are assertions: L1 reference ratios (1.00 / 2.00 / 2.60 /
  5.10), L2 zero-crossing preservation and trajectory length, L3 matrix shape,
  row-sum and zero-mean checks. A failed gate aborts the run.

## Checkpoints

```bash
python reproduce.py            # refresh results.json + figures
git add -A && git commit -m "..."
python scripts/make_checkpoint.py L1   # or L2, L3
```

Produces `checkpoints/G06_L1_Checkpoint.zip` with results.json, the phase
figure(s), the brief note from `docs/checkpoint_notes/`, and commit_hash.txt.
The script refuses to package if results.json was not produced by HEAD.

## Session 3 blind test

```bash
unzip QXU6028_All_Groups_Blind_Test_Data_2026-27.zip   # outside this repo
python reproduce.py --data-dir /path/to/blind_G06 --spec <ANNOUNCED> \
    --out blind_results.json | tee run_log.txt
git rev-parse HEAD > pipeline_commit.txt
```

Upload `blind_results.json`, `run_log.txt`, `pipeline_commit.txt` as three
separate files before the hard close. Freeze the pipeline commit beforehand;
only the data path and spec may change on the day.

## Layout

```
src/constants.py   physical constants, fermi()
src/dataload.py    loading + manifest/shape/sha256 checks
src/l1.py          band-edge vs Fermi-referenced counting (+ closed form)
src/l2.py          model library, nearest-curve fit, 15% rule, bootstrap
src/l3.py          Tikhonov reconstruction, resolution, detection limit
src/figures.py     all figures
src/checks.py      results.json schema validation
docs/              AI usage log, AI error ledger, contribution statement,
                   self-assessment, checkpoint notes
```

## Process rules (from the assessment brief)

- No hand-edited numbers: every value in results.json comes from the pipeline.
- AI use is permitted and expected; log every substantive use in
  `docs/ai_usage_log.md` and every detected error in `docs/ai_error_ledger.md`.
- Do not share data, code or figures between groups.
- Final deadline: Tuesday 24 November 2026, 22:00 UK time.
