# Personal analytics and workflow branch

`personal/analytics` keeps experimental tooling, analysis and workflow notes for the Margit environment. These aren't part of the upstream pull requests. The branch is based on the Margit pull request code and is never an ancestor of an upstream PR branch.

| Path | Contents |
| --- | --- |
| `analytics/margit_observer_harness.py` | Read-only observation and calibration harness for live Margit fights |
| `dev-tools/` | Development scripts: a mutation-parity harness (`mut_harness.py`), two M1 memory probes and a random-agent smoke runner (`random_agent.py`, called `test_random_agent.py` in the notes) |
| `notes/` | Margit rework plans, phase results, workflow and the PR readiness plan. They were moved here from `docs/`, so paths inside them are historical. |
| `.agents/AGENTS.md` | Workflow rules for coding agents |

## Observer harness

Run it from the repository root with the game running and a character at Margit. It only reads game state.

```powershell
python -m analytics.margit_observer_harness observe [--steps N] [--interval SECONDS] [--stop-on-player-death]
python -m analytics.margit_observer_harness summary [--observer-json PATH]
python -m analytics.margit_observer_harness capture-calibration [--capture-key KEY]
```

`observe` writes a CSV and a JSON file per run to `logs/observer/`. The JSON holds every recorded field; the CSV is a subset. `capture-calibration` writes to `logs/calibration/`.

## Logs

`logs/` is ignored by git. Earlier observer, calibration and live-run logs (July to November 2026) are kept in a local archive and aren't committed: they predate the November environment fixes, so new recordings are more reliable.
