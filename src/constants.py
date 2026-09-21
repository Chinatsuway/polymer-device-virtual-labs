"""Physical constants and shared numerical definitions (QXU6028 methods guide)."""
import numpy as np

K_B = 8.617333e-5      # Boltzmann constant, eV K^-1
N_A = 3.816e15         # areal atom density, atoms cm^-2
E_CHARGE = 1.602176634e-19  # elementary charge, C
E_MAX = 2.5            # numerical integration cutoff, eV


def fermi(E, EF, T):
    """Fermi-Dirac occupation; exponent clipped to [-60, 60] to avoid overflow."""
    x = np.clip((np.asarray(E, dtype=float) - EF) / (K_B * T), -60.0, 60.0)
    return 1.0 / (np.exp(x) + 1.0)
