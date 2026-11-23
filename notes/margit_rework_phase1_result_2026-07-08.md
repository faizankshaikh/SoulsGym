# Margit Rework Phase 1 Result (2026-07-08)

Phase scope:

- Elden Ring data + interface foundation
- No Margit env lifecycle refactor (Phase 2 scope)

Implemented changes:

1. `soulsgym/games/eldenring.py`
   - Added explicit control interface properties used by base env setup:
     - `allow_attacks`
     - `allow_hits`
     - `allow_moves`
     - `allow_deaths`
     - `lock_on_bonus_range`
     - `los_lock_on_deactivate_time`
   - Added `clear_cache`, `_save_game_flags`, `_restore_game_flags`.
   - Implemented non-placeholder `reload()` with timeout-based respawn wait.
   - Added `reset_boss_hp("margit")` helper.
   - Normalized `margit_animation` return contract to string.

2. `soulsgym/core/data/eldenring/addresses.yaml`
   - Added missing `MargitLocalXYZ` record required by `margit_pose` setter.

3. `soulsgym/core/data/eldenring/coordinates.yaml`
   - Replaced dummy structure with `margit` schema keys expected by env reset logic.
   - Values are placeholders and explicitly marked TODO for in-game calibration.

4. `tests/envs/test_margit.py`
   - Added game-off skip guard aligned with Elden Ring test conventions.

Gate commands run:

```powershell
pytest tests/eldenring/test_game.py -q
pytest tests/envs/test_margit.py -q
pytest -c tests/pytest.ini
```

Gate outcomes:

- `pytest tests/eldenring/test_game.py -q` -> 24 skipped, 0 failed
- `pytest tests/envs/test_margit.py -q` -> 1 skipped, 0 failed
- `pytest -c tests/pytest.ini` -> 56 skipped, 4 deselected, 0 failed

Live validation outcomes (game-on context):

- `python -u -c "from soulsgym.core.game_window import GameWindow; GameWindow('EldenRing'); print('gamewindow_ok')"` -> `gamewindow_ok`
- `pytest tests/envs/test_margit.py -q -rs` -> 1 passed
- `pytest tests/eldenring/test_game.py -q -rs` -> 24 passed

Assessment:

- Phase 1 objective achieved for game-off baseline stability and interface/data contract hardening.
- Phase 1 objective additionally validated in live game-on context.
- Next required step is checkpoint/tag, then explicit user approval before Phase 2 start.