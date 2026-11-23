# Margit Rework Phase 3 Plan (2026-07-08)

Status: Planning only. No implementation is included in this phase document.

## Phase goal

Stabilize warning-heavy runtime behavior and clean the validation surface so future work is easier to verify and safer to run live.

Primary outcomes:

1. Unknown animation warnings are reduced to known, explainable edge cases.
2. Throwaway validation paths are removed or replaced with canonical scripts.
3. Live test routines are standardized in low-risk modes.

## Scope boundaries

In scope:

- Elden Ring animation mapping and decode behavior.
- Margit warning handling strategy.
- Test-harness and script cleanup.
- Documentation updates for safe live validation usage.

Out of scope:

- Coordinate calibration for full arena setup precision.
- Phase-2 Margit transition calibration.
- Long endurance stress tests beyond low-risk live profiles.

## File-by-file plan

## 1) Animation mapping and decode

### soulsgym/core/data/eldenring/animations.yaml

Planned work:

- Expand player standard animations with a practical baseline set used during live runs.
- Add boss animation IDs/categories for commonly observed Margit runtime values.
- Keep `critical` explicitly typed as list and document how unknowns are handled.

Done criteria:

- No repetitive unknown-animation warnings in a 5-cycle low-risk run unless encountering genuinely new IDs.

### soulsgym/games/eldenring.py

Planned work:

- Refine `margit_animation` decoding so integer values map to stable canonical strings.
- Ensure decode behavior stays deterministic for both known and unknown IDs.

Done criteria:

- `margit_animation` output format is consistent and testable across runs.

## 2) Margit environment warning hygiene

### soulsgym/envs/eldenring/margit.py

Planned work:

- Keep warnings actionable and non-spammy.
- Add concise warning paths for placeholders vs true unexpected runtime states.

Done criteria:

- Logs remain useful during live scenario runs and do not flood output.

## 3) Script and harness cleanup

### test_random_agent.py

Planned work:

- Remove or replace with canonical runner behavior using gym API lifecycle.
- Eliminate private-state mutation patterns.

Done criteria:

- No root-level script bypasses environment lifecycle.

### scripts/run_envs.py

Planned work:

- Add safe profile mode for live validation:
  - reset-only mode
  - one-step mode
  - short cycle mode

Done criteria:

- One official script supports low-risk live checks used in the phase gates.

### tests/envs/test_margit.py

Planned work:

- Preserve skip guards.
- Add one optional live marker profile test (short and safe) if appropriate.

Done criteria:

- Test behavior is predictable in game-off and game-on contexts.

## 4) Documentation updates

### docs/margit_rework_workflow.md

Planned work:

- Add explicit Phase 3 gates and low-risk live check profile.

Done criteria:

- Workflow captures exact pass criteria used for this phase.

### docs/margit_rework_phase3_result_2026-07-08.md

Planned work:

- Create result report only after implementation and gates run.

Done criteria:

- Report includes command list, outputs summary, and approval status.

## Gate plan for Phase 3

## Gate A: Animation decode sanity

Checks:

```powershell
pytest tests/eldenring/test_game.py -q -rs
```

Pass:

- No regression in existing Elden Ring attribute tests.

## Gate B: Warning reduction live-lite

Checks:

- Run 5-cycle low-risk live script profile (reset + action 19).

Pass:

- Unknown animation warnings are reduced and categorized; no crashes.

## Gate C: Harness cleanup validation

Checks:

```powershell
pytest tests/envs/test_margit.py -q -rs
pytest -c tests/pytest.ini
```

Pass:

- Margit env test remains stable.
- Default suite remains green under current skip policy.

## Gate D: Workflow/documentation closure

Checks:

- Update workflow and phase report docs.

Pass:

- Clear record of what changed, what passed, and residual risks.

## Residual risks after Phase 3

1. Placeholder coordinates still limit realistic arena setup behavior.
2. Phase-2 transition for Margit remains uncalibrated.
3. Full-fight random-agent robustness still depends on future data calibration.

## Approval policy

Phase 3 should only be approved when all four Phase 3 gates pass and the phase result doc is reviewed.