# Margit Rework Phase 5 Result (2026-07-08)

Phase scope:

- Deterministic action-sequence live profile
- Controlled AI-unpaused short profile
- CE table parity audit artifact
- PR-scope reduction by keeping changes minimal and reviewable

Implemented changes:

1. `scripts/run_envs.py`
   - Added profile `action-sequence`:
     - reset
     - best-effort lock-on attempt
     - scripted actions: light attack (16), heavy attack (17), roll (8)
     - per-step reporting with HP/reward/termination fields
   - Added profile `ai-unpaused-short`:
     - explicit operator message that AI unpause is manual
     - bounded per-cycle rollout with deterministic logging
   - Added profile `ai-unpaused-observe`:
     - script does not issue combat actions
     - user plays manually while script samples game state timeline
     - captures both mapped boss animation and raw boss animation ID
     - explicit end marker is always emitted:
       - `observer_end_status=completed`
       - `observer_end_status=interrupted_by_user`
       - `observer_end_status=runtime_error`
       - `observer_end_status=player_death_stop`
     - automatic artifacts are saved per run:
       - `logs/observer/ai_unpaused_observe_<timestamp>.csv`
       - `logs/observer/ai_unpaused_observe_<timestamp>.json`
   - Refactored repeated logging into helper functions for cleaner output and lower review noise.

2. `soulsgym/core/data/eldenring/animations.yaml`
  - Added newly observed player animation IDs from live runs:
    - `5400`
    - `10202020`
    - `10202021`
    - `10202023`
    - `10202115`
  - This removed noisy unknown-animation warnings on follow-up validation runs.

3. `docs/margit_iudex_parity_audit_2026-07-08.md` (new)
   - Added parity matrix for reset/arena/phase/action/lock-on/animation/reset-semantics.
   - Added CE table cross-check summary and address-coverage conclusions.
   - Documented that no new address replacements were validated in this pass.

Gate outcomes:

## Gate A: Action sequence live check

Status:

- Completed.

Command executed:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile action-sequence --cycles 3
```

Observed result summary:

- 3 cycles completed.
- Lock-on attempt and full scripted sequence (16 -> 17 -> 8) executed each cycle.
- No termination/truncation during the sequence.
- Margit placeholder-coordinate warnings are still expected and appeared.
- Unknown player animation observed during run: `10202020`.
- Follow-up one-cycle rerun after animation mapping: no unknown-animation warnings.

## Gate B: AI unpaused short check

Status:

- Completed.

Command executed:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-short --cycles 3 --steps 8
```

Observed result summary:

- 3 cycles completed, 8 capped steps each.
- No crashes or hangs.
- AI-unpaused behavior produced HP deltas in cycle 1 (player and boss), proving non-trivial interaction.
- Unknown player animation observed repeatedly during run: `5400`.
- Follow-up short rerun after animation mapping: no unknown-animation warnings.

## Gate C: CE table parity audit

Status:

- Completed.
- Audit artifact added: `docs/margit_iudex_parity_audit_2026-07-08.md`.

## Gate D: Regression safety

Commands executed:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe -m pytest tests/eldenring/test_game.py -q -rs
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe -m pytest tests/envs/test_margit.py -q -rs
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe -m pytest -c tests/pytest.ini
```

Results:

- `tests/eldenring/test_game.py`: 24 passed
- `tests/envs/test_margit.py`: 1 passed
- Default suite: 25 passed, 31 skipped, 4 deselected
- Post-mapping confirmation rerun: 25 passed, 31 skipped, 4 deselected

## Gate E: PR-slim cleanup review

Status:

- Changes kept narrowly scoped to required Phase 5 items.
- No unrelated code paths were modified.

Assessment:

- Phase 5 code and audit deliverables are in place.
- Gate A/B/Gate C/Gate D are completed.
- Remaining work is final review and commit/tag flow.

## Post-fix quick validation (sequencing/recovery patch)

Commands executed:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile action-sequence --cycles 1
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-short --cycles 1 --steps 20
```

Observed outcomes:

- Gate A logic fix validated: settle no-op steps inserted between sequence actions and `sequence_pass=True`.
- Gate B logic fix validated: run completed full 20 steps without crashes/hangs and emitted summary counters.
- In this specific rerun, AI-unpaused profile showed `boss_animation_changes=0`, indicating no strong boss behavior variance was observed in that sample window.

## Gate B observer mode for manual play

Purpose:

- Capture richer boss/player behavior while the user plays manually.
- Detect whether logging ended normally or stopped mid-fight.

Command:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-observe --steps 300 --interval 0.2
```

Optional early-stop mode:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-observe --steps 300 --interval 0.2 --stop-on-player-death
```

Interpretation:

- If the run ends normally, output includes `observer_end_status=completed`.
- If interrupted by user, output includes `observer_end_status=interrupted_by_user`.
- If the script fails, output includes `observer_end_status=runtime_error`.

Latest observer evidence (manual-play sample):

- Run completed full `300` sampled steps at `0.2s` interval.
- Final marker: `observer_end_status=completed`.
- Summary: `player_anim_changes=97`, `boss_anim_changes=0`.
- HP trajectory captured meaningful combat progression:
  - Player HP: `455 -> 74`
  - Boss HP: `4174 -> 2978`

## Observer summary helper

Purpose:

- Produce a concise gate report from observer JSON artifacts without rerunning live capture.

Commands:

```powershell
# Summarize latest observer artifact
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --profile ai-unpaused-summary

# Summarize a specific artifact
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --profile ai-unpaused-summary --observer-json logs/observer/ai_unpaused_observe_YYYYMMDD_HHMMSS.json
```

Latest summary sample output:

- `observer_summary_file=logs/observer/ai_unpaused_observe_20260708_230534.json`
- `observer_gate_report status=completed runtime=0:00:24 steps_captured=120 alive_steps=78 death_step=79 player_hp_start=455 player_hp_end=-1082130432 boss_hp_start=4174 boss_hp_end=0 boss_damage=4174 unknown_boss_frames=108 unique_raw_boss_animation_ids=2`

Notes:

- `alive_steps` and `death_step` are the primary quality indicators when post-death memory values become noisy.
- For cleaner observer datasets, use `--stop-on-player-death` during capture.

## Observer evidence update (manual in-arena workflow, death-stop)

Command:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-observe --steps 600 --interval 10 --stop-on-player-death
```

Outcome:

- End marker: `observer_end_status=player_death_stop`.
- Capture stayed clean until death and avoided post-death value drift.
- Runtime: `0:00:50`.

Artifacts:

- `logs/observer/ai_unpaused_observe_20260708_234517.csv`
- `logs/observer/ai_unpaused_observe_20260708_234517.json`

Summary report:

- `observer_gate_report status=player_death_stop runtime=0:00:50 steps_captured=6 alive_steps=5 death_step=6 player_hp_start=455 player_hp_end=0 boss_hp_start=4174 boss_hp_end=3377 boss_damage=797 unknown_boss_frames=6 unique_raw_boss_animation_ids=1`

Interpretation:

- This run is valid evidence for manual-play observer workflow quality because data collection ends at player death instead of continuing into noisy memory states.

## Observer evidence update (second confirming sample)

Command:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-observe --steps 600 --interval 10 --stop-on-player-death
```

Outcome:

- End marker: `observer_end_status=player_death_stop`.
- Runtime: `0:00:40`.

Artifacts:

- `logs/observer/ai_unpaused_observe_20260708_234735.csv`
- `logs/observer/ai_unpaused_observe_20260708_234735.json`

Summary report:

- `observer_gate_report status=player_death_stop runtime=0:00:40 steps_captured=5 alive_steps=4 death_step=5 player_hp_start=455 player_hp_end=0 boss_hp_start=4174 boss_hp_end=3436 boss_damage=738 unknown_boss_frames=5 unique_raw_boss_animation_ids=1`

Interpretation:

- This second run corroborates the first death-stop sample: capture terminates cleanly at death and avoids post-death memory drift.

## Observer evidence update (2026-07-09 live baseline)

Command:

```powershell
C:/Users/faiza/miniconda3/envs/soulsgym/python.exe scripts/run_envs.py --env SoulsGymMargit-v0 --profile ai-unpaused-observe --steps 120 --interval 0.2 --stop-on-player-death
```

Outcome:

- End marker: `observer_end_status=player_death_stop`.
- Runtime: `0:00:19`.

Artifacts:

- `logs/observer/ai_unpaused_observe_20260709_000236.csv`
- `logs/observer/ai_unpaused_observe_20260709_000236.json`

Summary report:

- `observer_gate_report status=player_death_stop runtime=0:00:19 steps_captured=99 alive_steps=98 death_step=99 player_hp_start=455 player_hp_end=0 boss_hp_start=2508 boss_hp_end=2074 boss_damage=434 unknown_boss_frames=99 unique_raw_boss_animation_ids=1`

Interpretation:

- This run confirms stable manual-play observer capture under the death-stop protocol.
- Boss animation mapping remains incomplete (`unknown_boss_frames=99`) while raw boss animation ID remains stable (`unique_raw_boss_animation_ids=1`).

## Checkpoint update (2026-07-09 animation mapping pass)

Decision:

- Skip additional live data collection for now and use existing observer artifacts as mapping source.

Multi-run raw ID inventory used for mapping:

- `496506000` (108 frames)
- `497755216` (99 frames)
- `499056304` (44 frames)
- `496619600` (15 frames)
- `496873584` (10 frames)
- `497874032` (6 frames)
- `499912752` (5 frames)
- `502221968` (5 frames)
- `504659904` (newly observed in latest confirmation attempt)

Implemented mapping changes:

- Added raw Margit animation label mapping in `soulsgym/games/eldenring.py`.
- Registered mapped labels in `soulsgym/core/data/eldenring/animations.yaml` under `boss.margit.misc`.

Validation after mapping updates:

- `pytest tests/eldenring/test_game.py -q -rs`: 24 passed.
- `pytest tests/envs/test_margit.py -q -rs`: 1 passed.

Operational note:

- Additional live confirmation run after introducing `Raw_504659904` was explicitly deferred.
