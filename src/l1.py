"""L1 — forward carrier counting: band-edge vs Fermi-referenced integrals."""
import numpy as np

from constants import E_CHARGE, E_MAX, N_A, K_B, fermi

N_INT_L1 = 20001  # integration points, per methods guide


def n_band(EF, T, c):
    """Finite-temperature band-edge count: integrate from E=0."""
    E = np.linspace(0.0, E_MAX, N_INT_L1)
    return N_A * np.trapezoid(c * E * fermi(E, EF, T), E)


def n_fermi(EF, T, c):
    """Fermi-referenced count: integrate from E=E_F (numerical)."""
    E = np.linspace(EF, E_MAX, N_INT_L1)
    return N_A * np.trapezoid(c * E * fermi(E, EF, T), E)


def n_fermi_closed(EF, T, c):
    """Closed form of the Fermi-referenced integral for the ideal linear DoS."""
    kT = K_B * T
    return N_A * c * kT * (EF * np.log(2.0) + (np.pi**2 / 12.0) * kT)


def gate_checks(c, T):
    """Published reference ratios; independent of c."""
    references = [(0.0, 1.00), (0.073, 2.00), (0.100, 2.60), (0.200, 5.10)]
    for EF, expected in references:
        ratio = n_band(EF, T, c) / n_fermi(EF, T, c)
        assert abs(ratio - expected) / expected < 0.01, (
            f"L1 gate failed at E_F={EF} eV: ratio {ratio:.4f}, expected {expected}"
        )
    # closed form must agree with the numerical integral
    for EF, _ in references:
        num = n_fermi(EF, T, c)
        clo = n_fermi_closed(EF, T, c)
        assert abs(num - clo) / clo < 1e-3, (
            f"closed form disagrees with numerical integral at E_F={EF} eV"
        )


def run_l1(l1_data, l1_params):
    """Return the marked L1 values plus the sweep table for plotting."""
    c = l1_params["c"]
    T = l1_params["T"]
    EF_op = l1_params["EF_op_eV"]
    rho = l1_params["rho_ohm_sq"]

    gate_checks(c, T)

    EF_grid = l1_data["EF_eV"].to_numpy()
    n_band_csv = l1_data["n_band_cm2"].to_numpy()
    n_F_grid = np.array([n_fermi(EF, T, c) for EF in EF_grid])
    C_grid = n_band_csv / n_F_grid

    # exact operating point — never substitute the nearest CSV row
    n_band_op = n_band(EF_op, T, c)
    n_F_op = n_fermi(EF_op, T, c)
    correction = n_band_op / n_F_op
    mobility = 1.0 / (E_CHARGE * n_F_op * rho)

    return {
        "correction_factor": float(correction),
        "n_fermi_op_cm2": float(n_F_op),
        "mobility_corrected_cm2_Vs": float(mobility),
        "EF_op_eV": float(EF_op),
        "rho_ohm_sq": float(rho),
        "sweep": {"EF_eV": EF_grid, "C": C_grid},
    }
