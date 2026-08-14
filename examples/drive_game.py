"""Example: drive the headless Jump Jump engine as a Python library.

No window is opened and pygame is never imported. This is the entry point for
embedding the game in another program (a bot, an agent, a simulator, CI, ...).

The simple driver below aims at the nearest ledge above the player so it keeps
climbing -- a tiny example of reading `game.snapshot()` and reacting to it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Game


def choose_action(game):
    """Point the player at the nearest ledge just below its feet."""
    target, best = None, None
    for plat in game.platforms:
        dist = plat.top - game.player.bottom
        if 0 <= dist <= 240 and (best is None or dist < best):
            best, target = dist, plat
    if target is None:
        return "stop"
    dx = target.centerx - game.player.centerx
    return "right" if dx > 10 else "left" if dx < -10 else "stop"


def main():
    game = Game(seed=7)
    for _ in range(2000):
        game.step(choose_action(game))

    snap = game.snapshot()
    print(f"after {snap['frame']} frames: state={snap['state']} "
          f"score={snap['score']} platforms={snap['platforms']}")


if __name__ == "__main__":
    main()