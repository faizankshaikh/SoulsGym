# Margit Rework Plan (File by File)

## Plan Status Update (Phase 6 Kickoff: Calibration)

Completed:

- Phase 1: Elden Ring interface/data foundations
- Phase 2: Margit env lifecycle parity refactor
- Phase 3: animation warning reduction + harness/script cleanup
- Phase 4: docs and PR-readiness baseline updates
- Phase 5: live validation profiles, observer capture mode, CE parity audit, regression gates

Still pending:

- Phase 6: coordinate calibration and phase-2 setup calibration
- Full coordinate calibration for Margit reset/arena setup
- Margit phase-2 transition calibration
- Optional Elden Ring integration test module parity with DS3 harness

## PR footprint tracking (2026-07-09)

Measured against `origin/master...HEAD`:

- 33 files changed
- 3322 insertions, 57 deletions
- Docs-only churn: 1925 insertions, 0 deletions
- Non-doc code/data/tests churn: 1390 insertions, 57 deletions

Highest non-doc churn files:

- `scripts/run_envs.py` (473 add, 11 del)
- `soulsgym/envs/eldenring/margit.py` (440 add, 0 del)
- `soulsgym/games/eldenring.py` (239 add, 21 del)

Decision:

- PR-size trimming is deferred until all remaining technical tasks are complete.
- Do not perform broad cleanup/scope reduction mid-phase unless a blocker requires it.
- Final PR prep will include a dedicated trim pass to remove non-essential history/process noise.

Execution notes learned in live testing:

1. Live tests should run with the player **inside** the boss arena to avoid false negatives.
2. Elden Ring window/capture must be set to expected resolution profile (`800x450`) for reliable `GameWindow` init.
3. Low-risk live checks (`reset-only` / `one-step`) are the default safety profile before longer rollouts.

## Goal

Bring the Elden Ring Margit environment to the same operational quality level as the current Iudex environment, with:

- stable reset and step lifecycle
- predictable random-agent smoke behavior
- clear test coverage and regression gates
- PR-ready code quality and repository hygiene

## Current blockers summary

1. Margit coordinates remain placeholders and limit deterministic arena reset quality.
2. Margit phase-2 transition routine remains uncalibrated.
3. Animation table coverage still requires incremental updates as new IDs appear.
4. Phase-2 transition setup still needs calibrated trigger/verification conditions.
5. Final PR footprint remains larger than desired and requires an end-of-plan trim pass.

## File-by-file cleanup plan

## 1) Core environment implementation

### soulsgym/envs/eldenring/margit.py

Scope:

- Refactor to follow Iudex reset/step lifecycle style.
- Remove temporary bypass logic and commented dead blocks.
- Keep only Margit-specific logic where needed.

Planned changes:

- Restore full reset sequence:
  - input reset
  - game window focus
  - reload checks
  - arena setup checks
  - optional phase setup checks
  - entity reset
  - camera reset
  - game pause and state snapshot
- Move action application through base `SoulsEnv._apply_action` and `SoulsEnv._step` behavior unless a Margit-specific override is required.
- Align game state update semantics with existing envs.
- Tighten reward computation shape and terminal reward behavior to match project conventions.
- Add robust reset verification with retries and explicit error raises.

Acceptance criteria:

- `gymnasium.make("SoulsGymMargit-v0")` can run reset + looped stepping without internal manual state hacks.
- No commented-out critical lifecycle blocks remain.

## 2) Elden Ring game interface

### soulsgym/games/eldenring.py

Scope:

- Close parity gaps with functionality relied upon by `SoulsEnv` and Margit env.

Planned changes:

- Implement or complete required controls used during env reset and stabilization.
- Add helper methods expected by env logic (for example boss HP reset helpers if needed).
- Make animation type handling consistent with static animation tables and test expectations.
- Replace placeholder `reload()` behavior with a usable, testable implementation strategy.

Acceptance criteria:

- Required env calls are supported by Elden Ring interface without bypass paths.
- Reload and control toggles are deterministic enough for repeated episode resets.

## 3) Elden Ring static data

### soulsgym/core/data/eldenring/addresses.yaml

Scope:

- Complete address definitions used by env + game interface.

Planned changes:

- Fill missing addresses and verify pointer chains for all used properties.
- Verify correct read/write type annotations.
- Remove placeholder or incomplete entries that are no longer used.

Acceptance criteria:

- All addresses used by `EldenRing` and `MargitEnv` resolve and behave correctly.

### soulsgym/core/data/eldenring/coordinates.yaml

Scope:

- Replace dummy coordinate placeholders with full Margit coordinate set.

Planned changes:

- Add Margit coordinate schema matching existing boss env conventions:
  - `bonfire`
  - `fog_wall`
  - `post_fog_wall`
  - `center`
  - `player_init_pose`
  - optional `player_init_poses_random`
  - `boss_init_pose`

Acceptance criteria:

- Reset/setup code can position player/boss and validate poses with deterministic checks.

Current status:

- Schema added and consumed by env logic.
- Values are still placeholders and require in-game calibration.

### soulsgym/core/data/eldenring/animations.yaml

Scope:

- Expand from placeholder values to practical player and boss animation sets.

Planned changes:

- Add enough player animation timing entries for action validity masking.
- Add Margit animation categories for observation IDs and analysis.
- Track unknown animation fallback behavior and reduce warning noise.

Acceptance criteria:

- Action masks and obs animation IDs are stable during random-agent smoke tests.

Current status:

- Baseline warning reduction completed for observed IDs.
- Additional IDs may appear and should be added incrementally.

### soulsgym/core/data/eldenring/player_stats.yaml

Scope:

- Validate and tune Margit baseline stats for repeatable training conditions.

Acceptance criteria:

- Episodes start with expected HP/SP/MP and remain stable across resets.

### soulsgym/core/data/eldenring/bonfires.yaml

Scope:

- Verify selected grace used by Margit env for deterministic reset path.

Acceptance criteria:

- Reloads place player in a known route to arena setup.

## 4) Environment registration and packaging consistency

### soulsgym/__init__.py

Scope:

- Keep registration intact, ensure env ID metadata remains correct after refactor.

Acceptance criteria:

- Registration paths continue working for Margit env.

### pyproject.toml (verify only)

Scope:

- Ensure no packaging regressions from new/changed files.

Acceptance criteria:

- Package data and test configs remain valid.

## 5) Test suite hardening

### tests/envs/test_margit.py

Scope:

- Upgrade from creation-only test into meaningful smoke lifecycle test.

Planned changes:

- Add `reset()` call and short fixed number of `step()` calls.
- Include assertions for obs keys, info action mask shape, and basic termination semantics.
- Add robust skip condition when Elden Ring is not running.

Acceptance criteria:

- Test fails on lifecycle regressions, not just import/registration failures.

### tests/eldenring/test_game.py

Scope:

- Add checks for new Elden Ring interface capabilities used by Margit env.

Acceptance criteria:

- Interface regressions are detected before env integration failures.

### tests/pytest.ini

Scope:

- Add marker taxonomy for Elden Ring and Margit integration tests.

Acceptance criteria:

- Selective test execution is easy and explicit.

### tests/eldenring/integration_tests/test_envs.py (new)

Scope:

- Mirror DS3 integration harness style for Margit.

Acceptance criteria:

- One integration test path exists for full Margit loop in real game context.

Current status:

- Not added yet; deferred while live safety/stability was prioritized.

## 6) Throwaway script cleanup

### test_random_agent.py

Scope:

- Remove bypass-based script from repo root.

Planned changes:

- Either delete or replace with gym API compliant smoke script.

Acceptance criteria:

- No script in repo root mutates private env internals to fake lifecycle.

### scripts/run_envs.py

Scope:

- Extend as canonical smoke runner for all supported envs.

Acceptance criteria:

- Single standard script supports reproducible short validation runs for Margit.

## 7) Documentation updates

### README.md

Scope:

- Update status text only when technical gates pass.

Acceptance criteria:

- Margit status reflects tested reality.

Current status:

- Completed in earlier phases.

### docs/envs/index.rst and docs/envs/margit.rst (new)

Scope:

- Add Margit env docs page and include in docs index.

Acceptance criteria:

- Margit env appears in generated env docs.

Current status:

- Completed in earlier phases.

### docs/games/eldenring.rst

Scope:

- Document Elden Ring interface capabilities and known constraints.

Acceptance criteria:

- Contributors can understand what is implemented and reliable.

Current status:

- Completed in earlier phases.

## Risk and sequencing notes

- Addresses and coordinates are hard dependencies for stable env behavior. These should be completed before heavy env refactoring.
- `reload()` strategy in Elden Ring is a critical risk item and should be validated early with small experiments.
- Keep each phase small enough to revert with one commit if behavior regresses.

## Definition of "PR-ready" for this rework

1. Margit env follows standard lifecycle without private-state hacks.
2. Smoke and integration tests for Margit exist and pass in intended context.
3. No throwaway validation scripts remain in root.
4. Docs and status statements are accurate and consistent.
5. Changes are split into reviewable commits mapped to the workflow phases.
6. Final PR trim gate completed:
  - remove or defer non-essential process artifacts from the PR scope
  - keep only required code/data/tests and minimum supporting docs for reviewer context