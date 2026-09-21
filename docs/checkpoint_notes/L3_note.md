# L3 checkpoint note — G06

- Gate: A is 128x100, d is 3x128, max|row sums of A| < 1e-11 (probe blind to
  uniform offset); reconstruction enforces mean(m) = 0 via projection P plus
  an explicit final de-meaning.
- Tikhonov with first-difference L (180x100); eta0 = 1e-2 ||A||_2^2/||L||_2^2
  = 1.33e-3. Eta sensitivity over x0.01..x100 shows the reconstruction is
  stable: both extrema keep their positions and amplitudes within ~10% over
  two decades of eta, so eta0 is retained.
- Features: negative dip -0.031 at (+0.9, -2.1) probe pitches (merged blob
  ~11 pixels); positive maximum +0.015 at (-2.7, +2.7). Both are stable
  under the eta sweep, so neither is a regularisation artifact.
- Resolution: point-spread test (unit impulse, zero-meaned, same eta and
  solver) gives FWHM 2.41 pitches at the centre pixel and 2.17 at an
  off-centre pixel (weighted-sigma method); conservative resolution 2.41
  probe pitches.
- Noise and detection limit: channel-wise std from the 3 repeats; 500
  noise-only reconstructions (seed 12345) give delta_95 = 9.5e-6, far below
  the feature amplitudes.
- Pass/fail: PENDING the specification announced in Session 3; rerun
  `python reproduce.py --spec <THRESHOLD>` and this note updates from
  results.json.

TODO(group): fill in the announced spec, record the confidence statement,
and comment on degradation with noise for the report.
