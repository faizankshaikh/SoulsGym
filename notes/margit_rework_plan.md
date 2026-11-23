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

## Phase 7: Rich gameplay data collection and analysis pipeline

Status: Planned. Starts after Phase 6 remaining tasks (integration test, script cleanup, regression gate).

### Overview

Goal: capture high-quality gameplay episodes at playable resolution, store structured trajectory data,
and build an offline analysis pipeline (frame inspection, animation timeline, reward curves).

This phase requires the player to run the game at full 1280x720 (borderless windowed or windowed)
rather than the current enforced 800x450. A "flip the switch" patch is needed to unlock this
without breaking the PR-ready 800x450 default.

---

### Task 7-A: Understand and unlock the resolution constraint

**Why 800x450 is a hard requirement today (root cause analysis):**

The constraint comes from two places in `soulsgym/core/game_window.py`:

1. **Class-level constant** (`game_resolution`, line 33): hardcoded `(800, 450)` for both games.
   All resolution logic reads from this single dict.

2. **`_determine_image_crop()`** (line 185): uses `game_resolution` as the *expected* capture size.
   It detects black padding around the window border and crops the raw frame down to match.
   Two hard `RuntimeError` guards:
   - `res_diff < 0`: game window is smaller than 800x450 → crop would go negative → fails.
   - `res_diff[0] > 50 or res_diff[1] > 10`: window is more than ~50 px taller or ~10 px wider
     than 800x450 → "resolution difference is too great" → fails.
   At 1280x720 the diff would be ~[270, 480], hitting the second guard immediately.

3. **`img_resolution` setter** (line 103): upper-bounds img size against `game_resolution`,
   so you cannot request a larger output image even if the window were bigger.

4. **Windowed requirement**: `pixel_forge.Window(name)` captures by Win32 window title.
   Fullscreen-exclusive mode does not expose a standard Win32 window title reliably, so the game
   must run in windowed or borderless-windowed mode regardless of resolution.

**What the "flip the switch" patch looks like:**

Minimal, reversible change — no PR-required behavior changes, just add an opt-in override:

- Add `game_resolution: tuple[int, int] | None = None` param to `GameWindow.__init__`.
  If provided, it overrides the class-level dict entry for the current instance only.
- Relax `_determine_image_crop()` tolerance when the instance resolution is larger than the
  800x450 default (or skip the tight tolerance check and fall back to a direct scale instead).
- Thread the param through `Game.__init__` (both `DarkSoulsIII` and `EldenRing`) as an optional
  kwarg so the env can pass it in.
- Default stays `None` (→ 800x450) so all existing behavior and tests are unaffected.
- The switch is explicitly marked "local patch, not for PR" in a code comment so it is
  easy to identify and remove during the final trim pass.

**Acceptance criteria for Task 7-A:**
- `GameWindow` accepts `game_resolution=(1280, 720)` at construction without error.
- `_determine_image_crop` succeeds and produces correct crop indices at 1280x720.
- Existing 800x450 tests continue to pass unmodified.
- A one-line change in `scripts/run_envs.py` or a CLI flag can toggle between resolutions.

---

### Task 7-B: Episode trajectory capture (post switch)

Extend `ai-unpaused-observe` to record all available `GameState` fields per step.
No video capture — metadata only.

Fields to add to each record (already available from `game_state()`):
- `phase`
- `player_sp`, `player_max_sp`, `player_max_hp`, `boss_max_hp`
- `player_pose` (x, y, z, angle)
- `boss_pose` (x, y, z, angle)
- `camera_pose` (x, y, z, dx, dy, dz)
- `player_animation_duration`, `boss_animation_duration`

Acceptance criteria:
- Observer JSON/CSV artifacts include all fields above.
- Existing summary print stays readable (prints only key fields, not poses).
- No video, no frame capture.

---

### Task 7-C: Offline analysis pipeline

Jupyter notebook at `notebooks/margit_eda.ipynb` that loads any observer JSON artifact and produces:

1. **HP/SP timelines** — player and boss HP over steps; stamina curve
2. **Event detection** — hits taken (player HP drops), damage dealt (boss HP drops)
3. **Animation frequency** — bar chart of player and boss animation distributions
4. **Positioning** — player x/y trajectory, distance to boss over time
5. **Suggestions** — rule-based improvement notes derived from the data:
   - Stamina management (sp_min vs max, depletion events)
   - Aggression ratio (attack animations vs dodge/guard animations)
   - Hit exposure (was player in an attack animation when they took damage?)
   - Positioning efficiency (average distance to boss)

Acceptance criteria:
- Notebook runs end-to-end on any observer JSON from `logs/observer/`
- All plots render inline
- Suggestions section prints readable text conclusions

---

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