"""All figures produced by the pipeline."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def fig_l1(l1, out_path):
    EF = l1["sweep"]["EF_eV"]
    C = l1["sweep"]["C"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(EF, C, "o-", label="C(E_F) = n_band / n_Fermi")
    for level in (2, 4):
        ax.axhline(level, ls="--", lw=0.8, color="grey")
        cross = np.interp(level, C, EF)
        ax.plot(cross, level, "s", color="tab:red")
        ax.annotate(f"C={level} at {cross:.3f} eV", (cross, level),
                    textcoords="offset points", xytext=(6, 6), fontsize=8)
    ax.axvline(l1["EF_op_eV"], ls=":", color="tab:green")
    ax.annotate(f"operating point {l1['EF_op_eV']:.4f} eV\nC={l1['correction_factor']:.3f}",
                (l1["EF_op_eV"], l1["correction_factor"]),
                textcoords="offset points", xytext=(8, -18), fontsize=8)
    ax.set_xlabel("E_F (eV)")
    ax.set_ylabel("correction factor C")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def fig_l2_model(l2, out_path):
    fig, ax = plt.subplots(figsize=(6, 5))
    curve = l2["model_curve"]
    order = np.argsort(l2["EF_grid"])
    ax.plot(curve[order, 0], curve[order, 1], "-", lw=1,
            label=f"selected model: {l2['model']} (E_g/kT={l2['Eg_kT']})")
    ax.plot(l2["RH_norm"], l2["Rs_norm"], "o", ms=4, label="measured (normalised)")
    ax.axvline(0, lw=0.5, color="grey")
    ax.set_xlabel("R_H / max|R_H|")
    ax.set_ylabel("R_xx / max R_xx")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def fig_l2_trajectory(l2, out_path):
    idx = l2["measurement_index"]
    EF = np.array(l2["EF_trajectory_eV"])
    lo = l2["EF_band_eV"]["lo"]
    hi = l2["EF_band_eV"]["hi"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(idx, lo, hi, alpha=0.3, label="bootstrap 16-84%")
    ax.plot(idx, EF, "o-", ms=3, label="assigned E_F")
    ax.axhline(0, lw=0.5, color="grey")
    ax.set_xlabel("measurement index")
    ax.set_ylabel("E_F (eV)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def fig_l3_map(l3, out_path):
    m_map = l3["map_2d"]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    v = np.max(np.abs(m_map))
    im = ax.imshow(m_map, cmap="RdBu_r", vmin=-v, vmax=v,
                   extent=[-3, 3, -3, 3], origin="lower")
    fig.colorbar(im, ax=ax, label="zero-mean Hall non-uniformity")
    for f in l3["features"]:
        ax.plot(f["x"], f["y"], "k*", ms=12)
        ax.annotate(f"{f['sign']} {f['amplitude']:+.3f}", (f["x"], f["y"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=8)
    ax.set_xlabel("x (probe pitches)")
    ax.set_ylabel("y (probe pitches)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def fig_l3_method(l3, out_path):
    sens = l3["eta_sensitivity"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot([s["roughness"] for s in sens], [s["residual"] for s in sens], "o-")
    for s in sens:
        ax1.annotate(f"x{s['scale']:g}", (s["roughness"], s["residual"]),
                     textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax1.set_xlabel("roughness ||Lm||")
    ax1.set_ylabel("residual ||Am - d||")
    ax1.set_title("eta sensitivity (eta0 = %.3e)" % l3["eta0"], fontsize=9)

    for det in l3["resolution_detail"]:
        centres = np.linspace(-2.7, 2.7, 10)
        ax2.plot(centres, det["lobe_profile_row"], "o-", ms=3,
                 label=f"impulse at {det['pixel']}, FWHM={det['fwhm_probe_pitch']:.2f} pitches")
    ax2.set_xlabel("x (probe pitches)")
    ax2.set_ylabel("reconstructed amplitude")
    ax2.set_title("point-spread test", fontsize=9)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
