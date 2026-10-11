# Student Load Forecasting Prototype — Team BREAD (UNSW COMP9900 Capstone)

UNSW COMP9900 Capstone, Term 2 2026 (June–August 2026), project 105 "Alternative Student Load Forecasting Prototype", client: UNSW Planning & Performance. Team of 6; I was the **Scrum Master** and also contributed code and documentation.

**中文简介**：UNSW 毕业设计（Capstone）团队项目：为 UNSW Planning & Performance 做学生人数（student load）预测原型。团队用连续时间马尔可夫链（CTMC）对 Program × Funding Group 分群预测，并提供 Gradio 看板和 Docker 交付。我担任 Scrum Master，同时负责预处理结果的校验保存、客户输出契约和已知局限文档。

Original team repository (private; visible to team members and course staff): `unsw-cse-comp99-3900/capstone-project-9900-26t2-h11c-bread`.

## What this repository is

A curated snapshot of the team repository from about **21 July 2026 (Sprint 2)** with teammates' emails removed. The configuration, I/O, preprocessing, pipeline and UI modules and the tests are real code from that point; `src/upp_forecast/models/` (CTMC / baseline) and `reporting/` are **placeholders** in this snapshot — the final forecasting model written later is not included here. Large data, generated outputs and the formal team reports are not included either.

## Team-level results (from the team's final report, not reproduced here)

- A shared continuous-time Markov chain model across Program × Funding Group segments, with client-supplied future new-student inflows progressed through the same chain; Gradio dashboard; Docker delivery.
- 57 automated tests passing in the final system; six-fold rolling-origin backtest: **WAPE 3.64%** against **6.40%** for a seasonal-naive baseline.
- A real client-driven scope change (extra output fields requested at the week-8 client meeting) handled in the last sprints.

These are team results; I am not claiming the model or backtest as my own work.

## My contribution

See [`docs/scrum-master-record.md`](docs/scrum-master-record.md) for the detail. In short:

| Area | What | Evidence |
|---|---|---|
| Scrum Master | Sprint reporting (50/50, 41/46, 44 committed points), Retrospective B, merge-gate rule and weekly Jira health check | `docs/scrum-master-record.md` |
| H11CBREAD-32 | Validated persistence of preprocessing outputs, with tests | `src/upp_forecast/preprocessing/save_processed_data.py`, `tests/test_preprocessing.py` |
| H11CBREAD-41 | Client-facing output contract (`outputs/forecast/`) | `docs/output_schema.md` |
| H11CBREAD-37 | Strengths / weaknesses / limitations document | `docs/known_limitations.md` |

My commits in the team repository appear under the names `Yanyan Zhu` and `yyz` (both z5565492@ad.unsw.edu.au); the three files above carry an "Implemented for H11CBREAD-xx by …" header.

## How to run what is here

Python ≥ 3.13 (see `pyproject.toml`):

```bash
pip install "numpy>=2.3,<3" "pandas>=3,<4" pyyaml "scipy>=1.14,<2" "scikit-learn>=1.9,<2" "matplotlib>=3.10,<4" "gradio>=6.19.0" pytest
python -m pytest
```

or `uv sync --group dev && uv run pytest`. Checked on 11 October 2026 in a fresh Python 3.13 virtual environment: **41 passed, 2 failed** — both failures (`test_term_aliases_match_terms_active_years_raw_terms`, `test_create_demo_builds_gradio_interface`) look for the client's raw data under `data/raw/` (`Terms Active Years.csv`, `Actuals Data.csv`), which is not included. My three tests (`pytest tests/test_preprocessing.py -k "save_processed or validate_modelling"`) pass on their own. PySpark is only imported lazily by the Spark CSV strategy and is not needed for the tests. The Docker files (`Dockerfile`, `compose.yaml`) are the team's and build an image with Python, Java 21 and PySpark.

## Likely interview questions

**What was your technical contribution?** Small and specific: the validated save step for preprocessing outputs, the output-schema contract and the limitations document (table above). My main contribution was the Scrum Master role.

**Tell me about a conflict or failure and what you changed.** Sprint 2: two members implemented the pipeline entry point twice (package vs module with the same name); both merged, the code failed to run and earlier over-forecasting logic was overwritten. Three "Request Changes" pull requests had also been merged in the same batch. I introduced a hard merge gate on unresolved review feedback and a weekly Jira health check.

**Why does `docs/known_limitations.md` show WAPE 1.51?** It is the Sprint-2 draft (16 July 2026) written from early experimental results, and says so ("re-verify all numbers"). The model changed afterwards, so the final evaluation numbers are the ones in the team's final report (WAPE 3.64% in a six-fold rolling-origin backtest), not the ones in that draft.

**What is a CTMC and why use it here?** Students move between states (for example newly commencing, continuing, completed) over time; a CTMC describes the rates of those transitions, and the matrix exponential of the generator gives transition probabilities over any elapsed time. It keeps forecasts explainable — a client requirement — because every forecast decomposes into existing students plus the client's future-intake scenario.

**What is WAPE?** Weighted absolute percentage error: total absolute error divided by total actual headcount, so large programs dominate and it stays defined when small programs have near-zero headcount.
