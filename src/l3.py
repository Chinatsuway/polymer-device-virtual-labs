"""L3 — two-dimensional inverse problem: zero-mean uniformity map."""
import numpy as np

ETA_SCALES = [0.01, 0.1, 1.0, 10.0, 100.0]
PIXEL_CENTRES = np.linspace(-2.7, 2.7, 10)  # probe-pitch units


def gradient_matrix(npix=10):
    """First-difference matrix: one row per horizontal/vertical neighbour pair."""
    rows = []
    N = npix * npix
    for i in range(npix):
        for j in range(npix):
            k = i * npix + j
            if j < npix - 1:
                r = np.zeros(N)
                r[k] = -1
                r[k + 1] = 1
                rows.append(r)
            if i < npix - 1:
                r = np.zeros(N)
                r[k] = -1
                r[k + npix] = 1
                rows.append(r)
    return np.asarray(rows)


def make_solver(A, L, eta):
    """Precompute the regularised operator with the constant mode projected out."""
    N = A.shape[1]
    one = np.ones((N, 1)) / np.sqrt(N)
    P = np.eye(N) - one @ one.T
    M = P @ (A.T @ A + eta * (L.T @ L)) @ P + 1e-9 * np.eye(N)
    PA_T = P @ A.T

    def reconstruct(dvec):
        b = PA_T @ dvec
        m = np.linalg.lstsq(M, b, rcond=None)[0]
        return m - m.mean()

    return reconstruct


def eta_sensitivity(A, L, dbar, eta0):
    """Residual norm vs roughness norm over the eta grid."""
    out = []
    for scale in ETA_SCALES:
        eta = eta0 * scale
        rec = make_solver(A, L, eta)
        m = rec(dbar)
        out.append({
            "scale": scale, "eta": float(eta),
            "residual": float(np.linalg.norm(A @ m - dbar)),
            "roughness": float(np.linalg.norm(L @ m)),
        })
    return out


def find_features(m_map):
    """Extrema as features; adjacent extremal pixels merged into one feature."""
    features = []
    for sign, label in [(1, "positive"), (-1, "negative")]:
        masked = sign * m_map
        threshold = np.max(masked) * 0.5
        blob = masked >= threshold
        # merge connected pixels (4-neighbourhood) around the global extremum
        i0, j0 = np.unravel_index(np.argmax(masked), masked.shape)
        visited = np.zeros_like(blob, dtype=bool)
        stack = [(i0, j0)]
        pixels = []
        while stack:
            i, j = stack.pop()
            if not (0 <= i < 10 and 0 <= j < 10) or visited[i, j] or not blob[i, j]:
                continue
            visited[i, j] = True
            pixels.append((i, j))
            stack += [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
        amp = float(sign * m_map[i0, j0])
        features.append({
            "sign": label,
            "x": float(PIXEL_CENTRES[j0]),
            "y": float(PIXEL_CENTRES[i0]),
            "amplitude": amp,
            "pixels": [[int(i), int(j)] for i, j in pixels],
        })
    return features


def resolution_test(A, L, eta, pixels=((5, 5), (2, 7))):
    """Inject a unit impulse, reconstruct, measure the positive-lobe FWHM."""
    rec = make_solver(A, L, eta)
    widths = []
    for pi, pj in pixels:
        q = np.zeros(100)
        q[pi * 10 + pj] = 1.0
        q -= q.mean()
        y = A @ q
        q_hat = rec(y).reshape(10, 10)

        half = np.max(q_hat) / 2.0
        # discrete half-maximum extent along row and column through the pixel
        row = q_hat[pi, :] >= half
        col = q_hat[:, pj] >= half
        width_row = float(np.sum(row))
        width_col = float(np.sum(col))
        discrete = max(width_row, width_col)

        # weighted-sigma estimate (used when the discrete contour is coarse)
        w = np.maximum(q_hat, 0.0)
        ii, jj = np.meshgrid(PIXEL_CENTRES, PIXEL_CENTRES, indexing="ij")
        r2 = (ii - PIXEL_CENTRES[pi]) ** 2 + (jj - PIXEL_CENTRES[pj]) ** 2
        sigma2 = float(np.sum(w * r2) / (2.0 * np.sum(w)))
        weighted = 2.355 * np.sqrt(sigma2) / (PIXEL_CENTRES[1] - PIXEL_CENTRES[0])

        pitch = PIXEL_CENTRES[1] - PIXEL_CENTRES[0]
        fwhm_pitch = discrete if np.sum(q_hat >= half) >= 3 else weighted
        widths.append({
            "pixel": [pi, pj],
            "fwhm_probe_pitch": float(fwhm_pitch),
            "method": "discrete" if np.sum(q_hat >= half) >= 3 else "weighted",
            "lobe_profile_row": q_hat[pi, :].copy(),
            "pitch": float(pitch),
        })
    conservative = max(w["fwhm_probe_pitch"] for w in widths)
    return conservative, widths


def detection_limit(A, L, eta, d_reps, n_noise=500, seed=12345):
    """95th percentile of max|m_noise| from channel-wise repeat noise."""
    sigma_j = d_reps.std(axis=0, ddof=1)
    rng = np.random.default_rng(seed)
    rec = make_solver(A, L, eta)
    maxima = []
    for _ in range(n_noise):
        noise = rng.normal(0.0, sigma_j)
        m_noise = rec(noise)
        maxima.append(float(np.max(np.abs(m_noise))))
    delta_95 = float(np.percentile(maxima, 95))
    return delta_95, {"sigma_j": sigma_j, "maxima": np.array(maxima)}


def pass_fail(a, delta_95, spec):
    if a + delta_95 < spec:
        return True, f"clear pass: a+d95={a + delta_95:.4f} < spec={spec}"
    if a - delta_95 > spec:
        return False, f"clear fail: a-d95={a - delta_95:.4f} > spec={spec}"
    return False, f"borderline: |a-spec|={abs(a - spec):.4f} within d95={delta_95:.4f}"


def run_l3(A, d_reps, spec=None, seed=12345, n_noise=500):
    L = gradient_matrix(10)
    eta0 = 1e-2 * np.linalg.norm(A, 2) ** 2 / np.linalg.norm(L, 2) ** 2
    dbar = d_reps.mean(axis=0)

    sensitivity = eta_sensitivity(A, L, dbar, eta0)
    rec = make_solver(A, L, eta0)
    m = rec(dbar)
    assert abs(m.mean()) < 1e-10, "reconstruction must obey the zero-mean constraint"
    m_map = m.reshape(10, 10)

    features = find_features(m_map)
    resolution, resolution_detail = resolution_test(A, L, eta0)
    delta_95, noise_detail = detection_limit(A, L, eta0, d_reps, n_noise=n_noise, seed=seed)

    a = float(np.max(np.abs(m)))
    if spec is not None:
        passed, confidence = pass_fail(a, delta_95, spec)
    else:
        passed, confidence = None, "spec not yet announced (Session 3)"

    return {
        "map": [float(x) for x in m],
        "map_2d": m_map,
        "features": features,
        "resolution_probe_pitch": float(resolution),
        "resolution_detail": resolution_detail,
        "detection_limit": delta_95,
        "detection_limit_fraction": (delta_95 / spec) if spec else None,
        "max_abs": a,
        "eta0": float(eta0),
        "eta_sensitivity": sensitivity,
        "spec": spec,
        "pass": passed,
        "confidence": confidence,
        "seed": seed,
        "n_noise": n_noise,
    }
