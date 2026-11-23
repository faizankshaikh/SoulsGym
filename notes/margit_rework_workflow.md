# Margit Rework Workflow (Checkpoints + Test Gates)

## Purpose

Define a strict implementation workflow before starting code changes so we preserve known good states, keep commits reviewable, and continuously verify that the project still runs.

This workflow is mandatory for the Margit rework.

## Branching and checkpoint policy

## 1) Branch model

- Keep one long-lived implementation branch for this effort.
- Use mandatory checkpoint tags after each approved phase.
- Phase branches are optional aliases for readability and review navigation.

Recommended naming:

- `margit-rework/phase-1-data-interface`
- `margit-rework/phase-2-env-lifecycle`
- `margit-rework/phase-3-tests-harness`
- `margit-rework/phase-4-cleanup-docs`

Practical policy used in this rework:

- Implementation may continue on a single branch when phase gates, user approvals, and checkpoint
	tags are strictly enforced.
- Optional phase-named branches can be created as aliases at phase commits for easier history
	browsing without rewriting history.

## 2) Commit policy

- One logical change set per commit.
- Commit after each passing gate.
- No mixed commits across unrelated files or phases.

Commit message format:

- `phase-X(scope): short summary`

Examples:

- `phase-1(eldenring-data): complete margit coordinates and addresses`
- `phase-2(env): refactor margit reset lifecycle to iudex pattern`

## 3) Safety tags/checkpoints

Before each phase starts:

- Create an annotated checkpoint tag.

Suggested tags:

- `checkpoint/pre-margit-rework`
- `checkpoint/after-phase-1`
- `checkpoint/after-phase-2`
- `checkpoint/after-phase-3`

## Required gate structure

Each phase follows this exact cycle:

1. Plan review gate (explicitly approved)
2. Implement only that phase scope
3. Pre-test game-state briefing (explicitly confirmed)
4. Run phase test gate
5. Review results
6. User review and explicit approval to proceed
7. Commit + checkpoint tag
8. Move to next phase

No phase is marked done without passing its gate.

## Mandatory pre-test game-state briefing

Before any test command is executed, provide a short state briefing and wait for user confirmation.

Required briefing format:

1. Command about to run
2. Expected game state before running
3. Expected AI state (paused or unpaused)
4. Expected player location/state (for example: inside boss arena, at grace, menu closed)
5. Expected capture/window state (for example: 800x450 capture, game focused)
6. Confirmation prompt to proceed

Execution rule:

- Do not run the command until the user confirms the listed state is ready.

Current live-run override (2026-07-08):

- Reset-fidelity work (bonfire to fog-wall traversal behavior) is deferred.
- For live Margit runtime commands, execute only after the user manually enters the boss arena,
	unpauses the boss, and gives an explicit green light.
- Do not run `--profile reset-only` unless the user explicitly asks to re-open reset calibration.

Briefing examples:

- `pytest -c tests/pytest.ini`
	- Expected game state: game may be off; this suite should still run.
	- AI state: not required.
- `pytest tests/envs/test_margit.py -q -rs`
	- Expected game state: Elden Ring running and loaded ingame.
	- AI state: paused is acceptable unless gate explicitly says unpaused.
- `python scripts/run_envs.py --env SoulsGymMargit-v0 --profile action-sequence --cycles 3`
	- Expected game state: inside Margit boss fight arena, menu closed.
	- AI state: paused for deterministic sequence validation.
- `python scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-short --cycles 3 --steps 20`
	- Expected game state: inside Margit boss fight arena, menu closed.
	- AI state: unpaused.

## Test strategy and commands

## Baseline checks (run once before phase work)

Goal: prove we can return to known baseline behavior.

Commands:

```powershell
pytest -c tests/pytest.ini
```

If Elden Ring is running and configured, also run:

```powershell
pytest tests/eldenring/test_game.py -q
```

Record outcomes in a short phase log (pass/fail + notes).

## Phase gates

## Phase 1 gate: data + Elden Ring interface

Target:

- Static tables and game interface changes compile and load.

Minimum checks:

```powershell
pytest tests/eldenring/test_game.py -q
pytest tests/envs/test_margit.py -q
```

Optional live smoke:

```powershell
python scripts/run_envs.py --env SoulsGymMargit-v0
```

Pass criteria:

- No import/runtime errors from Elden Ring interface changes.
- Margit env can instantiate and reset in game-on context.

## Phase 2 gate: Margit env lifecycle parity

Target:

- Reset/step flow aligned with Iudex style.

Minimum checks:

```powershell
pytest tests/envs/test_margit.py -q
```

Integration gate (game-on):

```powershell
pytest -m integration tests/eldenring/integration_tests/test_envs.py -q
```

Pass criteria:

- Episode loop progresses without private-state bypasses.
- Action mask and termination behavior remain coherent.

## Phase 3 gate: test harness + cleanup scripts

Target:

- Remove throwaway script paths, standardize runners and tests.

Checks:

```powershell
pytest -c tests/pytest.ini
pytest tests/envs/test_margit.py -q
```

Pass criteria:

- No root-level throwaway validation script remains.
- Canonical script path validates Margit using gym API lifecycle.

## Phase 4 gate: docs + final readiness

Target:

- Public docs and status messaging are aligned with tested reality.

Checks:

```powershell
pytest -c tests/pytest.ini
```

If docs build is part of your local flow:

```powershell
cd docs
make html
```

Pass criteria:

- Docs are consistent with implemented behavior.
- Final branch is clean and review-ready.

## Phase 5 gate: live parity + CE audit + PR trim

Target:

- Validate practical fight behavior, close parity audit gaps, and reduce PR review burden.

Checks:

- Run Phase 5 live action-sequence and AI-unpaused-short profiles.
- Complete CE table parity audit artifacts.
- Run regression checks:

```powershell
pytest tests/eldenring/test_game.py -q -rs
pytest tests/envs/test_margit.py -q -rs
pytest -c tests/pytest.ini
```

Pass criteria:

- Live checks complete without crashes/hangs.
- CE audit doc and parity matrix are complete.
- Regression suite remains green with expected skips only.
- User confirms PR scope is trimmed to essentials.

## Review checklist for each gate

- Scope stayed inside current phase
- Tests for this phase passed
- No unrelated files changed
- Commit is small and readable
- Rollback point (tag) created

## Practical anti-regression rules

1. Do not edit more than one risk-heavy subsystem in the same commit.
2. Keep temporary debug instrumentation out of committed code.
3. Prefer additive test-first changes when possible.
4. If a phase gate fails 3 times in a row, stop and re-plan before more edits.
5. Do not delete old paths until replacement path is tested.

## Phase ownership map

- Phase 1: `soulsgym/core/data/eldenring/*`, `soulsgym/games/eldenring.py`
- Phase 2: `soulsgym/envs/eldenring/margit.py`
- Phase 3: `tests/*`, `scripts/run_envs.py`, `test_random_agent.py`
- Phase 4: `README.md`, `docs/*`
- Phase 5: `scripts/*`, `soulsgym/core/data/eldenring/*`, `soulsgym/games/eldenring.py`, `soulsgym/envs/eldenring/margit.py`, `docs/*`, `tests/*`

## Start protocol (before coding)

1. Confirm this workflow document and plan document are approved.
2. Run baseline checks and save results.
3. Create `checkpoint/pre-margit-rework` tag.
4. Start Phase 1 branch and implement only Phase 1 scope.

Only after these four steps do we begin implementation.