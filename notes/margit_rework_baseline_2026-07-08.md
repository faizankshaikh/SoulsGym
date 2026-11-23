# Margit Rework Baseline Snapshot (2026-07-08)

Environment:

- OS: Windows
- Conda env: `soulsgym`
- Python: 3.11.2

Commands run:

```powershell
pytest -c tests/pytest.ini
pytest tests/eldenring/test_game.py -q
```

Results:

1. `pytest -c tests/pytest.ini`
   - Collected: 60
   - Deselected: 4
   - Selected: 56
   - Passed: 0
   - Failed: 1
   - Skipped: 55
   - Failing test: `tests/envs/test_margit.py::test_margit_env_creation`
   - Failure reason: `RuntimeError: Process eldenring.exe not open`

2. `pytest tests/eldenring/test_game.py -q`
   - 24 skipped
   - No failures

Interpretation:

- Test environment and dependencies are correctly configured.
- Elden Ring specific tests are guarded and skip when the game is not running.
- Margit env test currently does not skip in game-off context and fails during env creation.

Pre-rework gate status:

- Baseline captured successfully.
- Known pre-existing failure recorded and accepted as initial state.