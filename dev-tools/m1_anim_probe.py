"""M1.2 probe: test the MargitAnimation offset-fix hypothesis (read-only).

Reads candidate pointer chains repeatedly and classifies the values. No writes
beyond standard EldenRing() construction (speedhack DLL + speed 1.0), which the
user already approved via m1_gonogo.py. Untracked; not part of the PR.

    conda run -n soulsgym --no-capture-output python m1_anim_probe.py
"""

import time

from soulsgym.games import EldenRing

SAMPLES = 24
INTERVAL = 0.5

CHAINS = {
    "H1_anim_id           [0x18,0x20]": {"base": "WorldChrMan", "offsets": [0x500, 0x180, 0x190, 0x18, 0x20], "type": "int"},
    "H2_anim_time_f       [0x18,0x24]": {"base": "WorldChrMan", "offsets": [0x500, 0x180, 0x190, 0x18, 0x24], "type": "float"},
    "H3_anim_maxtime_f    [0x18,0x28]": {"base": "WorldChrMan", "offsets": [0x500, 0x180, 0x190, 0x18, 0x28], "type": "float"},
    "old_AnimTime         [0x80,0x90]": {"base": "WorldChrMan", "offsets": [0x500, 0x180, 0x190, 0x80, 0x90], "type": "float"},
    "old_AnimMaxTime      [0x80,0x94]": {"base": "WorldChrMan", "offsets": [0x500, 0x180, 0x190, 0x80, 0x94], "type": "float"},
}


def classify(vals: list[int | float]) -> str:
    """Summarize sampled values and whether they look like animation IDs."""
    s = set(vals)
    if not s:
        return "no reads"
    if all(isinstance(v, float) for v in s):
        lo, hi = min(s), max(s)
        return f"{len(s)} distinct float, range [{lo:.3f} .. {hi:.3f}]"
    small = all(isinstance(v, int) and -1 <= v < 10_000_000 for v in s)
    kind = "TAE-plausible" if small else "pointer-like/garbage"
    return f"{len(s)} distinct, {kind}: {sorted(s)[:8]}"


def main():
    """Sample the candidate animation addresses and print a summary."""
    game = EldenRing()
    print(f"[probe] is_ingame={game.is_ingame}  margit_hp={game.margit_hp}/{game.margit_max_hp}")
    print(f"[probe] margit_pose={game.margit_pose}")
    print(f"[probe] sampling {SAMPLES}x every {INTERVAL}s ...", flush=True)

    results = {name: [] for name in CHAINS}
    results["control_PlayerAnimation"] = []
    for _ in range(SAMPLES):
        game.clear_cache()
        for name, rec in CHAINS.items():
            try:
                results[name].append(game.mem.read_record(rec))
            except Exception as exc:
                results[name].append(f"ERR:{type(exc).__name__}")
        try:
            results["control_PlayerAnimation"].append(
                game.mem.read_record(game.data.addresses["PlayerAnimation"])
            )
        except Exception as exc:
            results["control_PlayerAnimation"].append(f"ERR:{type(exc).__name__}")
        time.sleep(INTERVAL)

    print("\n=== RESULTS ===")
    for name, vals in results.items():
        ok = [v for v in vals if not isinstance(v, str)]
        errs = len(vals) - len(ok)
        print(f"{name:34s} errs={errs:2d}  {classify(ok)}")


if __name__ == "__main__":
    main()
