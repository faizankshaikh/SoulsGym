"""M1 go/no-go: validate the Rust speedhack pause/resume and speed control on Elden Ring.

Bounded live scenario (PLAN.md M1.1). Game-process writes are limited to speedhack DLL
injection and game-speed values (0.0 / 0.5 / 2.0 / 1.0). No reset, step, teleport, flag,
input, or reload writes. Not part of the shipped PR; run untracked from the repo root:

    conda run -n soulsgym --no-capture-output python m1_gonogo.py

Preconditions: Elden Ring running EAC-free in offline mode, player loaded into the game
in a safe spot, game window at 800x450. The user watches the game window throughout and
confirms stability afterwards.
"""

import sys
import time
import traceback

PHASE_SLEEP = 4.0


def log(msg: str):
    """Print a prefixed progress message."""
    print(f"[m1-gonogo] {msg}", flush=True)


def main() -> int:
    """Run the go/no-go checks and return the process exit code."""
    from soulsgym.games import EldenRing

    log("Constructing EldenRing() (injects speedhack DLL, sets speed 1.0) ...")
    game = EldenRing()
    log("Game interface constructed.")

    log("--- Read-only checks ---")
    log(f"is_ingame        = {game.is_ingame}")
    log(f"player_hp        = {game.player_hp} / {game.player_max_hp}")
    log(f"player_pose      = {game.player_pose}")
    log(f"player_animation = {game.player_animation}")
    img = game.img
    log(f"img shape        = {getattr(img, 'shape', None)}")

    log("--- Pause test: game speed -> 0 for %.0fs. WATCH THE GAME FREEZE ---" % PHASE_SLEEP)
    game.pause()
    t0 = time.time()
    pose_a = game.player_pose
    anim_a = game.player_animation
    time.sleep(PHASE_SLEEP)
    pose_b = game.player_pose
    anim_b = game.player_animation
    frozen = (pose_a == pose_b).all() if hasattr(pose_a, "all") else pose_a == pose_b
    log(f"pose frozen={frozen}  anim: {anim_a} -> {anim_b}  ({time.time() - t0:.1f}s paused)")

    log("--- Resume: game speed -> 1 ---")
    game.resume()
    time.sleep(2.0)
    log(f"player_animation after resume = {game.player_animation}")

    log("--- Speed sweep: 2.0 then 0.5 then 1.0. WATCH THE GAME SPEED CHANGE ---")
    game.game_speed = 2.0
    time.sleep(PHASE_SLEEP)
    game.game_speed = 0.5
    time.sleep(PHASE_SLEEP)
    game.game_speed = 1.0
    log("Speed restored to 1.0.")

    log("--- Second pause/resume cycle (stability) ---")
    game.pause()
    time.sleep(2.0)
    game.resume()
    log("Done. Confirm in chat: did the game stay stable and controllable?")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception:
        traceback.print_exc()
        try:
            # Best effort: leave the game running at normal speed.
            from soulsgym.games import EldenRing

            game = EldenRing()
            game.game_speed = 1.0
            print("[m1-gonogo] Recovery: game speed reset to 1.0.", flush=True)
        except Exception:
            print("[m1-gonogo] Recovery failed; check game speed manually.", flush=True)
        rc = 1
    sys.exit(rc)
