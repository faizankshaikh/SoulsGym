"""Canonical random-agent smoke runner using the gym API.

This script intentionally avoids mutating private environment internals.
"""

from __future__ import annotations

import gymnasium

import soulsgym  # noqa: F401


def run_random_agent(env_id: str = "SoulsGymMargit-v0", steps: int = 10):
    """Run a short random-agent rollout.

    Args:
        env_id: Gym environment ID.
        steps: Maximum number of environment steps.
    """
    env = gymnasium.make(env_id)
    try:
        obs, info = env.reset()
        print(f"Initialized {env_id}: player_hp={float(obs['player_hp'][0]):.1f} "
              f"boss_hp={float(obs['boss_hp'][0]):.1f}")
        terminated, truncated = False, False
        for i in range(steps):
            if terminated or truncated:
                break
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            print(
                f"step={i + 1} action={action} reward={float(reward):.4f} "
                f"player_hp={float(obs['player_hp'][0]):.1f} "
                f"boss_hp={float(obs['boss_hp'][0]):.1f} term={terminated} trunc={truncated}"
            )
    finally:
        env.close()


if __name__ == "__main__":
    run_random_agent()
