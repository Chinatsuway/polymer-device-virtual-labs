# AI error ledger — QXU6028 virtual lab, group G06

What earns marks: specific physics or analysis errors — the AI claim/code, the
failed physical check that exposed it, and the corrected approach. Generic
statements such as "AI made a bug" are weak evidence.

| Date / phase | Tool + task | AI claim or output | Test / evidence that exposed the error | Correction and physical reason |
|---|---|---|---|---|
| 2026-09-21 / tooling | Kimi Code: checkpoint zip script | Used `zipfile.ZipDeflated` | `AttributeError` on first run; Python exposes `ZIP_DEFLATED` (hallucinated constant, wrong case) | Corrected to `zipfile.ZIP_DEFLATED`. Tag: silent fallback/hallucinated API. No physics impact, but it would have blocked the checkpoint upload if untested — every script must be executed, not just read |
| 2026-09-21 / L3 | Kimi Code: feature extraction | Reported feature amplitude as an unsigned magnitude with the sign in a separate label | The printed note read "negative amplitude +0.0306", an internally inconsistent record; results.json consumers (and the marker) need the signed map value to check feature sign | Store the signed map value at the extremum; sign then follows from the number itself. Tag: sign. Physical reason: the pass/fail and feature checks compare against a signed hidden-truth map, so dropping the sign silently flips a defect from depletion to accumulation |
| (add next entry) | | | | |

Candidate tags: integration-limit, unit, sign, normalisation order,
index/alignment, zero-mean constraint, regularisation,
silent fallback/hallucinated API.

Group guidance: full credit normally requires at least two genuine *physics*
errors with detection and correction evidence. The two seed entries above are
real but only one is physics-flavoured; keep watching the physics gates
(integration limits, signs, normalisation order, zero-mean constraint) during
the remaining work and record what actually fails.
