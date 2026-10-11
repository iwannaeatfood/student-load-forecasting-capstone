# Forecast Output Schema

Implemented for H11CBREAD-41

Output contract for `outputs/forecast/` (`paths.forecast` in
`configs/default.yaml`). H11CBREAD-34/-38/-66 write these files; do not
invent new paths.

- `combined_forecast.csv` — internal, all modelling dimensions: `Year`,
  `Funding Group`, `Program`, `Term`, `State`,
  `Combined Predicted Active HC`, `Predicted Existing Active HC`,
  `Predicted NAC Inflow HC`.
- `program_forecast.csv` — client-facing, locked by H11CBREAD-65:
  `ACAD_PROG`, `forecast_year`, `forecast_term`, `predicted_hc`.
  No extra columns.
- `forecast_metrics.csv` — from H11CBREAD-38: `MAE`, `RMSE`, `WAPE`,
  `Bias`, `Predicted HC`, `Actual HC`, plus one segment column.

**Status: planned, not yet produced.** The H11CBREAD-11 pipeline does not
write to `outputs/forecast/` yet — it only writes `outputs/<run_id>/
forecast_output.csv` (per-run, no real model wired in). H11CBREAD-34/-38/-66
must write the three files above into `outputs/forecast/` as their single
export point once the real model lands; until then, nothing reads from or
writes to this directory.

Sprint-1 placeholder path keys (`paths.forecasts/metrics/figures`) have been
removed from `configs/default.yaml` — nothing referenced them.
