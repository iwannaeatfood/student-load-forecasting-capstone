# Scrum Master record — Team BREAD (COMP9900 Project 105)

Role: Scrum Master (and developer) for a six-person team, June–August 2026. Sources: the team's Retrospective B report (submitted 26 July 2026) and the Scrum Master segment of the final demo script (6 August 2026). Both are course submissions held in my local files and are not reproduced here; this note summarises the parts about my own work.

## Sprint outcomes I reported

| Sprint | Goal | Points |
|---|---|---|
| 1 | Foundation: repository, Docker environment, first data pipeline | 50 of 50 delivered (the largest sprint) |
| 2 | Data preprocessing and first modelling work | 41 of 46 delivered |
| 3 | Finish and validate the forecasting module, prepare client handover | 44 committed (in progress at the time of the demo script) |

## What went wrong in Sprint 2 (from Retrospective B)

- Two members built separate pipeline entry points (a package `pipeline/` and a module `pipeline.py` with the same import name); both were merged without a collision check and the merged code failed to run.
- Already-implemented model logic that reduced over-forecasting was overwritten in the same merge.
- Three pull requests marked "Request Changes" were merged in the same batch of six, so review outcomes did not gate merges.
- A manual Jira review found stories with no assignee (six, under two epics), missing story points or sprint links, and one story marked Done while its integration code did not run.

## Process actions I owned

1. **Merge gate** — a pull request with unresolved blocking review feedback is not merged ("no exceptions"); I set the rule and followed up on its application.
2. **Weekly Jira health check** — every week, check that stories have acceptance criteria, story points and the right sprint.

Other retro actions were assigned to teammates (a local import/CLI check before merging pipeline changes; confirming module ownership before parallel work).

## My Sprint 2 technical work (Jira stories assigned to me)

| Story | Deliverable | Where |
|---|---|---|
| H11CBREAD-32 | Validated persistence of preprocessing outputs (`validate_modelling_columns`, `save_processed_data`) with unit tests | `src/upp_forecast/preprocessing/save_processed_data.py`, `tests/test_preprocessing.py` (last three tests) |
| H11CBREAD-41 | Client-facing output contract for `outputs/forecast/`, revised after pull-request review (PR #6, merged 22 July 2026) | `docs/output_schema.md`, `configs/default.yaml` (`paths.forecast`) |
| H11CBREAD-37 | Prototype strengths / weaknesses / limitations document (PR #7, merged 22 July 2026) | `docs/known_limitations.md` |

Scale, for honesty: these are small modules and documents (about 40 lines of code plus two short documents); my main contribution to the project was running the process above.
