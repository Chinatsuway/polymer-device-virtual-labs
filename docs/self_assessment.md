# Critical self-assessment (150-200 words) — group G06

- Weakness 1: what is weak, where it affects the result, and the evidence.
- Remedy 1: a specific measurement, test, model or dataset that would address it.
- Weakness 2: what is weak, where it affects the result, and the evidence.
- Remedy 2: a specific measurement, test, model or dataset that would address it.
- Residual limitation: what remains uncertain even after the remedies.

Draft (150-200 words):

TODO(group): write the final draft here. Candidate material from the analysis
so far — pick two you can defend honestly:
1. L2 gap estimate is quantised to the 0.25 kBT scan grid; the bootstrap band
   spans one grid step, so resolution of E_g is grid-limited, not noise-limited.
2. L3 spatial resolution (FWHM ~2.4 probe pitches) means features narrower
   than ~2 pitches are broadened and their amplitudes underestimated.
3. The positive corner feature sits at the map edge where the probe
   sensitivity is weakest; it survives the eta sweep but an edge artefact
   cannot be fully excluded.
4. Three repeats give a noisy per-channel sigma_j; delta_95 inherits that
   uncertainty.
