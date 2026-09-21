# L2 checkpoint note — G06

- Gate: charge neutrality located from the R_H zero-crossing between
  measurement indices 22 and 23 *before* normalisation; R_H and R_xx
  normalised independently to their own maxima; signs preserved.
- Nearest-curve fit in separately normalised (R_H, R_xx) space.
  Residuals: cone r = 0.1050, best hard gap r = 0.0159.
- 15% improvement rule: 0.0159 < 0.85 x 0.1050 and E_g = 3.75 kBT >= 1 kBT,
  so the hard-gap model is selected. Bootstrap (200 replicates, seed 12345)
  selects the hard gap in 100% of replicates; E_g/kT 16-84% interval
  half-width = 0.12 (one grid step of 0.25).
- Fermi-level trajectory: monotonic drift from about -0.061 eV to +0.118 eV
  across the series, crossing neutrality near index 22-23.
- Device implication: a 3.75 kBT (~97 meV at 300 K) gap is several times
  thermal energy, so off-state leakage is suppressed — the material favours
  switching use over sensor/interconnect use.

TODO(group): check the trajectory figure, discuss resolution limits
(sub-thermal gaps indistinguishable), and refine the device recommendation
with numbers.
