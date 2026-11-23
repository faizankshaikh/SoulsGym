# Margit PR Readiness Plan

Working plan for `margit-rework/phase-1-data-interface`.

## PR Contract

This PR ships the baseline Elden Ring Margit environment registered as
`SoulsGymMargit-v0`, along with only the game-interface, data, documentation, and
test changes necessary to support it.

The PR must distinguish two claims:

- The environment has a stable, documented Gymnasium interface.
- The live Elden Ring integration has been validated from a prepared, safe game state.

Calibration progress, observation campaigns, analysis notebooks, and local-only
runner tooling are not part of the shipped feature.

## Working Rules

- Compare the branch against `fork/master`.
- Treat `git diff fork/master...HEAD` as the source of truth for PR scope.
- Work on one gate at a time. Do not begin the next gate until its review checkpoint
	 has been approved.
- Preserve each accepted, known-working state with a checkpoint commit before
	 beginning the next gate.
- Keep deterministic tests independent of a running Elden Ring process. Mark all
	tests that require the game as `integration` tests.

## Human Review Protocol

Every gate has a human review checkpoint. At each checkpoint, the reviewer must
inspect the stated acceptance evidence, the diff since the preceding checkpoint,
and the remaining worktree status. The reviewer then explicitly chooses one of:

- **Approve:** create the gate checkpoint and continue.
- **Revise:** record the required changes; do not start the next gate.
- **Defer:** move nonessential work to a separate branch or issue before continuing.
- **Stop:** preserve the current state and revisit the PR contract.

Approval is not inferred from a passing command. Commands provide evidence; a
person accepts the resulting scope and behavior.

## Version-Control Safety Protocol

### Before Every Gate

1. Run `git status --short --branch` and review all uncommitted changes.
2. Run `git diff --check` and inspect `git diff --stat` against the preceding
	 checkpoint.
3. Confirm that the planned work belongs only to the current gate.
4. If unrelated work is present, leave it untouched and isolate it in another
	 branch, commit, or worktree before proceeding.

### At Every Approved Gate

1. Run the gate's focused validation commands.
2. Inspect `git diff --check`, `git diff --stat`, and the relevant full diff.
3. Create one small checkpoint commit with a gate-specific message, for example
	 `pr-readiness(gate-2): define Margit environment contract`.
4. Create an annotated tag after human approval, for example
	 `checkpoint/pr-readiness-gate-2`.
5. Record the commit SHA, tag, validation commands, outcomes, and deferred items
	 in the PR description or review notes.

### Change-Control Rules

- Do not amend, squash, rebase, or force-push a reviewed checkpoint without a new
	human review. Add a follow-up commit instead.
- Do not mix exploratory observation, calibration, or unrelated cleanup into a
	readiness gate. Use a separate branch from the last approved checkpoint.
- When a validation result changes the PR contract, stop at the current gate and
	obtain review before changing implementation scope.
- Never use destructive Git commands to recover from an experiment. Return to the
	most recent tag by creating a new branch or revert commit after review.
- Keep local logs and generated artifacts outside the tracked diff unless the
	reviewer has explicitly accepted them as PR evidence.

## Gate 0: Establish a Reviewable Baseline

### Objective

Freeze the intended scope before changing behavior.

### Actions

1. Review the current worktree and either include the four modified implementation
	 files in the next checkpoint or explicitly discard/defer them.
2. Add this plan to the checkpoint once its content is accepted.
3. Record the baseline commit and the changed-file list against `fork/master`.
4. Confirm whether Margit is presented as a baseline environment with known
	 limitations, rather than a fully calibrated encounter.

### Acceptance Evidence

- `git status --short` contains only intentional work.
- The changed-file manifest assigns every file `keep`, `remove`, or `defer`.
- A checkpoint commit preserves the accepted baseline.

### Review Checkpoint

Human review: approve the manifest, PR contract, known limitations, and baseline
checkpoint tag before proceeding to Gate 1.

### Gate 0 Working Notes (Approved)

- Baseline checkpoint commit approved: `284b7e3`
- Baseline checkpoint tag approved: `checkpoint/pr-readiness-gate-0`
- Baseline branch: `margit-rework/phase-1-data-interface`
- Baseline framing confirmed: Margit is presented as a baseline environment with
	known live-state limitations, not a fully calibrated encounter.

#### Changed-File Manifest (`git diff --name-status fork/master...HEAD`)

| File | Disposition | Gate 0 rationale |
| --- | --- | --- |
| `.gitignore` | `defer` | Keep only if required by shipped artifacts; re-evaluate in Gate 1. |
| `PR_READINESS_PLAN.md` | `defer` | Working planning artifact; not part of shipped PR scope. |
| `README.md` | `keep` | User-facing docs are in scope, but must be trimmed in Gate 5. |
| `docs/envs/index.rst` | `keep` | Required docs surface; minimal content only. |
| `docs/envs/margit.rst` | `keep` | Margit environment docs are required for shipped behavior. |
| `docs/games/eldenring.rst` | `keep` | Elden Ring game-interface docs are in scope if minimal. |
| `scripts/run_envs.py` | `remove` | Margit observation and calibration workflows migrate to the dedicated manual harness. |
| `soulsgym/__init__.py` | `keep` | Registration/public export path for environment availability. |
| `soulsgym/core/data/eldenring/actions.yaml` | `keep` | Runtime data dependency for Elden Ring behavior. |
| `soulsgym/core/data/eldenring/addresses.yaml` | `keep` | Runtime data dependency; mandatory quality review in Gate 1. |
| `soulsgym/core/data/eldenring/animations.yaml` | `keep` | Runtime data dependency; mandatory taxonomy review in Gate 1. |
| `soulsgym/core/data/eldenring/coordinates.yaml` | `keep` | Runtime data dependency for encounter setup/state. |
| `soulsgym/core/data/eldenring/player_stats.yaml` | `keep` | Runtime data dependency for player state handling. |
| `soulsgym/core/game_window.py` | `keep` | Capture behavior appears required; parity/necessity review pending. |
| `soulsgym/core/memory_manipulator.py` | `keep` | Core game-memory interface dependency. |
| `soulsgym/core/static.py` | `keep` | Shared static/data-loading behavior required by runtime path. |
| `soulsgym/envs/eldenring/margit.py` | `keep` | Primary environment implementation in PR contract. |
| `soulsgym/envs/utils.py` | `keep` | Shared env utility used by new/updated env behavior. |
| `soulsgym/games/eldenring.py` | `keep` | Primary Elden Ring game-interface implementation in contract. |
| `soulsgym/games/game.py` | `keep` | Base game abstraction changes required by Elden Ring integration. |
| `tests/eldenring/test_game.py` | `keep` | In scope with required safety bug fix and integration marking. |
| `tests/envs/test_margit.py` | `keep` | In scope; will absorb required checks from deleted runner script. |

#### Gate 0 Reviewer Decision (Recorded)

1. Manifest approved.
2. Gate 0 checkpoint approved and tagged.
3. `PR_READINESS_PLAN.md` remains deferred from final PR scope.

## Gate 1: Reduce Scope to Shipped Behavior

### Keep Only When Required

- Environment registration and public exports.
- Margit environment lifecycle and Elden Ring game-interface support.
- Memory addresses, animation/action/coordinate/stat data consumed by that code.
- Image capture or static configuration required by the registered environment.
- Focused tests and minimal user-facing documentation.

### Remove or Defer

- Do not silently remove active developer observation workflows.
- Any migration or split of runner features requires explicit human approval with
	a preserved source location and replacement command path.
- Notebooks, logs, generated calibration artifacts, and phase-history documents.
- `.gitignore` rules unrelated to generated artifacts required by the PR.
- Documentation describing branch history, implementation process, or unshipped
	calibration work.

### File-Specific Decisions

| Surface | Required decision |
| --- | --- |
| `addresses.yaml` | Identify legitimate module bases; remove obsolete commented blocks or make validated entries active with a concise usage comment. |
| `animations.yaml` | Ensure categories are clear, behavior-oriented, and consumed by environment/game logic. Remove unused or ambiguous taxonomy. |
| `eldenring.py` | Keep a separate raw Margit animation map only when standard mapping cannot represent the data; document the reason and ownership. |
| `static.py`, `game_window.py` | Retain only capture/static behavior required for Margit; justify any resolution-specific behavior. |
| `README.md`, docs | Describe shipped setup and behavior only; retain known safety limitations where users need them. |

### Acceptance Evidence

- Every file in `git diff --name-status fork/master...HEAD` has an explicit disposition.
- No observation or calibration workflow is silently deleted.
- `ai-unpaused-observe` (or approved replacement) remains usable and reports output paths.
- `git diff --check fork/master...HEAD` passes.

### Review Checkpoint

Human review: approve the post-trim manifest and full diff. Tag the accepted scope
before implementation changes continue.

### Gate 1 Working Notes (Approved)

Status: **approved on 2026-07-11**. Create and tag the Gate 1 checkpoint before
starting Gate 2 implementation work.

#### Runner Migration Decision

- Selected path: remove `scripts/run_envs.py` and migrate the remaining Margit
	operational workflows to `tests/envs/test_margit_manual.py`.
- The replacement is an explicit executable harness, not a pytest-discovered
	test module. It keeps user-assisted observation and calibration separate from
	automated and destructive environment tests.
- Recovery source used: `scripts/run_envs.py` restored from commit `9313d07`
	before its Margit-specific capabilities were migrated.

#### `run_envs.py` Capability Migration Inventory

| Previous capability | Disposition | Replacement or rationale |
| --- | --- | --- |
| `full`, `reset-only`, `one-step`, `short-cycle`, `action-sequence` | Retire | These manipulate/reset the game. Contract checks belong in pytest; destructive scenarios remain quarantined. |
| `ai-unpaused-short` | Retire | It resets and acts through the environment, so it belongs with future destructive-validation safety work. |
| `ai-unpaused-observe` | Migrate | `python tests/envs/test_margit_manual.py observe` preserves user-controlled state capture. |
| `ai-unpaused-summary` | Migrate | `python tests/envs/test_margit_manual.py summary` reads Margit observer JSON artifacts. |
| `calibration-capture` | Migrate | `python tests/envs/test_margit_manual.py capture-calibration` writes a labeled Margit coordinate sample. |
| `--env`, `--profile`, `--cycles` | Retire | The replacement is intentionally Margit-only and does not multiplex unrelated profiles. |
| `--steps`, `--interval`, `--stop-on-player-death` | Migrate | `observe` command options. |
| `--observer-json` | Migrate | `summary` command option. |
| `--capture-key` | Migrate | `capture-calibration` command option. |
| `--game-resolution` | Migrate | `observe` and `capture-calibration` command options; default is the verified `800x450`. |
| Observer CSV/JSON, calibration JSON, artifact-path reporting | Migrate | Retained by the Margit manual harness with timestamped output paths. |
| Captured image frames | Do not retain | Live checks validate in-memory image shape only. Observation artifacts keep numeric state and metadata, not screenshots or video. |

#### Test Migration Corrections

- Integration action-sequence test now fails on unexpected early
	`terminated`/`truncated` conditions.
- Contract tests run without a game process. Unattended integration tests require
  a running game but no player positioning or game-state mutation. Manual
  destructive scenarios reset, move, or act through the environment and are not
  normal integration tests.
- `tests/envs/test_margit.py` marks reset, one-step, and action-sequence scenarios
	with both `integration` and `manual_destructive`; they do not belong in
	unattended CI runs or the user-guided observation workflow.
- The live environment-creation scenario is also `manual_destructive`, because
	its current fixture teardown calls `env.close()`, which kills the player to
	force a reload.

#### Integration Marker Registration

- Added root `pytest.ini` with `integration`, `manual_destructive`, `iudex`, and
	`vordt` markers to match root invocations.

#### Test Execution Modes

| Mode | Command | Preconditions | Purpose |
| --- | --- | --- | --- |
| Automated | `conda run -n soulsgym python -m pytest -rs` | None | Deterministic tests only. |
| Unattended integration | `conda run -n soulsgym python -m pytest -m "integration and not manual_destructive" -rs` | Game process running when applicable | Read-only or self-contained live checks only. |
| Gameplay observation | `conda run -n soulsgym python tests/envs/test_margit_manual.py observe --steps 10000 --interval 0.2 --stop-on-player-death --game-resolution 800x450` | User controls the fight in a prepared arena | Capture CSV/JSON gameplay logs; not a pytest replacement. |
| Manual destructive validation | Not part of the current approval workflow | Dedicated disposable save and an approved safety procedure | Future reset/step/action validation only after fail-fast safeguards are designed and reviewed. |

#### Validation Commands And Outcomes

1. `conda run -n soulsgym python -m pytest -rs`
	- Result: pass.
	- Summary: `26 passed, 31 skipped, 8 deselected`.
	- Unknown-marker warnings: none.

2. `conda run -n soulsgym python -m pytest -m "integration and not manual_destructive" -rs`
	- Result: pass.
	- Summary: `25 passed, 4 skipped, 36 deselected`.
	- Manual destructive Margit scenarios are excluded.

3. `conda run -n soulsgym python -m pytest -m manual_destructive -rs`
	- Result: deliberately not run. These scenarios can reload, teleport, reset,
	  and issue actions to the live game.
	- Collection check: exactly four destructive Margit scenarios selected.
	- Do not run this selector until a fail-fast safety procedure, disposable-save
	  workflow, and explicit human approval are in place.

4. Historical incident only, **do not rerun**: `conda run -n soulsgym python
	-m pytest -m integration -rs`.
	- Result: failed in live Margit integration execution before destructive
	  scenarios were separated.
	- Summary: `3 failed, 1 passed, 4 skipped, 57 deselected`.
	- Failure cause: prepared game-state precondition not met (`_arena_setup`
	  could not place player at fog wall), not marker registration issues. This is
	  now classified as a destructive-scenario safety failure rather than
	  unattended integration evidence.
	- Unknown-marker warnings: none.

5. `conda run -n soulsgym python -m ruff check --output-format concise soulsgym`
	- Result: pass.

6. Supervised observation and summary validation
	- Previous runner capture passed. The migrated harness summary command passed
	  against the same artifact.
	- Artifacts: `logs/observer/ai_unpaused_observe_20260711_141036.csv` and
	  `logs/observer/ai_unpaused_observe_20260711_141036.json`.
	- Migrated summary command: `conda run -n soulsgym python
	  tests/envs/test_margit_manual.py summary --observer-json
	  logs/observer/ai_unpaused_observe_20260711_141036.json`.
	- Summary result: pass. The report read 60 alive samples, phase 1 throughout,
	  and the expected animation, HP, pose, and lock-on fields.
	- Migrated capture command: `conda run -n soulsgym python
	  tests/envs/test_margit_manual.py observe --steps 60 --interval 0.2
	  --stop-on-player-death --game-resolution 800x450`.
	- Migrated capture result: pass. Captured 47 samples and stopped at player
	  death as requested.
	- Migrated artifacts: `logs/observer/ai_unpaused_observe_20260711_143237.csv`
	  and `logs/observer/ai_unpaused_observe_20260711_143237.json`.
	- Migrated summary result: pass. It read 47 samples, reported death at step 47,
	  and retained the expected phase, HP, animation, pose, and lock-on fields.
	- Pause-safety follow-up failed: a 10-sample capture printed the pause marker,
	  but Elden Ring crashed. The harness must not use pause/resume or game-flag
	  writes.
	- Read-only safety validation: pass. A user-confirmed 10-sample capture completed
	  with no game-control behavior and the game remained stable and controllable.
	- Read-only capture command: `conda run -n soulsgym python
	  tests/envs/test_margit_manual.py observe --steps 10 --interval 0.2
	  --stop-on-player-death --game-resolution 800x450`.
	- Read-only artifacts: `logs/observer/ai_unpaused_observe_20260711_143921.csv`
	  and `logs/observer/ai_unpaused_observe_20260711_143921.json`.
	- Read-only summary: pass. It read 10 samples with no player death, no phase
	  transition, and no unknown animation frames.
	- Renamed-harness validation: pass. `tests/envs/test_margit_manual.py observe`
	  captured 10 stable samples with user-confirmed game control and wrote
	  `logs/observer/ai_unpaused_observe_20260711_144510.csv` and
	  `logs/observer/ai_unpaused_observe_20260711_144510.json`.
	- Targeted read-only properties: pass. The `player_hp`, `margit_hp`, and
	  `lock_on` integration checks passed without constructing the Margit
	  environment or invoking its lifecycle.
	- Renamed-harness summary: pass. It read the 10-sample artifact with no player
	  death, phase transition, or unknown animation frames.
	- Read-only image-capture validation: pass. The `img` game-interface check
	  validated the in-memory `90x160x3` frame shape in 0.91 seconds with
	  user-confirmed game stability. No image artifact was written.
	- Resolution-override isolation: pass. Eight non-live focused tests verified
	  that `800x450` remains the default, valid overrides are instance-local,
	  malformed dimensions are rejected, and the Elden Ring factory forwards
	  overrides consistently.
	- Resolution-override scope decision: retain it for the validated Margit
	  `800x450` capture path; it is capture configuration only and must not
	  mutate shared defaults.
	- Elden Ring address-data review: pass. All active address records resolve
	  through the five required pattern bases; the fixed `bases` mapping is
	  intentionally empty and now explicit. Inactive Cheat Engine reference
	  patterns were removed, and a non-live invariant verifies that every
	  shipped address references a configured base.
	- Margit animation-taxonomy review: pass. The shipped mapping now contains
	  only `Idle`, `Unknown`, and observed `Raw_*` labels. Speculative attack,
	  movement, and phase-transition labels were removed; phase-two setup uses
	  its explicit HP threshold until transition semantics are calibrated.
	  An offline regression test protects this observation-only contract.
	- Static-data loader review: retain unchanged. `static.py` remains required
	  shared infrastructure for input mapping, memory-base resolution, and game
	  data. Its Elden Ring data loads offline with five pattern bases, 25 address
	  records, and 12 Margit observation labels.
	- Ignore-rule review: retain unchanged. Existing rules ignore generated
	  tooling output and the `logs/observer/` and `logs/calibration/` live
	  artifact directories, while new test, configuration, and documentation
	  sources remain trackable.
	- Public documentation review: pass. README and Margit documentation now
	  distinguish read-only observation from experimental game-mutating
	  reset/step control. The strict Sphinx HTML build completed with no warnings.
	- Manual-harness construction safety: corrected. The observation and
	  calibration commands now use `read_only=True`, which skips initial
	  speedhack and environment-setup writes. Three offline regression tests
	  verify the no-write construction path and factory forwarding. A new
	  10-sample supervised observer run passed with user-confirmed game
	  stability and control; it wrote
	  `logs/observer/ai_unpaused_observe_20260711_150540.csv` and
	  `logs/observer/ai_unpaused_observe_20260711_150540.json`.
	- Pytest safety boundary: pass. Default selections from both the repository
	  root and `tests/` exclude integration and manual-destructive tests.
	- Gate 1 full-diff review: pass. The default safe suite completed with
	  `13 passed, 31 skipped, 32 deselected`; all manual-destructive lifecycle
	  scenarios remain intentionally quarantined and were not run.

#### Gate 1 Approval (Recorded)

- No remaining Gate 1 scope decisions.
- Human approval: 2026-07-11.
- Scope correction: Dark Souls III changes were reverted. Gate 1 behavior changes
	  are limited to Elden Ring and Margit.

## Gate 2: Verify the Public Environment Contract

### Retrospective Plan Review (Required First Task)

Before changing or running any Gate 2 contract behavior, review and update this
plan against the following established constraints:

1. A command is read-only only when both construction and execution avoid process
	   writes. Inspect constructors, setup hooks, teardown, and helper defaults; do
	   not infer safety from the absence of `reset()` or `step()` calls alone.
2. `reset()`, `step()`, action input, pause/resume, flag writes, reload, and
	   `close()` are destructive in the current Margit implementation. Keep their
	   tests under `manual_destructive`; do not run them as ordinary integration
	   evidence.
3. Default test commands must exclude both `integration` and
	   `manual_destructive`, whether invoked from the repository root or `tests/`.
4. Gate 2 contract logic must first be verified with controlled fakes or mocks.
	   A live read-only check validates only the read path actually exercised.
5. Keep Elden Ring/Margit changes local. Existing Dark Souls III code is a
	   reference for behavior review, not a target for API cleanup or consistency
	   refactors.
6. Every live scenario needs an explicit user approval, bounded command,
	   documented preconditions, stability confirmation, and an artifact policy.
	   Image frames stay in memory; observer and calibration metadata remain ignored.
7. Any change after a human gate approval reopens the affected review and requires
	   fresh focused validation.

### Gate 2 Review Boundary

- Classify every public contract item as deterministic, read-only live, or
	  manual-destructive before implementing tests.
- Do not widen the scope to a complete encounter lifecycle. The current PR may
	  document lifecycle limitations, but it must not claim unverified stability.
- Preserve `read_only=True` for user-assisted observer and calibration commands;
	  add a regression whenever construction can introduce a new process write.

### Required Behavior

1. Importing `soulsgym` registers `SoulsGymMargit-v0`.
2. Construction exposes valid action and observation spaces.
3. `reset()` returns `(observation, info)` and establishes a valid encounter state.
4. `step(action)` validates actions and returns the complete Gymnasium tuple with a
	 stable observation shape and dtype.
5. Rewards, termination, truncation, phase transitions, player death, boss death,
	 errors, and `close()` have deliberate, documented behavior.

Items 3 through 5 are contract-definition work first. Their live lifecycle
execution remains manual-destructive until separately designed and approved.

### Implementation Review

- Compare `margit.py` to existing Dark Souls environment lifecycles for
	initialization, reset, reward/events, terminal state, exception handling, and
	cleanup. Use that comparison to identify differences, not to modify Dark Souls
	code.
- Compare `eldenring.py` and `game.py` to the existing game abstraction. Each
	Elden Ring-specific difference must be necessary and covered by a test or short
	documentation.
- Ensure environment code has one authoritative source for animation mappings and
	data semantics.
- Audit constructor and teardown paths for writes before classifying any command
	  as read-only.

### Acceptance Evidence

- A reviewer can identify the code path for each required behavior.
- Public API differences from existing SoulsGym environments are documented and
	intentional.
- Each behavior has an explicit test lane: deterministic fake, read-only live, or
	  manual-destructive.

### Review Checkpoint

Human review: perform and approve a line-level parity review. Tag the accepted
contract before expanding or finalizing tests.

## Gate 3: Add Repeatable Test Evidence

### Deterministic Tests

Expand `tests/envs/test_margit.py` or focused neighboring tests to cover, without
requiring Elden Ring:

- Environment registration and constructor configuration validation.
- Action/observation-space contract and result tuple shape.
- Reward, phase, terminal-state, and cleanup logic through controlled fakes or
	mocks.
- Error behavior for unavailable/invalid game state where it is part of the
	environment contract.

### Live Integration Tests

- Mark every game-dependent test, including `tests/eldenring/test_game.py`, with
	`@pytest.mark.integration`.
- Keep unattended integration tests read-only. They must not allow player death,
	force a game reset, consume the player save, write flags, alter speed, or leave
	input held.
- Mark every lifecycle, action, reset, reload, pause/resume, or close test with
	`@pytest.mark.manual_destructive` in addition to `integration`. Run it only
	after an explicit future safety design and human approval.
- The test setup must reliably skip with a useful reason when Elden Ring is not
	available or not in-game.

### Acceptance Evidence

- Default `pytest` runs deterministic Margit coverage and does not rely on skipped
	live checks for success.
- `pytest -m "integration and not manual_destructive"` clearly selects the
	read-only game-dependent suite.
- The player-death/reset issue is prevented by classification and construction
	safety, then verified by an approved read-only live run.

### Review Checkpoint

Human review: approve the test list, results, and skipped-test reporting. Tag the
accepted automated evidence before live validation.

## Gate 4: Validate the Live Game Integration

### Preconditions

- Elden Ring is launched in offline mode with the documented settings.
- A disposable or backed-up save is used.
- The player is in the documented, safe starting state near the Margit encounter.
- Resolution and capture settings match the shipped documentation.

### Scenario

Run one short, user-approved, bounded read-only scenario. It may observe game
state, summarize a numeric artifact, or validate an in-memory image shape. It
must not call environment reset/step/close, send input, pause/resume, reload, or
write flags or speed.

### Record in the PR

- Command and environment used.
- Game resolution and setup assumptions.
- Scenario length and observed result.
- Any limitations, skipped checks, or manual steps.

### Acceptance Evidence

- The scenario completes successfully from a prepared game state, and the user
	  confirms the game remains stable and controllable.
- No process-write or unsafe game side effect occurs.
- The evidence is reproducible by a reviewer with the same prerequisites.

### Review Checkpoint

Human review: approve the recorded live evidence, safety result, and limitations.
Tag the accepted live-validation state before documentation is finalized.

## Gate 5: Align Documentation and Packaging

### Documentation Requirements

- README: platform/game prerequisites, safe-use warning, environment name, and a
	minimal Gymnasium example.
- Margit docs: setup prerequisites, required game state, read-only observation
	usage, and lifecycle limitations that affect users.
- Remove planning language, branch history, calibration status prose, and retired
	generic-runner instructions. Retain only necessary user-assisted read-only
	harness guidance.

### Packaging Requirements

- Elden Ring YAML data files required at runtime are included in package data.
- Imports and registration work from an installed package, not only the repository
	checkout.
- Documentation builds without warnings that conceal missing references.

### Acceptance Evidence

- Package build/install smoke check passes.
- Sphinx documentation build passes.
- User documentation matches the final public behavior and live-validation setup.

### Review Checkpoint

Human review: approve rendered documentation and installed-package smoke-check
evidence. Tag the release-candidate state before final sign-off.

## Gate 6: Final Sign-Off

Run and attach the results of the applicable checks:

```powershell
git diff --check fork/master...HEAD
ruff check soulsgym
pytest -rs
pytest -m "integration and not manual_destructive" -rs
```

Also run the package and documentation build commands used by this repository's
environment. When game prerequisites are unavailable, record the integration test
skips explicitly; they are not equivalent to a passing live validation.

### Final Reviewer Checklist

- Every changed file is essential to the stated PR contract.
- No local-only runner, generated artifact, planning archive, or unrelated cleanup
	is included.
- Data sources, mapping ownership, and Elden Ring-specific behavior are clear.
- Default tests provide meaningful deterministic coverage.
- Live tests are explicitly integration-marked and game-safe.
- A recorded live scenario validates the actual Elden Ring interaction.
- Documentation describes shipped behavior and safety prerequisites accurately.
- The final diff is clean, reviewable, and checkpointed.
- Every gate has a recorded human approval, checkpoint commit, and annotated tag.
- Any post-approval change is a reviewed follow-up commit with fresh validation.

## Suggested PR Description

Use these headings in the PR description:

1. Scope
2. Public Behavior
3. Automated Evidence
4. Live Validation
5. Known Limitations
6. Reviewer Checklist