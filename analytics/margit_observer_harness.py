"""User-assisted operational checks for the Margit environment.

This module intentionally contains no pytest tests. It preserves the manual observation and
calibration workflows without mixing them with automated or destructive environment tests.

The workflows use the Elden Ring game interface directly. They only read the game state and never
call ``reset`` or ``step`` of the environment, or write game flags.

Note:
    This is a development tool for live sessions. It is excluded from the upstream pull request.
"""

import argparse
import csv
import datetime
import json
import time
from pathlib import Path

from soulsgym.envs.eldenring.margit import MargitEnv
from soulsgym.exception import GameStateError
from soulsgym.games.eldenring import EldenRing

OBSERVER_DIR = Path("logs") / "observer"
CALIBRATION_DIR = Path("logs") / "calibration"


def _connect(game_resolution: tuple[int, int]) -> EldenRing:
    """Attach to the running game and check that the player is loaded."""
    game = EldenRing(game_resolution=game_resolution)
    if not game.is_ingame:
        raise GameStateError("Player is not loaded into the game")
    return game


def _read_sample(game: EldenRing) -> dict:
    """Read the observed game properties as JSON-compatible values."""
    boss_hp, boss_max_hp = game.margit_hp, game.margit_max_hp
    return {
        # The phase is approximated by the HP threshold, as in the environment
        "phase": 2 if boss_hp <= boss_max_hp * MargitEnv.PHASE2_HP_THRESHOLD_RATIO else 1,
        "player_hp": int(game.player_hp),
        "player_max_hp": int(game.player_max_hp),
        "player_sp": int(game.player_sp),
        "player_max_sp": int(game.player_max_sp),
        "boss_hp": int(boss_hp),
        "boss_max_hp": int(boss_max_hp),
        "player_pose": [round(float(value), 4) for value in game.player_pose],
        "boss_pose": [round(float(value), 4) for value in game.margit_pose],
        "camera_pose": [round(float(value), 4) for value in game.camera_pose],
        "player_animation": str(game.player_animation),
        "player_animation_duration": 0.0,  # The game interface has no player animation time
        "boss_animation": game.margit_animation,
        "boss_animation_duration": round(float(game.margit_animation_time), 4),
        "boss_animation_raw": str(game.mem.read_record(game.data.addresses["MargitAnimation"])),
        "lock_on": bool(game.lock_on),
    }


def _timestamped_path(directory: Path, prefix: str, suffix: str) -> Path:
    """Create a timestamped artifact path without overwriting prior captures."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return directory / f"{prefix}_{stamp}{suffix}"


def observe(
    steps: int, interval: float, stop_on_player_death: bool, game_resolution: tuple[int, int]
):
    """Record a user-controlled Margit fight without calling reset or step.

    The user must enter the arena, unpause AI, and retain control of the player.
    This command only reads the current game state at the requested interval; it
    never calls ``env.reset()``, ``env.step()``, pause, resume, or game-flag writes.
    """
    print("Margit observation: captures state only; user controls the fight.")
    print("Expected setup: inside Margit arena, AI unpaused, menu closed.")
    game = _connect(game_resolution)

    player_animation_changes = 0
    boss_animation_changes = 0
    previous_player_animation = None
    previous_boss_animation = None
    unknown_boss_frames = 0
    unreadable_frames = 0
    raw_boss_animation_ids = set()
    status = "completed"
    start = datetime.datetime.now()
    records = []

    try:
        for step in range(1, steps + 1):
            # Re-resolve pointer chains every sample: death/respawn reloads invalidate
            # cached ChrIns pointers and stale reads return garbage.
            game.clear_cache()
            try:
                sample = _read_sample(game)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # During death/respawn loading screens the chains are unreadable.
                # Skip the sample and keep observing; pointers recover after reload.
                unreadable_frames += 1
                if unreadable_frames % 25 == 1:
                    print(f"observer_notice=state_unreadable step={step} detail={exc}")
                time.sleep(interval)
                continue
            player_animation = sample["player_animation"]
            boss_animation = (sample["boss_animation"], sample["boss_animation_raw"])
            player_changed = player_animation != previous_player_animation
            boss_changed = boss_animation != previous_boss_animation
            if previous_player_animation is not None and player_changed:
                player_animation_changes += 1
            if previous_boss_animation is not None and boss_changed:
                boss_animation_changes += 1
            previous_player_animation = player_animation
            previous_boss_animation = boss_animation
            if sample["boss_animation"].startswith("Unknown"):
                unknown_boss_frames += 1
            raw_boss_animation_ids.add(sample["boss_animation_raw"])

            if step % 10 == 0:
                print(
                    f"step={step}/{steps} player_hp={sample['player_hp']} "
                    f"boss_hp={sample['boss_hp']}"
                )
            records.append(
                {
                    "step": step,
                    "t_sec": round((datetime.datetime.now() - start).total_seconds(), 3),
                    **sample,
                }
            )
            if stop_on_player_death and sample["player_hp"] <= 0:
                status = "player_death_stop"
                print(f"observer_notice=player_hp_zero step={step}")
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        status = "interrupted_by_user"
        print("observer_notice=keyboard_interrupt")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        status = "runtime_error"
        print(f"observer_notice=runtime_error detail={exc}")
    finally:
        runtime = str(datetime.datetime.now() - start).split(".")[0]
        summary = {
            "status": status,
            "runtime": runtime,
            "player_animation_changes": player_animation_changes,
            "boss_animation_changes": boss_animation_changes,
            "unknown_boss_frames": unknown_boss_frames,
            "unreadable_frames": unreadable_frames,
            "unique_raw_boss_animation_ids": len(raw_boss_animation_ids),
            "steps_requested": steps,
            "steps_captured": len(records),
            "interval": interval,
            "stop_on_player_death": stop_on_player_death,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        csv_path = _timestamped_path(OBSERVER_DIR, "ai_unpaused_observe", ".csv")
        json_path = csv_path.with_suffix(".json")
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "step",
                    "t_sec",
                    "player_hp",
                    "boss_hp",
                    "player_animation",
                    "boss_animation",
                    "boss_animation_raw",
                    "lock_on",
                ],
            )
            writer.writeheader()
            writer.writerows({key: record[key] for key in writer.fieldnames} for record in records)
        json_path.write_text(
            json.dumps({"summary": summary, "records": records}, indent=2), encoding="utf-8"
        )
        print(
            f"observer_summary status={status} runtime={runtime} "
            f"player_animation_changes={player_animation_changes} "
            f"boss_animation_changes={boss_animation_changes} "
            f"unknown_boss_frames={unknown_boss_frames} "
            f"unique_raw_boss_animation_ids={len(raw_boss_animation_ids)}"
        )
        print(f"observer_end_status={status}")
        print(f"observer_artifact_csv={csv_path.as_posix()}")
        print(f"observer_artifact_json={json_path.as_posix()}")


def _to_int(value: object) -> int | None:
    """Return an integer value, or ``None`` for missing data."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def summarize(observer_json: Path | None):
    """Print a compact summary for a Margit observation JSON artifact."""
    if observer_json is None:
        files = sorted(OBSERVER_DIR.glob("ai_unpaused_observe_*.json"))
        if not files:
            raise FileNotFoundError(
                "No observer JSON artifact found. Pass --observer-json explicitly."
            )
        observer_json = files[-1]

    payload = json.loads(observer_json.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    records = payload.get("records", [])
    if not records:
        print(f"observer_summary_file={observer_json.as_posix()}")
        print("observer_summary_error=no_records")
        return

    player_hp = [_to_int(record.get("player_hp")) for record in records]
    boss_hp = [_to_int(record.get("boss_hp")) for record in records]
    player_sp = [_to_int(record.get("player_sp")) for record in records]
    player_hp = [value for value in player_hp if value is not None]
    boss_hp = [value for value in boss_hp if value is not None]
    player_sp = [value for value in player_sp if value is not None]
    death_step = next(
        (record.get("step") for record in records if (_to_int(record.get("player_hp")) or 0) <= 0),
        None,
    )
    phases = [record.get("phase") for record in records if record.get("phase") is not None]
    raw_ids = {
        str(record["boss_animation_raw"])
        for record in records
        if record.get("boss_animation_raw") not in (None, "None", "")
    }
    unknown_frames = sum(
        record.get("boss_animation", "").startswith("Unknown") for record in records
    )
    boss_damage = boss_hp[0] - boss_hp[-1] if boss_hp else None
    phase_transitions = sum(first != second for first, second in zip(phases, phases[1:]))

    print(f"observer_summary_file={observer_json.as_posix()}")
    print(
        "observer_gate_report "
        f"status={summary.get('status', 'unknown')} runtime={summary.get('runtime', 'unknown')} "
        f"steps_captured={summary.get('steps_captured', len(records))} "
        f"death_step={death_step} player_hp_start={player_hp[0] if player_hp else None} "
        f"player_hp_end={player_hp[-1] if player_hp else None} "
        f"player_sp_min={min(player_sp) if player_sp else None} "
        f"boss_hp_start={boss_hp[0] if boss_hp else None} boss_hp_end={boss_hp[-1] if boss_hp else None} "
        f"boss_damage={boss_damage} phase_start={phases[0] if phases else None} "
        f"phase_end={phases[-1] if phases else None} phase_transitions={phase_transitions} "
        f"unknown_boss_frames={unknown_frames} unique_raw_boss_animation_ids={len(raw_ids)}"
    )


def capture_calibration(capture_key: str, game_resolution: tuple[int, int]):
    """Capture a labeled Margit coordinate sample without resetting the environment."""
    valid_keys = {
        "bonfire",
        "fog_wall",
        "post_fog_wall",
        "center",
        "player_init_pose",
        "boss_init_pose",
    }
    if capture_key not in valid_keys:
        raise ValueError(f"Unsupported capture key: {capture_key}")

    game = _connect(game_resolution)
    player_pose = [float(value) for value in game.player_pose]
    boss_pose = [float(value) for value in game.margit_pose]
    selected_pose = boss_pose if capture_key == "boss_init_pose" else player_pose
    payload = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "capture_key": capture_key,
        "player_pose": player_pose,
        "boss_pose": boss_pose,
        "suggested_coordinates_patch": {"margit": {capture_key: selected_pose}},
    }
    json_path = _timestamped_path(CALIBRATION_DIR, f"margit_calibration_{capture_key}", ".json")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"calibration_capture_key={capture_key}")
    print(f"calibration_artifact_json={json_path.as_posix()}")


def _parse_resolution(value: str) -> tuple[int, int]:
    """Parse and validate a ``WIDTHxHEIGHT`` game-resolution value."""
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        resolution = (int(width_text), int(height_text))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Resolution must have the format WIDTHxHEIGHT.") from exc
    if any(dimension <= 0 for dimension in resolution):
        raise argparse.ArgumentTypeError("Resolution dimensions must be positive.")
    return resolution


def main():
    """Run an explicit user-assisted Margit operational workflow."""
    parser = argparse.ArgumentParser(
        description="Run Margit-only manual observation and calibration checks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    observe_parser = subparsers.add_parser("observe", help="Observe a user-controlled Margit fight.")
    observe_parser.add_argument("--steps", type=int, default=10_000)
    observe_parser.add_argument("--interval", type=float, default=0.2)
    observe_parser.add_argument("--stop-on-player-death", action="store_true")
    observe_parser.add_argument("--game-resolution", type=_parse_resolution, default=(800, 450))

    summary_parser = subparsers.add_parser(
        "summary", help="Summarize a Margit observation artifact."
    )
    summary_parser.add_argument("--observer-json", type=Path)

    calibration_parser = subparsers.add_parser(
        "capture-calibration", help="Capture a Margit coordinate sample."
    )
    calibration_parser.add_argument("--capture-key", default="player_init_pose")
    calibration_parser.add_argument("--game-resolution", type=_parse_resolution, default=(800, 450))

    args = parser.parse_args()
    if args.command == "observe":
        observe(args.steps, args.interval, args.stop_on_player_death, args.game_resolution)
    elif args.command == "summary":
        summarize(args.observer_json)
    else:
        capture_calibration(args.capture_key, args.game_resolution)


if __name__ == "__main__":
    main()
