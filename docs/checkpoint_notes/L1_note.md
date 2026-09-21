# L1 checkpoint note — G06

- Gate: n_band/n_Fermi = 1.00 at E_F=0, ~2.00 at 0.073 eV, ~2.60 at 0.10 eV,
  ~5.10 at 0.20 eV (asserted in code; closed form agrees with numerical
  integration to <0.1%).
- Correction factor at the exact operating point (E_F = 0.099778 eV, not the
  nearest CSV row): C = 2.594.
- Corrected carrier density n_Fermi = 3.64e11 cm^-2; corrected mobility
  mu = 1/(e n_F rho) = 3.05e4 cm^2 V^-1 s^-1 (no extra 10^4 factor).
- C grows with doping because the Fermi-referenced window shrinks relative to
  the full band-edge count as E_F moves up: at fixed resistivity the datasheet
  over-counts carriers by C, so the true mobility is C times the datasheet
  value and sensor sensitivity (1/n) is over-stated by the same factor.

TODO(group): turn the last point into one quantified sentence of sensor advice
for the report.
