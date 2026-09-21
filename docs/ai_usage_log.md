# AI usage log — QXU6028 virtual lab, group G06

Record every substantive AI use. Disclosure does not reduce marks;
unverified output and undisclosed use may.

| Date / phase | Tool / model | Purpose | Prompt / instruction summary | Output used / changed / rejected | Checked by |
|---|---|---|---|---|---|
| 2026-09-21 / all | Kimi Code CLI (Kimi) | Implement the full L1-L3 analysis pipeline, checkpoint packaging, and repo scaffolding | Implement per the Practical Methods Guide: L1 band-edge vs Fermi-referenced integrals with published gate ratios; L2 nearest-curve fit in separately normalised (R_H, R_xx) space with cone + hard-gap library, 15% selection rule, 200-replicate bootstrap; L3 Tikhonov reconstruction with zero-mean projection, eta sensitivity, point-spread resolution, noise-linked detection limit | Used after verification: all gate assertions run and pass; L1 ratios 1.00/2.00/2.60/5.10 confirmed; L2 zero-crossing preserved, trajectory length 55; L3 map zero-mean, 100 finite values, A row sums < 1e-11. Changed: feature amplitude made signed; L1 figure annotation overlap fixed. Rejected: nothing outright | (name) |
| 2026-09-21 / tooling | Kimi Code CLI (Kimi) | Checkpoint zip packaging script | Package results.json + phase figures + brief note + commit_hash.txt as G06_L{1,2,3}_Checkpoint.zip | Used after fixing a `zipfile.ZIP_DEFLATED` typo (see error ledger) | (name) |
| 2026-09-21 / verification | Kimi Code CLI (Kimi) | Reproducibility and blind-readiness checks | Clean-clone rerun of reproduce.py; pipeline run against a different group's data to prove no group-specific hardcoding | Used: clean clone regenerates identical results.json; G01 dry run selects a different (cone) model, confirming data-driven selection. Other-group outputs kept in /tmp only, never committed | (name) |

Notes for the group:
- Add one row for every further AI conversation (report drafting, figure tweaks,
  debugging). Include what was checked, not only what was asked.
- "(name)" must be replaced by the member who ran the physical/numerical checks.
