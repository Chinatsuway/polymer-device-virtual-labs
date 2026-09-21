#!/usr/bin/env python3
"""One-command reproduction pipeline for the QXU6028 virtual lab (group G06).

Usage:
    python reproduce.py --data-dir data/regular_G06 --spec <THRESHOLD> [--seed 12345]

Regenerates every reported number and figure from the raw group data.
For the Session 3 blind test, point --data-dir at the blind_G06 folder and
pass the announced specification via --spec. Do not edit any value by hand.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import figures
from checks import validate_results
from dataload import load_group_data
from l1 import run_l1
from l2 import run_l2
from l3 import run_l3


def git_commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "UNKNOWN"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data/regular_G06")
    parser.add_argument("--spec", type=float, default=None,
                        help="L3 pass/fail specification threshold (announced in Session 3)")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--out", default="results.json")
    parser.add_argument("--figures-dir", default="figures")
    args = parser.parse_args()

    print(f"[pipeline] data dir: {args.data_dir}")
    print(f"[pipeline] seed: {args.seed}")

    data = load_group_data(args.data_dir)
    group = data["group"]
    print(f"[pipeline] group: {group}, dataset set: {data['dataset_set']}")

    print("[L1] forward carrier counting ...")
    l1 = run_l1(data["l1_data"], data["l1_params"])
    print(f"[L1] gate checks passed (ratios 1.00 / 2.00 / 2.60 / 5.10)")
    print(f"[L1] correction factor at E_F={l1['EF_op_eV']:.6f} eV: {l1['correction_factor']:.4f}")
    print(f"[L1] n_Fermi(op) = {l1['n_fermi_op_cm2']:.6e} cm^-2")
    print(f"[L1] corrected mobility = {l1['mobility_corrected_cm2_Vs']:.4f} cm^2 V^-1 s^-1")

    print("[L2] zero-dimensional inverse ...")
    l2 = run_l2(data["l2_data"], data["l2_meta"], data["l1_params"]["c"], seed=args.seed)
    n_idx = len(l2["measurement_index"])
    print(f"[L2] {n_idx} measurement indices; R_H zero-crossing bracket: "
          f"{l2['zero_crossing_bracket']}")
    print(f"[L2] selected model: {l2['model']}, E_g/kT = {l2['Eg_kT']:.2f} "
          f"+/- {l2['Eg_uncertainty_kT']:.2f} (bootstrap 16-84%)")
    print(f"[L2] residuals: cone={l2['r_cone']:.4f}, selected={l2['r_selected']:.4f}; "
          f"hard-gap fraction={l2['hard_gap_fraction']:.2f}")
    print(f"[L2] wing log-log slope |R_H| vs R_xx: {l2['wing_loglog_slope']:.2f} "
          f"(ideal cone: 2)")

    print("[L3] two-dimensional inverse ...")
    l3 = run_l3(data["A"], data["d_reps"], spec=args.spec, seed=args.seed)
    print(f"[L3] eta0 = {l3['eta0']:.4e}; map mean ~ 0, 100 finite values")
    for f in l3["features"]:
        print(f"[L3] feature: {f['sign']} amplitude {f['amplitude']:+.4f} at "
              f"({f['x']:+.2f}, {f['y']:+.2f}) probe pitches")
    print(f"[L3] resolution = {l3['resolution_probe_pitch']:.2f} probe pitches; "
          f"detection limit d95 = {l3['detection_limit']:.3e}")
    if args.spec is None:
        print("[L3] WARNING: --spec not given; pass/fail left null until the "
              "Session 3 specification is announced")
    else:
        print(f"[L3] pass/fail vs spec={args.spec}: {l3['confidence']}")

    commit = git_commit()
    results = {
        "schema_version": "QXU6028-results-v1",
        "group": group,
        "dataset_set": data["dataset_set"],
        "pipeline_commit": commit,
        "L1": {
            "correction_factor": l1["correction_factor"],
            "n_fermi_op_cm2": l1["n_fermi_op_cm2"],
            "mobility_corrected_cm2_Vs": l1["mobility_corrected_cm2_Vs"],
        },
        "L2": {
            "model": l2["model"],
            "Eg_kT": l2["Eg_kT"],
            "Eg_uncertainty_kT": l2["Eg_uncertainty_kT"],
            "EF_trajectory_eV": l2["EF_trajectory_eV"],
        },
        "L3": {
            "map": l3["map"],
            "features": [
                {k: f[k] for k in ("sign", "x", "y", "amplitude")} for f in l3["features"]
            ],
            "resolution_probe_pitch": l3["resolution_probe_pitch"],
            "detection_limit_fraction": l3["detection_limit_fraction"],
            "pass": l3["pass"],
            "confidence": l3["confidence"],
        },
    }
    validate_results(results, Path(args.data_dir) / "results_template.json", n_idx)
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(f"[pipeline] results written to {args.out} (commit {commit})")

    diagnostics = {
        "L1": {k: v for k, v in l1.items() if k != "sweep"},
        "L2": {k: v for k, v in l2.items()
               if k not in ("model_curve", "EF_grid", "EF_band_eV", "RH_norm", "Rs_norm",
                            "RH_std", "Rs_std", "measurement_index", "EF_trajectory_eV")},
        "L2_EF_band_eV_lo": list(map(float, l2["EF_band_eV"]["lo"])),
        "L2_EF_band_eV_hi": list(map(float, l2["EF_band_eV"]["hi"])),
        "L3": {k: v for k, v in l3.items() if k not in ("map_2d", "resolution_detail")},
    }
    Path("diagnostics.json").write_text(json.dumps(diagnostics, indent=2, default=float))

    fig_dir = Path(args.figures_dir)
    fig_dir.mkdir(exist_ok=True)
    figures.fig_l1(l1, fig_dir / "L1_correction_sweep.png")
    figures.fig_l2_raw(data["l2_data"], l2["zero_crossing_bracket"],
                       fig_dir / "L2_raw_repeats.png")
    figures.fig_l2_model(l2, fig_dir / "L2_model_fit.png")
    figures.fig_l2_trajectory(l2, fig_dir / "L2_trajectory.png")
    figures.fig_l3_map(l3, fig_dir / "L3_map.png")
    figures.fig_l3_method(l3, fig_dir / "L3_method.png")
    print(f"[pipeline] figures written to {fig_dir}/")
    print("[pipeline] DONE")


if __name__ == "__main__":
    main()
