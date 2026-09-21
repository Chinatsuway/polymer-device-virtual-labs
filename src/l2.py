"""L2 — zero-dimensional inverse problem: DoS class, gap, Fermi-level trajectory."""
import numpy as np

from constants import K_B, N_A, fermi

E_GRID = np.linspace(-2.5, 2.5, 4000)          # energy integral grid, eV
EF_GRID_KT = np.linspace(-8.0, 9.0, 400)       # candidate Fermi levels, kBT
GAP_GRID_KT = np.arange(0.50, 8.00 + 1e-12, 0.25)  # hard-gap candidates, kBT
IMPROVEMENT_RULE = 0.85                        # 15% residual-improvement rule


def dos(E, model, c, Eg):
    if model == "cone":
        return c * np.abs(E)
    D = Eg / 2.0
    return np.where(np.abs(E) > D, c * (np.abs(E) - D), 0.0)


def carrier_np(EF_array, T, model, c, Eg):
    """Fermi-window populations for every candidate E_F (vectorised).

    n integrates g*f from E_F upward, p integrates g*(1-f) from E_F downward.
    """
    E = E_GRID[None, :]
    EF = np.asarray(EF_array)[:, None]
    f = fermi(E, EF, T)
    g = dos(E, model, c, Eg)
    n = N_A * np.trapezoid(np.where(E >= EF, g * f, 0.0), E, axis=1)
    p = N_A * np.trapezoid(np.where(E <= EF, g * (1.0 - f), 0.0), E, axis=1)
    return n, p


def model_curves(T, c):
    """Build the model library once: normalised (R_H, R_s) curves per model.

    e and mu are set to 1; their fixed scale cancels under separate
    normalisation. Signs of R_H are preserved.
    """
    kT = K_B * T
    EF_grid = EF_GRID_KT * kT
    library = {"cone": {"Eg_kT": 0.0}}
    models = [("cone", 0.0)] + [("gap", g) for g in GAP_GRID_KT]
    lib = {}
    for model, Eg_kT in models:
        n, p = carrier_np(EF_grid, T, model, c, Eg_kT * kT)
        total = n + p
        R_H = (p - n) / total**2      # e = 1
        R_s = 1.0 / total             # mu = 1
        RH_norm = R_H / np.max(np.abs(R_H))
        Rs_norm = R_s / np.max(R_s)
        lib[(model, float(Eg_kT))] = np.column_stack([RH_norm, Rs_norm])
    return EF_grid, lib


def prepare_data(l2_data):
    """Group repeats: central estimate = mean, uncertainty = std (ddof=1)."""
    grouped = l2_data.groupby("measurement_index", sort=True)
    idx = grouped.size().index.to_numpy()
    assert (grouped.size() == 3).all(), "each measurement_index must have 3 repeats"
    RH_mean = grouped["R_H_raw"].mean().to_numpy()
    Rs_mean = grouped["R_xx_raw"].mean().to_numpy()
    RH_std = grouped["R_H_raw"].std(ddof=1).to_numpy()
    Rs_std = grouped["R_xx_raw"].std(ddof=1).to_numpy()
    return idx, RH_mean, Rs_mean, RH_std, Rs_std


def normalise(RH, Rs):
    """Normalise each channel independently; keep the sign of R_H."""
    return RH / np.max(np.abs(RH)), Rs / np.max(Rs)


def locate_zero_crossing(idx, RH_mean):
    """Pair of measurement indices bracketing the R_H sign change."""
    sign = np.sign(RH_mean)
    crossings = np.nonzero(np.diff(sign) != 0)[0]
    assert len(crossings) >= 1, "R_H never changes sign: cannot locate neutrality"
    i = crossings[0]
    return int(idx[i]), int(idx[i + 1])


def fit_model(data_xy, EF_grid, model_xy):
    """Nearest-point assignment on the normalised model curve."""
    d2 = ((data_xy[:, None, :] - model_xy[None, :, :]) ** 2).sum(axis=2)
    j_nearest = np.argmin(d2, axis=1)
    rms = float(np.sqrt(np.mean(np.min(d2, axis=1))))
    return rms, EF_grid[j_nearest], j_nearest


def select_model(data_xy, EF_grid, lib):
    """Fit cone and every hard-gap candidate; apply the 15% improvement rule."""
    r_cone, EF_cone, _ = fit_model(data_xy, EF_grid, lib[("cone", 0.0)])
    best = None
    for (model, Eg_kT), model_xy in lib.items():
        if model != "gap":
            continue
        rms, EF_assigned, _ = fit_model(data_xy, EF_grid, model_xy)
        if best is None or rms < best["rms"]:
            best = {"Eg_kT": Eg_kT, "rms": rms, "EF": EF_assigned}
    if best["rms"] < IMPROVEMENT_RULE * r_cone and best["Eg_kT"] >= 1.0:
        return {
            "model": "hard_gap", "Eg_kT": float(best["Eg_kT"]),
            "rms": best["rms"], "r_cone": r_cone, "EF": best["EF"],
        }
    return {
        "model": "cone", "Eg_kT": 0.0,
        "rms": r_cone, "r_cone": r_cone, "EF": EF_cone,
        "best_gap_Eg_kT": float(best["Eg_kT"]), "best_gap_rms": float(best["rms"]),
    }


def bootstrap(l2_data, idx, EF_grid, lib, n_replicates=200, seed=12345):
    """Resample one repeat per index; refit with the same selection rule."""
    rng = np.random.default_rng(seed)
    pivot = l2_data.pivot(index="measurement_index", columns="repeat")
    RH_reps = pivot["R_H_raw"].loc[idx].to_numpy()   # (n_idx, 3)
    Rs_reps = pivot["R_xx_raw"].loc[idx].to_numpy()

    Eg_samples = []
    EF_samples = []
    gap_selected = 0
    for _ in range(n_replicates):
        pick = rng.integers(0, 3, size=len(idx))
        rows = np.arange(len(idx))
        RH = RH_reps[rows, pick]
        Rs = Rs_reps[rows, pick]
        RH_n, Rs_n = normalise(RH, Rs)
        data_xy = np.column_stack([RH_n, Rs_n])
        sel = select_model(data_xy, EF_grid, lib)
        Eg_samples.append(sel["Eg_kT"])
        EF_samples.append(sel["EF"])
        gap_selected += int(sel["model"] == "hard_gap")
    return {
        "Eg_kT_samples": np.array(Eg_samples),
        "EF_samples": np.array(EF_samples),          # (n_replicates, n_idx)
        "hard_gap_fraction": gap_selected / n_replicates,
    }


def run_l2(l2_data, l2_meta, c, seed=12345, n_replicates=200):
    T = l2_meta["T_K"]
    idx, RH_mean, Rs_mean, RH_std, Rs_std = prepare_data(l2_data)
    cross_a, cross_b = locate_zero_crossing(idx, RH_mean)

    RH_norm, Rs_norm = normalise(RH_mean, Rs_mean)
    # gate: the zero-crossing must survive independent normalisation
    i = list(idx).index(cross_a)
    assert RH_norm[i] * RH_norm[i + 1] < 0, "normalisation destroyed the R_H zero-crossing"

    EF_grid, lib = model_curves(T, c)
    data_xy = np.column_stack([RH_norm, Rs_norm])
    central = select_model(data_xy, EF_grid, lib)
    assert len(central["EF"]) == len(idx), "trajectory length must equal unique indices"

    boot = bootstrap(l2_data, idx, EF_grid, lib, n_replicates=n_replicates, seed=seed)
    Eg_lo, Eg_med, Eg_hi = np.percentile(boot["Eg_kT_samples"], [16, 50, 84])
    EF_lo, EF_hi = np.percentile(boot["EF_samples"], [16, 84], axis=0)

    # diagnostic: for an ideal cone the wings obey |R_H~| ∝ R_xx~^2
    wing = np.abs(RH_norm) > 0
    slope = np.polyfit(np.log(Rs_norm[wing]), np.log(np.abs(RH_norm[wing])), 1)[0]

    model_key = ("cone", 0.0) if central["model"] == "cone" else ("gap", central["Eg_kT"])
    return {
        "model": central["model"],
        "Eg_kT": central["Eg_kT"],
        "Eg_bootstrap_median_kT": float(Eg_med),
        "Eg_uncertainty_kT": float((Eg_hi - Eg_lo) / 2.0),
        "Eg_percentiles_kT": [float(Eg_lo), float(Eg_med), float(Eg_hi)],
        "hard_gap_fraction": float(boot["hard_gap_fraction"]),
        "r_cone": float(central["r_cone"]),
        "r_selected": float(central["rms"]),
        "best_gap": {"Eg_kT": central.get("best_gap_Eg_kT"), "rms": central.get("best_gap_rms")},
        "EF_trajectory_eV": [float(x) for x in central["EF"]],
        "EF_band_eV": {"lo": EF_lo, "hi": EF_hi},
        "measurement_index": idx,
        "zero_crossing_bracket": [cross_a, cross_b],
        "RH_norm": RH_norm, "Rs_norm": Rs_norm,
        "RH_std": RH_std, "Rs_std": Rs_std,
        "wing_loglog_slope": float(slope),
        "model_curve": lib[model_key],
        "model_curve_cone": lib[("cone", 0.0)],
        "EF_grid": EF_grid,
        "n_replicates": n_replicates,
        "seed": seed,
    }
