"""Validation of results.json against the supplied template schema."""
import json
import math
from pathlib import Path


def validate_results(results, template_path, n_indices):
    template = json.loads(Path(template_path).read_text())
    assert set(results.keys()) == set(template.keys()), "top-level keys must match template"
    for phase in ("L1", "L2", "L3"):
        assert set(results[phase].keys()) == set(template[phase].keys()), (
            f"{phase} keys must match template"
        )

    def finite(x):
        return isinstance(x, (int, float)) and math.isfinite(x)

    for key in ("correction_factor", "n_fermi_op_cm2", "mobility_corrected_cm2_Vs"):
        assert finite(results["L1"][key]), f"L1.{key} must be a finite number"

    assert results["L2"]["model"] in ("cone", "hard_gap")
    assert finite(results["L2"]["Eg_kT"])
    assert finite(results["L2"]["Eg_uncertainty_kT"])
    traj = results["L2"]["EF_trajectory_eV"]
    assert len(traj) == n_indices and all(finite(x) for x in traj), (
        "trajectory length must equal the number of unique measurement indices"
    )

    m = results["L3"]["map"]
    assert len(m) == 100 and all(finite(x) for x in m), "map must be 100 finite values"
    assert finite(results["L3"]["resolution_probe_pitch"])
    if results["L3"]["pass"] is not None:
        assert isinstance(results["L3"]["pass"], bool)
        assert finite(results["L3"]["detection_limit_fraction"])
