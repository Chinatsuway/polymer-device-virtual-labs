"""Data loading with integrity and shape checks.

Raw group files are never modified; loading re-verifies sha256 against the
supplied manifest when one is present.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _verify_manifest(data_dir: Path):
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["files"]:
        fpath = data_dir / entry["name"]
        digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
        assert digest == entry["sha256"], (
            f"sha256 mismatch for {entry['name']}: data files must remain unchanged"
        )


def load_group_data(data_dir):
    """Load every supplied file for one group dataset."""
    data_dir = Path(data_dir)
    _verify_manifest(data_dir)

    l1_data = pd.read_csv(data_dir / "L1_data.csv")
    l1_params = json.loads((data_dir / "L1_params.json").read_text())
    l2_data = pd.read_csv(data_dir / "L2_data.csv")
    l2_meta = json.loads((data_dir / "L2_meta.json").read_text())
    A = np.load(data_dir / "L3_A.npy")
    d_reps = np.loadtxt(data_dir / "L3_d.csv", delimiter=",")
    l3_meta = json.loads((data_dir / "L3_meta.json").read_text())

    assert A.shape == tuple(l3_meta["matrix_shape"]), f"A shape {A.shape}"
    assert d_reps.shape == tuple(l3_meta["readings_shape"]), f"d shape {d_reps.shape}"
    assert np.max(np.abs(A.sum(axis=1))) < 1e-11, "rows of A must sum to ~0"

    return {
        "data_dir": data_dir,
        "group": l1_params["group"],
        "dataset_set": l1_params["dataset_set"],
        "l1_data": l1_data,
        "l1_params": l1_params,
        "l2_data": l2_data,
        "l2_meta": l2_meta,
        "A": A,
        "d_reps": d_reps,
        "l3_meta": l3_meta,
    }
