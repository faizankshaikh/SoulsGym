# Margit Rework Phase 3 Result (2026-07-08)

Phase scope:

- Animation warning reduction and decode stabilization
- Throwaway script cleanup and canonical runner updates
- Safe live validation profile standardization

Implemented changes:

1. `soulsgym/games/eldenring.py`
   - Updated `margit_animation` decode behavior:
     - negative IDs -> empty string
     - very large IDs -> `Unknown`
     - normal IDs -> `Attack_<id>`
   - This prevents unstable high-value IDs from flooding warnings.

2. `soulsgym/core/data/eldenring/animations.yaml`
   - Ensured `critical` remains explicit list (`[]`).
   - Added observed player animation IDs used during live runs:
     - `29032000`
     - `50110`
     - `50113`
   - Added boss misc fallback `Unknown`.

3. `test_random_agent.py`
   - Replaced private-internals bypass script with canonical gym API runner.

4. `scripts/run_envs.py`
   - Added safe profiles:
     - `reset-only`
     - `one-step`
     - `short-cycle`
     - `full`
   - Removed hard dependency on `fire` and switched to `argparse` CLI.

Gate outcomes:

## Gate A: Animation decode sanity

```powershell
pytest tests/eldenring/test_game.py -q -rs
```

- Result: 24 passed

## Gate C: Harness cleanup validation

```powershell
pytest tests/envs/test_margit.py -q -rs
pytest -c tests/pytest.ini
```

- Results:
  - `tests/envs/test_margit.py`: 1 passed
  - default suite: 25 passed, 31 skipped, 4 deselected

## Gate B: Warning reduction live-lite

Command used:

```powershell
python scripts/run_envs.py --env SoulsGymMargit-v0 --profile one-step --cycles 5
```

Initial run:

- Completed all 5 cycles without crash.
- Unknown player animations observed: `50110`, `50113`.

Follow-up after mapping those IDs:

```powershell
python scripts/run_envs.py --env SoulsGymMargit-v0 --profile one-step --cycles 2
```

- Completed 2 cycles without unknown animation warnings.

Assessment:

- Phase 3 goals are met:
  - warning behavior is improved and more actionable
  - throwaway validation paths are replaced by canonical scripts
  - safe live validation profile is implemented and verified

Residual risks:

1. Margit coordinates are still placeholders and continue to trigger expected setup warnings.
2. Margit phase-2 transition remains uncalibrated.
3. Additional unseen animation IDs may appear in future live sessions and should be added incrementally.