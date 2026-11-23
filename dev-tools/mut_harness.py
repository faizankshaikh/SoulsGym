"""Mutation parity between the baseline (old) tests and the consolidated (new) tests.

Builds two scratch trees (outside the repository): ``old`` = baseline tests at 574c17c, ``new`` =
the tests in the working tree. Every mutant is applied to the same source file in both trees and
both suites are run. A mutant that only the old suite kills is a coverage gap of the new suite.

Usage: python mut_harness.py setup | run [mutant-id ...] | sanity
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(r"C:\Users\faiza\workspace\copilot-worktrees\testSoulsGym\faizankshaikh-friendly-potato")
HERE = Path(__file__).parent
MUT = HERE / "mut"
PY = r"C:\Users\faiza\miniconda3\envs\soulsgym\python.exe"
OLD_COMMIT = "574c17c"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def setup():
    """Create the old and new scratch trees."""
    if MUT.exists():
        shutil.rmtree(MUT)
    for name in ("old", "new"):
        (MUT / name).mkdir(parents=True)
        shutil.copytree(REPO / "soulsgym", MUT / name / "soulsgym", ignore=IGNORE)
    data = subprocess.run(
        ["git", "archive", OLD_COMMIT, "tests", "pytest.ini"],
        cwd=REPO,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(MUT / "old")
    shutil.copytree(REPO / "tests", MUT / "new" / "tests", ignore=IGNORE)
    shutil.copy(REPO / "pytest.ini", MUT / "new" / "pytest.ini")
    print("trees built")


def sync_new_tests():
    """Refresh the tests of the new tree from the working tree."""
    shutil.rmtree(MUT / "new" / "tests")
    shutil.copytree(REPO / "tests", MUT / "new" / "tests", ignore=IGNORE)
    shutil.copy(REPO / "pytest.ini", MUT / "new" / "pytest.ini")


def run_suite(tree: str, extra: list[str] | None = None) -> tuple[bool, str]:
    """Run the test suite of a scratch tree and return whether it passed and its output."""
    cmd = [PY, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "-rf", "--no-header"]
    cmd += extra or []
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        proc = subprocess.run(
            cmd, cwd=MUT / tree, env=env, capture_output=True, text=True, timeout=180
        )
    except subprocess.TimeoutExpired:
        return True, "TIMEOUT"
    out = proc.stdout + proc.stderr
    killed = proc.returncode != 0
    first = ""
    for line in out.splitlines():
        if line.startswith("FAILED ") or line.startswith("ERROR "):
            first = line[:170]
            break
    if killed and not first:
        first = out.strip().splitlines()[-1][:170] if out.strip() else f"rc={proc.returncode}"
    if not killed:
        first = out.strip().splitlines()[-1] if out.strip() else ""
    return killed, first


# (id, file relative to the tree root, old snippet, new snippet)
M = "soulsgym/envs/eldenring/margit.py"
S = "soulsgym/envs/soulsenv.py"
G = "soulsgym/games/eldenring.py"
MUTANTS = [
    # --- margit.py: reload / arena / phase / reset / close / reward / obs / spaces
    ("MG01 drop ingame check", M,
     '        if not self.game.is_ingame:\n            raise GameStateError("Player does not seem to be ingame")',
     '        if False:\n            raise GameStateError("Player does not seem to be ingame")'),
    ("MG02 margit_hp<=0 -> <0", M,
     "        if self.game.margit_hp <= 0:\n            return True",
     "        if self.game.margit_hp < 0:\n            return True"),
    ("MG03 hard reset x10", M,
     "        if time.time() - self._last_hard_reset > self.HARD_RESET_INTERVAL:",
     "        if time.time() - self._last_hard_reset > 10 * self.HARD_RESET_INTERVAL:"),
    ("MG04 reload keeps arena_init", M,
     "        self._arena_init = False\n        self._phase_init = False\n        self.game.reload()",
     "        self._phase_init = False\n        self.game.reload()"),
    ("MG05 reload keeps phase_init", M,
     "        self._arena_init = False\n        self._phase_init = False\n        self.game.reload()",
     "        self._arena_init = False\n        self.game.reload()"),
    ("MG06 reload does not reload", M,
     "        self.game.reload()\n        self._last_hard_reset = time.time()",
     "        self._last_hard_reset = time.time()"),
    ("MG06b reload keeps hard reset time", M,
     "        self.game.reload()\n        self._last_hard_reset = time.time()",
     "        self.game.reload()"),
    ("MG07 arena setup skips fog gate", M,
     "        self._enter_fog_gate()\n        self._arena_init = True",
     "        self._arena_init = True"),
    ("MG08 arena setup keeps arena_init", M,
     "        self._arena_init = True\n        self._phase_init = False  # When we reload",
     "        self._phase_init = False  # When we reload"),
    ("MG09 arena setup sets phase_init", M,
     "        self._phase_init = False  # When we reload, the phase is automatically reset to 1",
     "        self._phase_init = True  # When we reload, the phase is automatically reset to 1"),
    ("MG09b arena setup does not pause", M,
     "        self._phase_init = False  # When we reload, the phase is automatically reset to 1\n        self.game.pause()",
     "        self._phase_init = False  # When we reload, the phase is automatically reset to 1"),
    ("MG10 fog wall teleport never fails", M,
     "            if np.linalg.norm(d_pos) <= 2.0:\n                break",
     "            if True:\n                break"),
    ("MG11 phase ratio 0.7", M,
     "PHASE2_HP_THRESHOLD_RATIO = 0.6", "PHASE2_HP_THRESHOLD_RATIO = 0.7"),
    ("MG12 phase ratio 0.5", M,
     "PHASE2_HP_THRESHOLD_RATIO = 0.6", "PHASE2_HP_THRESHOLD_RATIO = 0.5"),
    ("MG13 threshold +1", M,
     "        hp_threshold = int(self.game.margit_max_hp * self.PHASE2_HP_THRESHOLD_RATIO)",
     "        hp_threshold = int(self.game.margit_max_hp * self.PHASE2_HP_THRESHOLD_RATIO) + 1"),
    ("MG13b threshold -1", M,
     "        hp_threshold = int(self.game.margit_max_hp * self.PHASE2_HP_THRESHOLD_RATIO)",
     "        hp_threshold = int(self.game.margit_max_hp * self.PHASE2_HP_THRESHOLD_RATIO) - 1"),
    ("MG13d threshold > -> >=", M,
     "        while self.game.margit_hp > hp_threshold:",
     "        while self.game.margit_hp >= hp_threshold:"),
    ("MG14 phase setup ignores player death", M,
     '            if self.game.player_hp <= 0:\n                raise ResetError("Player has died during the phase 2 setup")',
     '            if False:\n                raise ResetError("Player has died during the phase 2 setup")'),
    ("MG15 phase setup never times out", M,
     '                raise ResetError("Margit did not reach the phase 2 HP threshold")',
     "                break"),
    ("MG16 phase setup keeps phase_init", M,
     "        self.game.pause()\n        self._phase_init = True",
     "        self.game.pause()"),
    ("MG17 phase setup does not pause", M,
     "        self.game.pause()\n        self._phase_init = True",
     "        self._phase_init = True"),
    ("MG18 phase setup required ignores init", M,
     "        return self.phase == 2 and not self._phase_init",
     "        return self.phase == 2"),
    ("MG19 phase setup required ignores phase", M,
     "        return self.phase == 2 and not self._phase_init",
     "        return not self._phase_init"),
    ("MG19b arena setup required inverted", M,
     "        return not self._arena_init",
     "        return self._arena_init"),
    ("MG20 entity reset keeps arena_init", M,
     "                self._arena_init = False  # Make sure the arena is reset on the next reset call\n",
     ""),
    ("MG20b entity reset never fails", M,
     '                raise ResetError("Player or boss pose could not be reset")',
     "                break"),
    ("MG22 camera reset never fails", M,
     '                raise LockOnFailure("Lock on to Margit could not be established")',
     "                break"),
    ("MG23 fog gate ignores death", M,
     '        if self.game.player_hp == 0:\n            raise ResetError("Player has died during reset")',
     '        if False:\n            raise ResetError("Player has died during reset")'),
    ("MG24 fog gate accepts any pose", M,
     '        if np.linalg.norm(self.game.player_pose[:3] - coords["post_fog_wall"][:3]) > 2.0:',
     '        if np.linalg.norm(self.game.player_pose[:3] - coords["post_fog_wall"][:3]) > 2000.0:'),
    ("MG25 fog gate does not wait for idle", M,
     "        while not self.game.player_animation == self.PLAYER_IDLE_ANIMATION:",
     "        while False:"),
    ("MG26 reset does not pause", M,
     "        self._camera_reset()\n        self.game.pause()\n        self.terminated = False",
     "        self._camera_reset()\n        self.terminated = False"),
    ("MG27 reset does not focus window", M,
     "        self._game_window.focus()\n        if self._reload_required():",
     "        if self._reload_required():"),
    ("MG28 reset keeps terminated", M,
     "        self.game.pause()\n        self.terminated = False\n",
     "        self.game.pause()\n"),
    ("MG29 reset skips phase setup", M,
     "        if self._phase_setup_required():\n            self._phase_setup()\n",
     ""),
    ("MG30 reset never reloads", M,
     "        if self._reload_required():\n            self._reload()\n",
     "        if self._reload_required():\n            pass\n"),
    ("MG30b reset skips arena setup", M,
     "        if self._arena_setup_required():\n            self._arena_setup()\n",
     ""),
    ("MG30c reset skips entity reset", M,
     "        self._entity_reset()\n        self._camera_reset()",
     "        self._camera_reset()"),
    ("MG30d reset skips camera reset", M,
     "        self._entity_reset()\n        self._camera_reset()",
     "        self._entity_reset()"),
    ("MG31 reset keeps input", M,
     "        self._game_input.reset()\n        self._game_window.focus()",
     "        self._game_window.focus()"),
    ("MG33 close does not resume", M,
     "        self.game.resume()\n        self._game_input.reset()\n        self.game.player_hp = 0",
     "        self._game_input.reset()\n        self.game.player_hp = 0"),
    ("MG34 close does not reset input", M,
     "        self.game.resume()\n        self._game_input.reset()\n        self.game.player_hp = 0",
     "        self.game.resume()\n        self.game.player_hp = 0"),
    ("MG35 close does not kill the player", M,
     "        self.game.player_hp = 0  # Kill player to force game reload. Don't wait for completion",
     "        pass"),
    ("MG36 close reloads", M,
     "        self.game.player_hp = 0  # Kill player to force game reload. Don't wait for completion",
     "        self.game.player_hp = 0\n        self.game.reload()"),
    ("MG37 close touches a debug flag", M,
     "        self.game.player_hp = 0  # Kill player to force game reload. Don't wait for completion",
     "        self.game.allow_deaths = True\n        self.game.player_hp = 0"),
    ("MG37b close waits", M,
     "        self.game.player_hp = 0  # Kill player to force game reload. Don't wait for completion",
     "        self.game.player_hp = 0\n        self.game.sleep(0.1)"),
    ("MG38 props: extra write", M,
     "        self.game.player_stats = self.game.data.player_stats[self.ENV_ID]\n        self.game.resume()",
     "        self.game.player_stats = self.game.data.player_stats[self.ENV_ID]\n        self.game.allow_hits = True\n        self.game.resume()"),
    ("MG38b props: no bonfire", M,
     "        self.game.last_bonfire = self.BONFIRE\n",
     ""),
    ("MG38c props: no resume", M,
     "        self.game.player_stats = self.game.data.player_stats[self.ENV_ID]\n        self.game.resume()",
     "        self.game.player_stats = self.game.data.player_stats[self.ENV_ID]"),
    ("MG39 step hook keeps mp", M,
     "        super()._step_hook()\n        self.game.reset_player_mp()",
     "        super()._step_hook()"),
    ("MG40 reward terminal bonus sign", M,
     "            base_reward = 0.1 if next_game_state.boss_hp == 0 else -0.1",
     "            base_reward = -0.1 if next_game_state.boss_hp == 0 else 0.1"),
    ("MG41 reward terminal and", M,
     "        if next_game_state.boss_hp == 0 or next_game_state.player_hp == 0:",
     "        if next_game_state.boss_hp == 0 and next_game_state.player_hp == 0:"),
    ("MG42 reward boss norm", M,
     "        boss_reward = (game_state.boss_hp - next_game_state.boss_hp) / game_state.boss_max_hp",
     "        boss_reward = (game_state.boss_hp - next_game_state.boss_hp) / game_state.player_max_hp"),
    ("MG43 reward player norm", M,
     "        player_reward = player_hp_diff / game_state.player_max_hp",
     "        player_reward = player_hp_diff / game_state.boss_max_hp"),
    ("MG44 reward pose shaping", M,
     "        return boss_reward + player_reward + base_reward",
     "        return boss_reward + player_reward + base_reward + 0.001 * float(np.linalg.norm(next_game_state.player_pose[:3]))"),
    ("MG44b reward boss death only 0.05", M,
     "            base_reward = 0.1 if next_game_state.boss_hp == 0 else -0.1",
     "            base_reward = 0.05 if next_game_state.boss_hp == 0 else -0.1"),
    ("MG44c reward player death only -0.05", M,
     "            base_reward = 0.1 if next_game_state.boss_hp == 0 else -0.1",
     "            base_reward = 0.1 if next_game_state.boss_hp == 0 else -0.05"),
    ("MG45 obs unknown boss animation 0", M,
     '        obs["boss_animation"] = _boss_animations.get(obs["boss_animation"], {"ID": -1})["ID"]',
     '        obs["boss_animation"] = _boss_animations.get(obs["boss_animation"], {"ID": 0})["ID"]'),
    ("MG46 obs unknown player animation 0", M,
     '        obs["player_animation"] = _player_animations.get(obs["player_animation"], {"ID": -1})["ID"]',
     '        obs["player_animation"] = _player_animations.get(obs["player_animation"], {"ID": 0})["ID"]'),
    ("MG47 phase 3 allowed", M,
     "        assert phase in (1, 2)", "        assert phase in (1, 2, 3)"),
    ("MG48 boss animation space start 0", M,
     '"boss_animation": spaces.Discrete(len(boss_animations) + 1, start=-1),',
     '"boss_animation": spaces.Discrete(len(boss_animations) + 1, start=0),'),
    ("MG49 boss animation space +1", M,
     '"boss_animation": spaces.Discrete(len(boss_animations) + 1, start=-1),',
     '"boss_animation": spaces.Discrete(len(boss_animations) + 2, start=-1),'),
    ("MG50 player animation space +1", M,
     '"player_animation": spaces.Discrete(len(player_animations) + 1, start=-1),',
     '"player_animation": spaces.Discrete(len(player_animations) + 2, start=-1),'),
    ("MG51 action space +1", M,
     "        self.action_space = spaces.Discrete(len(self.game.data.actions))",
     "        self.action_space = spaces.Discrete(len(self.game.data.actions) + 1)"),
    ("MG52 action mask dtype int", M,
     "        action_mask = np.zeros(self.action_space.n, dtype=bool)",
     "        action_mask = np.zeros(self.action_space.n, dtype=int)"),
    ("MG53 state phase fixed", M,
     "            phase=self.phase,\n", "            phase=1,\n"),
    ("MG54 boss animation fixed", M,
     "        game_state.boss_animation = self.game.margit_animation",
     '        game_state.boss_animation = "Idle"'),
    ("MG55 obs space lock_on", M,
     '"lock_on": spaces.Discrete(2),', '"lock_on": spaces.Discrete(3),'),
    ("MG56 obs space phase 1 only", M,
     '"phase": spaces.Discrete(2, start=1),', '"phase": spaces.Discrete(1, start=1),'),
    ("MG57 obs boss_hp as is", M,
     '        obs["boss_hp"] = np.array([obs["boss_hp"]], dtype=np.float32)',
     '        obs["boss_hp"] = np.array([obs["boss_hp"] + 1], dtype=np.float32)'),
    ("MG58 entity reset skips boss hp", M,
     '        self.game.reset_boss_hp("margit")\n', ""),
    ("MG58b entity reset skips player sp", M,
     "        self.game.reset_player_sp()\n", ""),
    # --- soulsenv.py
    ("SE01 step after termination allowed", S,
     '        if self.terminated:\n            logger.error("Environment step called after environment was terminated")',
     '        if False:\n            logger.error("Environment step called after environment was terminated")'),
    ("SE02 no player death error", S,
     '        if game_state.player_hp == 0:\n            logger.error("_step_check: Player HP is 0")',
     '        if False:\n            logger.error("_step_check: Player HP is 0")'),
    ("SE03 all actions valid", S,
     "        if action in self.current_valid_actions():\n            self._game_input.add_actions",
     "        if True:\n            self._game_input.add_actions"),
    ("SE04 roll needs no stamina", S,
     "roll_ids = list(range(8, 16)) if player_sp > 0 and",
     "roll_ids = list(range(8, 16)) if player_sp >= 0 and"),
    ("SE04b attack needs no stamina", S,
     "attack_ids = [16, 17, 18] if player_sp > 0 and",
     "attack_ids = [16, 17, 18] if player_sp >= 0 and"),
    ("SE04c movement drops action 7", S,
     "movement_ids = list(range(8)) if current_duration >= durations[2] else []",
     "movement_ids = list(range(7)) if current_duration >= durations[2] else []"),
    ("SE04d no-op removed", S,
     "        return movement_ids + roll_ids + attack_ids + [19]",
     "        return movement_ids + roll_ids + attack_ids"),
    ("SE05 step ignores game speed", S,
     "        self.game.game_speed = self._game_speed\n        t_start = self.game.time",
     "        self.game.game_speed = 1.0\n        t_start = self.game.time"),
    ("SE06 step does not pause", S,
     "        self.game.pause()\n        t_end = self.game.time",
     "        t_end = self.game.time"),
    ("SE07 terminated needs both", S,
     "        self.terminated = self._game_state.player_hp == 0 or self._game_state.boss_hp == 0\n\n    def _handle_critical_game_state",
     "        self.terminated = self._game_state.player_hp == 0 and self._game_state.boss_hp == 0\n\n    def _handle_critical_game_state"),
    ("SE08 player hp not clamped", S,
     "        self._game_state.boss_hp -= game_state.boss_max_hp - boss_hp\n        if self._game_state.player_hp < 0:",
     "        self._game_state.boss_hp -= game_state.boss_max_hp - boss_hp\n        if False:"),
    ("SE08b boss hp not clamped", S,
     "        if self._game_state.boss_hp < 0:\n            self._game_state.boss_hp = 0\n        self.terminated = self._game_state.player_hp == 0 or self._game_state.boss_hp == 0\n\n    def _handle_critical_game_state",
     "        if False:\n            self._game_state.boss_hp = 0\n        self.terminated = self._game_state.player_hp == 0 or self._game_state.boss_hp == 0\n\n    def _handle_critical_game_state"),
    ("SE09 truncated always", S,
     "        return self.obs, reward, self.terminated, False, self.info",
     "        return self.obs, reward, self.terminated, True, self.info"),
    ("SE09b terminated never", S,
     "        return self.obs, reward, self.terminated, False, self.info",
     "        return self.obs, reward, False, False, self.info"),
    ("SE09c reward negated", S,
     "        return self.obs, reward, self.terminated, False, self.info",
     "        return self.obs, -reward, self.terminated, False, self.info"),
    ("SE10 no unknown boss animation warning", S,
     '            logger.warning(f"_step: Unknown boss animation {game_state.boss_animation}")',
     "            pass"),
    ("SE11 no unknown player animation warning", S,
     '            logger.warning(f"_step: Unknown player animation {game_state.player_animation}")',
     "            pass"),
    ("SE12 game_factory drops resolution", S,
     "        self.game = game_factory(self.game_id, game_resolution=game_resolution)",
     "        self.game = game_factory(self.game_id)"),
    ("SE13 window drops resolution", S,
     "        self._game_window = GameWindow(self.game_id, game_resolution=game_resolution)",
     "        self._game_window = GameWindow(self.game_id)"),
    ("SE14 no step hook", S,
     "        self._update_game_state(game_state, player_animation_td, boss_animation_td)\n        self._step_hook()",
     "        self._update_game_state(game_state, player_animation_td, boss_animation_td)"),
    ("SE15 step hook keeps boss hp", S,
     "        self.game.reset_player_hp()\n        self.game.reset_boss_hp(self.ENV_ID)\n\n    def _step_check",
     "        self.game.reset_player_hp()\n\n    def _step_check"),
    ("SE15b step hook keeps player hp", S,
     "        self.game.reset_player_hp()\n        self.game.reset_boss_hp(self.ENV_ID)\n\n    def _step_check",
     "        self.game.reset_boss_hp(self.ENV_ID)\n\n    def _step_check"),
    ("SE16 hp accounting sign", S,
     "        self._game_state.player_hp -= game_state.player_max_hp - player_hp",
     "        self._game_state.player_hp += game_state.player_max_hp - player_hp"),
    ("SE16b boss hp accounting sign", S,
     "        self._game_state.boss_hp -= game_state.boss_max_hp - boss_hp\n        if self._game_state.player_hp < 0:",
     "        self._game_state.boss_hp += game_state.boss_max_hp - boss_hp\n        if self._game_state.player_hp < 0:"),
    ("SE17 input never updated", S,
     "        # If no action was queued, the update is equivalent to a reset.\n        self._game_input.update_input()",
     "        # If no action was queued, the update is equivalent to a reset."),
    # --- games
    ("EG01 unknown name format", G,
     '.get(animation_id, f"Unknown_{animation_id}")', '.get(animation_id, f"Unknown{animation_id}")'),
    ("EG02 names skip misc", G,
     '                for section in ("attacks", "movement", "misc")\n                for name, animation_id in animations[section].items()',
     '                for section in ("attacks", "movement")\n                for name, animation_id in animations[section].items()'),
    ("EG03 animation reads wrong record", G,
     '        animation_id = self.mem.read_record(self.data.addresses["MargitAnimation"])',
     '        animation_id = self.mem.read_record(self.data.addresses["MargitHP"])'),
    ("EG04 reset boss hp to zero", G,
     '        setattr(self, boss_id + "_hp", getattr(self, boss_id + "_max_hp"))',
     '        setattr(self, boss_id + "_hp", 0)'),
    ("EG05 gravity setter inverted", G,
     "        self.mem.write_bit(address, index=0, value=0 if flag else 1)",
     "        self.mem.write_bit(address, index=0, value=1 if flag else 0)"),
    ("EG06 gravity getter inverted", G,
     "        return buff & 1 == 0  # Gravity disabled flag",
     "        return buff & 1 == 1  # Gravity disabled flag"),
    ("EG07 reset player hp no-op", G,
     "        self.player_hp = self.player_max_hp\n", "        pass\n"),
    ("EG08 reset player mp no-op", G,
     "        self.player_mp = self.player_max_mp\n", "        pass\n"),
    ("EG09 timed overflow", G,
     "        return (tend - tstart) / 1000 if tend >= tstart else tend / 1000",
     "        return (tend - tstart) / 1000 if tend >= tstart else -1"),
    # --- registration / factory / data
    ("EG05b gravity setter inverted", G,
     '        address = self.mem.resolve_record(self.data.addresses["PlayerGravity"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)',
     '        address = self.mem.resolve_record(self.data.addresses["PlayerGravity"])\n        self.mem.write_bit(address, index=0, value=1 if flag else 0)'),
    ("EG05c death setter inverted", G,
     '        address = self.mem.resolve_record(self.data.addresses["AllowPlayerDeath"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)',
     '        address = self.mem.resolve_record(self.data.addresses["AllowPlayerDeath"])\n        self.mem.write_bit(address, index=0, value=1 if flag else 0)'),
    ("EG05d gravity setter wrong bit", G,
     '        address = self.mem.resolve_record(self.data.addresses["PlayerGravity"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)',
     '        address = self.mem.resolve_record(self.data.addresses["PlayerGravity"])\n        self.mem.write_bit(address, index=1, value=0 if flag else 1)'),
    ("EG05e gravity setter wrong record", G,
     '        address = self.mem.resolve_record(self.data.addresses["PlayerGravity"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)',
     '        address = self.mem.resolve_record(self.data.addresses["AllowPlayerDeath"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)'),
    ("EG05f death setter does not resolve", G,
     '        address = self.mem.resolve_record(self.data.addresses["AllowPlayerDeath"])\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)',
     '        address = 0\n        self.mem.write_bit(address, index=0, value=0 if flag else 1)'),
    ("GM01 chain adds the first offset", "soulsgym/core/game_memory.py",
     '        address += record["offsets"][-1]\n', '        address += record["offsets"][0]\n'),
    ("GM02 chain skips the first dereference", "soulsgym/core/game_memory.py",
     '        address = self._read_ptr(self.bases[record["base"]])\n',
     '        address = self.bases[record["base"]]\n'),
    ("GM03 chain skips the last offset", "soulsgym/core/game_memory.py",
     '        address += record["offsets"][-1]\n', '        address += 0\n'),
    ("GM04 chain drops an intermediate offset", "soulsgym/core/game_memory.py",
     '        for offset in record["offsets"][:-1]:\n            address = self._read_ptr(address + offset)',
     '        for offset in record["offsets"][1:-1]:\n            address = self._read_ptr(address + offset)'),
    ("GM05 pointer endianness", "soulsgym/core/game_memory.py",
     '        return int.from_bytes(self._backend.read_bytes(address, 8), "little")',
     '        return int.from_bytes(self._backend.read_bytes(address, 8), "big")'),
    ("GM06 write_bit keeps other bits wrong", "soulsgym/core/game_memory.py",
     "        byte = (byte[0] & ~mask[0]).to_bytes(1, \"little\")",
     "        byte = (byte[0] & 0).to_bytes(1, \"little\")"),
    ("GM07 cache ignores the record", "soulsgym/core/game_memory.py",
     "        unique_address_id = str((record[\"offsets\"], record[\"base\"]))",
     "        unique_address_id = str(record[\"base\"])"),
    ("GF01 factory drops resolution", "soulsgym/games/__init__.py",
     "            return EldenRing(game_resolution=game_resolution)", "            return EldenRing()"),
    ("RG01 time limit 3001", "soulsgym/__init__.py",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         max_episode_steps=3000,",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         max_episode_steps=3001,"),
    ("RG02 not nondeterministic", "soulsgym/__init__.py",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         max_episode_steps=3000,\n         nondeterministic=True)",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         max_episode_steps=3000)"),
    ("RG03 no time limit", "soulsgym/__init__.py",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         max_episode_steps=3000,\n         nondeterministic=True)",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv',\n         nondeterministic=True)"),
    ("RG04 wrong entry point", "soulsgym/__init__.py",
     "entry_point='soulsgym.envs.eldenring.margit:MargitEnv'", "entry_point='soulsgym.envs.eldenring.margit:MargitState'"),
    ("YD01 duplicate animation id", "soulsgym/core/data/eldenring/animations.yaml",
     "      Attack3000: 2003000", "      Attack3000: 2003001"),
    ("YD02 idle id changed", "soulsgym/core/data/eldenring/animations.yaml",
     "      Idle: 2000020", "      Idle: 2000021"),
    ("YD03 phase 1 animation missing", "soulsgym/core/data/eldenring/animations.yaml",
     "      Hit41002: 41002\n", ""),
    ("YD04 duplicate name across sections", "soulsgym/core/data/eldenring/animations.yaml",
     "      Hit41002: 41002\n", "      Hit41002: 41002\n      Idle: 41003\n"),
    # --- guards on the live tests (test files) and on the ini files
    ("TM01 live test loses integration mark", "tests/eldenring/test_game.py",
     "@pytest.mark.integration\n# Evaluated lazily", "# Evaluated lazily"),
    ("TM02 game interface test loses destructive mark", "tests/eldenring/test_game.py",
     "@pytest.mark.manual_destructive\n@pytest.mark.skipif(\"game_not_open()\", reason=\"Elden Ring is not running.\")\n@pytest.mark.parametrize(\n    \"attr_name, attr_info\", interface_attributes",
     "@pytest.mark.skipif(\"game_not_open()\", reason=\"Elden Ring is not running.\")\n@pytest.mark.parametrize(\n    \"attr_name, attr_info\", interface_attributes"),
    ("TM03 live test with eager skip condition", "tests/eldenring/test_game.py",
     '@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\n@pytest.mark.parametrize(\n    "attr_name, attr_info", memory_attributes.items(), ids=list(memory_attributes)\n)\ndef test_read_only_game_attributes(',
     '@pytest.mark.skipif(False, reason="Elden Ring is not running.")\n@pytest.mark.parametrize(\n    "attr_name, attr_info", memory_attributes.items(), ids=list(memory_attributes)\n)\ndef test_read_only_game_attributes('),
    ("TM04 live test without skip condition", "tests/eldenring/test_envs.py",
     '@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\ndef test_margit_reset_only_profile(',
     "def test_margit_reset_only_profile("),
    ("TM05 live env test loses destructive mark", "tests/eldenring/test_envs.py",
     '@pytest.mark.manual_destructive\n@pytest.mark.integration\n@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\ndef test_margit_one_step_profile(',
     '@pytest.mark.integration\n@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\ndef test_margit_one_step_profile('),
    ("TM06 root ini runs live tests by default", "pytest.ini",
     'addopts = -m "not integration and not manual_destructive"', 'addopts = -m "not manual_destructive"'),
    ("TM07 tests ini runs live tests by default", "tests/pytest.ini",
     'addopts = -m "not integration and not manual_destructive"', 'addopts = -m "not integration"'),
    ("TM08 root ini drops the destructive marker", "pytest.ini",
     "    manual_destructive: marks tests that can reset, move, or otherwise manipulate a live game.\n", ""),
    ("TM09 live env test uses game without integration mark", "tests/eldenring/test_envs.py",
     '@pytest.mark.manual_destructive\n@pytest.mark.integration\n@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\ndef test_margit_env_creation_integration(',
     '@pytest.mark.manual_destructive\n@pytest.mark.skipif("game_not_open()", reason="Elden Ring is not running.")\ndef test_margit_env_creation_integration('),
]


def apply(tree: str, rel: str, old: str, new: str) -> str | None:
    """Apply a mutant to a scratch tree and return the original text, or ``None`` on failure."""
    path = MUT / tree / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        return f"n/a (found {count}x)"
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")
    return None


# The ini mutants change the default selection. Only run the guard tests for them, because the
# mutated selection would otherwise include live tests.
RESTRICT = {
    "TM06": {
        "old": ["tests/eldenring/test_live_markers.py"],
        "new": ["tests/eldenring/test_envs.py::test_default_selection_excludes_the_live_tests"],
    },
    "TM07": {
        "old": ["tests/eldenring/test_live_markers.py"],
        "new": ["tests/eldenring/test_envs.py::test_default_selection_excludes_the_live_tests"],
    },
}


def restore(tree: str, rel: str, original: str):
    """Restore a mutated file in a scratch tree."""
    (MUT / tree / rel).write_text(original, encoding="utf-8", newline="")


def run_mutant(mutant: tuple[str, str, str, str]) -> dict:
    """Run both suites against one mutant and record which suite kills it."""
    mid, rel, old, new = mutant
    result = {"id": mid}
    restrict = RESTRICT.get(mid.split()[0], {})
    originals = {}
    skip = {}
    for tree in ("old", "new"):
        path = MUT / tree / rel
        originals[tree] = path.read_text(encoding="utf-8") if path.exists() else None
        if originals[tree] is None:
            skip[tree] = "n/a (missing file)"
            continue
        note = apply(tree, rel, old, new)
        if note:
            skip[tree] = note
    try:
        with ThreadPoolExecutor(2) as pool:
            futures = {
                tree: pool.submit(run_suite, tree, restrict.get(tree))
                for tree in ("old", "new")
                if tree not in skip
            }
            for tree, fut in futures.items():
                result[tree] = fut.result()
    finally:
        for tree in ("old", "new"):
            if originals[tree] is not None:
                restore(tree, rel, originals[tree])
    for tree, note in skip.items():
        result[tree] = (None, note)
    return result


def fmt(r: dict) -> str:
    """Format a mutant result for printing."""

    def cell(x: tuple[bool | None, str]) -> str:
        killed, first = x
        if killed is None:
            return first
        return ("KILLED " if killed else "SURVIVED ") + first.replace("FAILED ", "")[:110]

    return f"{r['id']}\n   old: {cell(r['old'])}\n   new: {cell(r['new'])}"


def main():
    """Dispatch the command-line subcommand."""
    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
        return
    if cmd == "sync":
        sync_new_tests()
        return
    if cmd == "sanity":
        for tree in ("old", "new"):
            print(tree, run_suite(tree, ["-q"]))
        return
    wanted = sys.argv[2:]
    mutants = [m for m in MUTANTS if not wanted or any(m[0].startswith(w) for w in wanted)]
    results = []
    t0 = time.time()
    out_path = HERE / "mut_results.jsonl"
    with open(out_path, "a", encoding="utf-8") as out:
        for m in mutants:
            r = run_mutant(m)
            results.append(r)
            out.write(json.dumps(r) + "\n")
            out.flush()
            print(fmt(r), flush=True)
    gaps = [r for r in results if r["old"][0] and r["new"][0] is False]
    better = [r for r in results if r["new"][0] and r["old"][0] is False]
    print(f"\n{len(results)} mutants in {time.time() - t0:.0f}s")
    print("GAPS (old kills, new survives):", [r["id"] for r in gaps])
    print("NEW BETTER (new kills, old survives):", [r["id"] for r in better])
    both_survive = [r["id"] for r in results if r["old"][0] is False and r["new"][0] is False]
    print("SURVIVE BOTH:", both_survive)


if __name__ == "__main__":
    main()
