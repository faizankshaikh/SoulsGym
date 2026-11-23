# Margit Rework Phase 6 Plan (2026-07-08)

Status: Active execution. Option 1 selected: defer reset-fidelity calibration and proceed with phase-2 setup design under manual in-arena live workflow.

## Why Phase 6

Phase 5 stabilized validation and observer telemetry. Current priority is phase-2 setup calibration design while reset-fidelity calibration is deferred.

## Objectives

1. Calibrate and replace placeholder Margit coordinates in `coordinates.yaml`.
2. Add a reliable coordinate-capture workflow for repeatable calibration sessions.
3. Define and implement a calibrated phase-2 setup path (or explicit guarded fallback with measurable criteria).
4. Re-run regression and live checks with updated coordinates.

## Scope boundaries

In scope:

- `scripts/run_envs.py` helper profile for coordinate capture artifacts.
- `soulsgym/core/data/eldenring/coordinates.yaml` value replacement from live captures.
- `soulsgym/envs/eldenring/margit.py` phase-2 setup calibration updates.
- Result documentation for calibration evidence and residual risk.

Out of scope:

- New training-policy changes.
- Broad refactors unrelated to reset/phase calibration.

## File-by-file work

### scripts/run_envs.py

Planned:

- Add calibration profile to capture player/boss poses with labeled coordinate key intent.
- Emit JSON/YAML-friendly artifacts under `logs/calibration/`.

Done criteria:

- Repeated runs produce consistent capture artifacts usable for `coordinates.yaml` updates.

### soulsgym/core/data/eldenring/coordinates.yaml

Planned:

- Replace placeholders for:
  - `bonfire`
  - `fog_wall`
  - `post_fog_wall`
  - `center`
  - `player_init_pose`
  - `player_init_poses_random`
  - `boss_init_pose`

Done criteria:

- `_coords_ready()` returns true in live runs.
- Arena setup no longer skips due to placeholder coordinates.

### soulsgym/envs/eldenring/margit.py

Planned:

- Calibrate `_phase_setup` behavior using measurable trigger and completion checks.
- Keep deterministic fallback with explicit warning if calibration criteria are not met.

Done criteria:

- Phase-2 setup path is reproducible and does not destabilize reset.

## Gate structure

## Gate A: Capture readiness

Pass criteria:

- Calibration profile generates artifacts for all required coordinate keys.

## Gate B: Coordinate replacement validation

Pass criteria:

- `coordinates.yaml` updated from captured values.
- Live reset path enters arena setup without placeholder-skip warnings.

## Gate C: Phase-2 setup validation

Pass criteria:

- Phase-2 setup behavior is exercised and logs expected transitions.

## Phase-2 setup design spec (draft for approval)

Goal:

- Make phase=2 startup deterministic enough for validation while preserving the current manual in-arena workflow.

Scope for this change:

- Update only `soulsgym/envs/eldenring/margit.py` phase-2 setup behavior.
- Do not modify reset-only flow semantics in this step.

Proposed behavior:

1. Trigger:
  - Run phase-2 setup only when environment is created with `phase == 2` and `_phase_init` is false.
2. Preconditions:
  - Arena setup has completed.
  - Player is alive (`player_hp > 0`).
  - Boss is alive (`margit_hp > 0`).
3. Action:
  - Keep game unpaused during setup attempt.
  - Poll observed boss animation and boss HP in a bounded window.
  - Mark phase setup complete when one of these criteria is met:
    - boss HP is below configurable threshold for phase-2 proxy start, or
    - an allowed phase-transition animation ID/name is observed (when mapping is available).
4. Fallback:
  - If criteria are not met before timeout, emit structured warning and set `_phase_init = True` to avoid reset loops.
  - Include reason code in log message, for example `timeout_no_phase2_signal`.

Validation signals to log:

- setup_start with configured timeout and threshold values.
- setup_success with criterion type (`hp_threshold` or `animation_signal`) and observed values.
- setup_fallback with reason code and last observed values.

Acceptance criteria for implementation:

- No regression in existing tests.
- Phase-2 setup path is exercised without crashes in a short live run under manual workflow.
- Logs clearly show whether success or fallback occurred and why.

Review gate:

- Do not implement this spec until user explicitly approves this section.

## Gate D: Regression safety

```powershell
pytest tests/eldenring/test_game.py -q -rs
pytest tests/envs/test_margit.py -q -rs
pytest -c tests/pytest.ini
```

Pass criteria:

- All checks pass with expected skips only.

## Operational requirement

Before each live Gate A/B/C command, provide mandatory pre-test game-state briefing and wait for user confirmation per workflow policy.

Current default live protocol:

- User manually enters the Margit arena, unpauses boss AI, and gives explicit green light.
- Prefer observer captures with `--stop-on-player-death` for clean artifacts.
- Do not run `--profile reset-only` unless reset calibration is explicitly re-opened.

## Implementation update (2026-07-08)

- Approved phase-2 setup spec is implemented in `soulsgym/envs/eldenring/margit.py`.
- `_phase_setup` now has:
  - bounded setup window with timeout,
  - start/success/fallback structured logs,
  - success criteria via HP threshold proxy or mapped transition animation signal,
  - non-looping fallback that marks phase setup complete with explicit reason.
- Regression safety after implementation:
  - `tests/eldenring/test_game.py`: 24 passed
  - `tests/envs/test_margit.py`: 1 passed
  - Full suite: 25 passed, 31 skipped, 4 deselected

## Checkpoint update (2026-07-09)

- Multi-run observer artifacts were aggregated to expand Margit raw animation mapping.
- `soulsgym/games/eldenring.py` and `soulsgym/core/data/eldenring/animations.yaml` were updated with recurring raw IDs, including newly observed `504659904`.
- Focused regressions after mapping updates are green:
  - `tests/eldenring/test_game.py`: 24 passed
  - `tests/envs/test_margit.py`: 1 passed
- Additional live confirmation run was intentionally deferred by user decision.

Next non-live focus:

- Keep improving boss-animation observability from existing artifacts and code mapping updates, without requiring an immediate in-arena session.
