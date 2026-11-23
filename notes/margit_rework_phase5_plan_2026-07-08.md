# Margit Rework Phase 5 Plan (2026-07-08)

Status: Planning only. No implementation included in this document.

## Why Phase 5

Phase 1-4 established baseline lifecycle, test gates, and docs readiness. Phase 5 focuses on practical fight behavior verification, missing parity checks versus Iudex, CE table audit, and PR review-scope minimization.

## Phase 5 objectives

1. Add a deterministic live action sequence check after lock-on:
   - light attack
   - heavy attack
   - roll
2. Run a controlled live behavior check with AI unpaused and capture failure modes.
3. Audit Elden Ring CE table coverage versus current Margit env/game interface usage.
4. Minimize PR review burden by removing or consolidating non-essential artifacts.

## Scope boundaries

In scope:

- New live check scripts and/or script profiles needed for the two runtime scenarios.
- CE table-to-code mapping audit and explicit gap report.
- Lean-up pass for scripts/docs introduced during rework.

Out of scope:

- Full training policy improvements.
- Broad new feature additions unrelated to Margit parity.

## File-by-file plan

## 1) Deterministic live action sequence check

### scripts/run_envs.py

Planned work:

- Add profile: `action-sequence`.
- Behavior in this profile:
  - reset env
  - ensure lock-on attempt
  - execute mapped actions: lightattack, heavyattack, roll
  - print per-step observation deltas and termination status

Done criteria:

- Script reliably executes the sequence in boss arena and reports pass/fail.

### test_random_agent.py

Planned work:

- Keep as canonical gym smoke only; no private internals and no overlapping behavior with `action-sequence` profile.

Done criteria:

- No duplication of action-sequence logic.

## 2) Unpaused AI controlled check

### scripts/run_envs.py

Planned work:

- Add profile: `ai-unpaused-short`.
- Behavior:
  - run short capped rollout with AI unpaused
  - capture survival, termination cause, reset recovery status
  - hard limit cycles/steps to avoid unstable long loops

Done criteria:

- Produces deterministic report output and does not leave environment in hung state.

## 3) Margit parity audit versus Iudex + CE table audit

### ce_tables/ER_TGA.CT

Planned work:

- Audit relevant entries for:
  - player stats and animation pointers
  - margit HP/pose/animation pointers
  - flags relevant to movement, attacks, hits, lock-on behavior, deaths

Done criteria:

- Mapped list of usable addresses and unresolved gaps.

### soulsgym/core/data/eldenring/addresses.yaml

Planned work:

- Add/adjust addresses discovered as reliable from audit.
- Keep only verified records and mark uncertain ones clearly.

Done criteria:

- Address file reflects validated usage path for current env behavior.

### soulsgym/games/eldenring.py and soulsgym/envs/eldenring/margit.py

Planned work:

- Align with any newly validated CE mappings.
- Document which parity features still differ from Iudex and why.

Done criteria:

- Clear parity checklist with implemented vs pending items.

### docs/margit_iudex_parity_audit_2026-07-08.md (new)

Planned work:

- Add explicit side-by-side parity matrix:
  - reset fidelity
  - arena setup fidelity
  - phase handling
  - action validity timing
  - lock-on resilience
  - critical animation handling
  - hp/sp/mp reset semantics

Done criteria:

- Single audit artifact reviewers can use to understand current equivalence level.

## 4) PR review-scope minimization

### scripts/, docs/, tests/

Planned work:

- Remove or consolidate low-value temporary artifacts.
- Keep only scripts/docs that support ongoing maintenance and reviewability.
- Ensure commit history remains phase-scoped and readable.

Done criteria:

- PR contains only required files and rationale-backed artifacts.

## Phase 5 gates

## Gate A: Action sequence live check

Pass criteria:

- `action-sequence` profile runs successfully in-boss-arena with lock-on and all 3 actions.

## Gate B: AI unpaused short check

Pass criteria:

- `ai-unpaused-short` profile completes and reports outcome without crashes/hangs.

## Gate C: CE table parity audit

Pass criteria:

- CE mapping audit doc completed.
- Address/code updates validated by tests.

## Gate D: Regression safety

Checks:

```powershell
pytest tests/eldenring/test_game.py -q -rs
pytest tests/envs/test_margit.py -q -rs
pytest -c tests/pytest.ini
```

Pass criteria:

- All gate tests pass with expected skips only.

## Gate E: PR-slim cleanup review

Pass criteria:

- File list is pruned to required scope.
- User review confirms no extra burden artifacts remain.

## Approval policy

Phase 5 implementation starts only after explicit user approval of this plan.