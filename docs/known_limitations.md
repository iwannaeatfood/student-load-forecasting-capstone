# Prototype Strengths, Weaknesses, and Limitations

Implemented for H11CBREAD-37 by Yanyan Zhu (z5565492@ad.unsw.edu.au)

Draft from `.temp/combine/` experimental results; re-verify all numbers
once H11CBREAD-38 and H11CBREAD-66 land.

## Strengths

- CTMC progression and NAC inflow are separate models — each stays
  interpretable.
- Sparse cohorts get a deterministic 4-level fallback (Program + Funding
  Group → Program → Funding Group → global) instead of failing.
- NAC blend (`final = w*ridge + (1-w)*baseline`) damps the Ridge model's
  over-forecasting by design.

## Weaknesses

- 2026 holdout over-forecasts: Predicted HC 312,165 vs Actual 196,395
  (WAPE 1.51, Bias +0.59).
- Error concentrates in the smaller funding groups:

  | Funding Group | WAPE | Bias | Predicted HC | Actual HC |
  |---|---|---|---|---|
  | DEST | 1.32 | +0.35 | 130,886 | 97,115 |
  | INTL | 1.58 | +0.74 | 140,263 | 80,483 |
  | FEEP | 2.09 | +0.98 | 27,777 | 14,027 |
  | OTHR | 2.53 | +1.78 | 13,240 | 4,770 |

- 666 of 1,914 cohort matrices (35%) fall back off the finest level,
  mostly "not enough intervals" (<40 observed).

## Failure points

- NAC inflow calibration is the main accuracy lever (H11CBREAD-66).
- Sparse-cohort fallback is a workaround, not a fix; more history or
  partial pooling is out of prototype scope (H11CBREAD-60).
