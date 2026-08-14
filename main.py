# main.py

"""Jump Jump — endless golden-hour jumper.

Usage:
    python main.py                 # interactive windowed game
    python main.py --headless      # drive it from stdin, get JSON state per frame
    python main.py --seed 7        # reproducible world
"""

import argparse
import json
import sys

from core import Game, FPS, SCREEN_WIDTH, SCREEN_HEIGHT


# --------------------------------------------------------------------------- #
# Input translation (windowed)
# --------------------------------------------------------------------------- #
def _event_action(event):
    import pygame
    if event.type == pygame.QUIT:
        return "quit"
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_LEFT, pygame.K_a):
            return "left"
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            return "right"
        if event.key == pygame.K_SPACE:
            return "space"
    if event.type == pygame.KEYUP and event.key in (
            pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
        return "stop"
    return None


def _direction(action):
    if action == "left":
        return -1
    if action == "right":
        return 1
    if action == "stop":
        return 0
    return None


def run_windowed(seed=None):
    import pygame
    import view

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jump Jump — Golden Hour")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("verdana", 30, bold=True)
    small = pygame.font.SysFont("verdana", 22, bold=True)

    game = Game(seed=seed)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            action = _event_action(event)
            if action == "quit":
                pygame.quit()
                sys.exit()
            if action == "space" and game.state == "game_over":
                game.reset()
            direction = _direction(action)
            if direction is not None:
                game.direction = direction

        game.step()

        if game.state == "playing":
            view.render(screen, game, font)
        else:
            view.render_game_over(screen, game, font, small)
        pygame.display.flip()


# --------------------------------------------------------------------------- #
# Headless runner: one action per stdin line, one JSON line per frame
# --------------------------------------------------------------------------- #
def run_headless(seed=None):
    game = Game(seed=seed)
    for line in sys.stdin:
        action = line.strip().lower() or None
        if action == "q":
            break
        snapshot = game.step(action)
        if snapshot is not None:
            print(json.dumps(snapshot), flush=True)


def _check_expectations(expect, summary):
    """Evaluate a small dict of goal assertions against the final summary.

    Supported keys: score_ge, score_le, state, not_state, frames_ge, frames_le.
    Returns (results_dict, passed_bool)."""
    results = {}
    score = summary.get("score", 0)
    frames = summary.get("frames", 0)
    state = summary.get("final_state")
    if "score_ge" in expect:
        results["score_ge"] = score >= expect["score_ge"]
    if "score_le" in expect:
        results["score_le"] = score <= expect["score_le"]
    if "state" in expect:
        results["state"] = state == expect["state"]
    if "not_state" in expect:
        results["not_state"] = state != expect["not_state"]
    if "frames_ge" in expect:
        results["frames_ge"] = frames >= expect["frames_ge"]
    if "frames_le" in expect:
        results["frames_le"] = frames <= expect["frames_le"]
    return results, (all(results.values()) if results else True)


# --------------------------------------------------------------------------- #
# Scripted batch runner: a small JSON plan of actions, replayed deterministically
# --------------------------------------------------------------------------- #
def run_script(script_path, fallback_seed=None):
    if script_path == "-":
        data = json.loads(sys.stdin.read())
    else:
        with open(script_path, encoding="utf-8") as fh:
            data = json.load(fh)

    game = Game(seed=data.get("seed", fallback_seed))
    frames_run = 0
    for entry in data.get("actions", []):
        action = entry.get("action")
        frames = int(entry.get("frames", 1))
        for _ in range(frames):
            snapshot = game.step(action)
            if snapshot is None:
                break
            frames_run += 1
            print(json.dumps(snapshot), flush=True)

    summary = {
        "done": True,
        "frames": frames_run,
        "final_state": game.state,
        "score": int(game.score),
        "progress": round(game.progress(), 3),
        "player": {"x": int(game.player.x), "y": int(game.player.y)},
    }
    expect = data.get("expect", {})
    results, passed = _check_expectations(expect, summary)
    if results:
        summary["results"] = results
        summary["passed"] = passed
    print(json.dumps(summary), flush=True)
    return 0 if passed else 1


# --------------------------------------------------------------------------- #
def main(argv=None):
    parser = argparse.ArgumentParser(description="Jump Jump — endless jumper")
    parser.add_argument("--headless", action="store_true",
                        help="no window; read one action per stdin line, "
                             "print one JSON state line per frame")
    parser.add_argument("--script", metavar="FILE", default=None,
                        help="run a JSON action recipe; FILE may be '-' for stdin")
    parser.add_argument("--seed", type=int, default=None,
                        help="seed for a reproducible world")
    args = parser.parse_args(argv)

    if args.script is not None:
        code = run_script(args.script, args.seed)
        sys.exit(code)
    elif args.headless:
        run_headless(args.seed)
    else:
        run_windowed(args.seed)


if __name__ == "__main__":
    main()