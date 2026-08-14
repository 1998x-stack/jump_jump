"""Pure-engine tests. None of these need a display or pygame."""

import subprocess
import sys

import pytest

from core import (Game, Player, Platform, generate_initial_platforms,
                  refill_platforms, remove_platforms_below,
                  GRAVITY, PLAYER_SPEED, MAX_FALL_SPEED, BOUNCE_VELOCITY,
                  PLATFORM_MIN_GAP, PLATFORM_MAX_GAP, HORIZ_REACH,
                  SCREEN_WIDTH, SCREEN_HEIGHT)

# --------------------------------------------------------------------------- #
# Guarantee: core is pygame-free
# --------------------------------------------------------------------------- #
def test_core_imports_without_pygame():
    code = subprocess.run(
        [sys.executable, "-c", "import core; print('ok')"],
        capture_output=True, text=True, cwd=__import__("os").getcwd())
    assert code.returncode == 0, code.stderr
    assert "ok" in code.stdout


def test_core_source_has_no_pygame_import():
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "core.py")).read()
    assert "import pygame" not in src
    assert "from pygame" not in src


# --------------------------------------------------------------------------- #
# Player physics
# --------------------------------------------------------------------------- #
def test_gravity_applies():
    p = Player(); p.vy = 0.0
    before = p.y
    p.apply_gravity()
    assert p.vy == GRAVITY
    assert p.y > before


def test_fall_speed_capped():
    p = Player(); p.vy = MAX_FALL_SPEED * 2
    p.apply_gravity()
    assert p.vy <= MAX_FALL_SPEED


def test_horizontal_move_and_clamp():
    p = Player(); p.dir = 1
    before = p.x
    p.move_horizontal()
    assert p.x == before + PLAYER_SPEED
    p.x = -5
    p.move_horizontal()
    assert p.x >= 0


# --------------------------------------------------------------------------- #
# Platform generation
# --------------------------------------------------------------------------- #
def test_platforms_reach_above_screen():
    plats = generate_initial_platforms()
    tops = sorted(p.top for p in plats)
    assert tops[0] <= 0
    assert tops[-1] >= SCREEN_HEIGHT - 150


def test_gaps_within_reach():
    plats = generate_initial_platforms()
    for a, b in zip(plats, plats[1:]):
        assert PLATFORM_MIN_GAP <= a.top - b.top <= PLATFORM_MAX_GAP


def test_horizontal_reach():
    plats = generate_initial_platforms()
    for a, b in zip(plats, plats[1:]):
        assert abs(a.centerx - b.centerx) <= HORIZ_REACH


def test_refill_and_prune():
    plats = generate_initial_platforms()
    for p in plats:
        p.y += 400
    refill_platforms(plats)
    assert min(p.top for p in plats) <= 0
    for p in list(plats):
        p.y = SCREEN_HEIGHT + 100
    remove_platforms_below(plats)
    assert all(p.top <= SCREEN_HEIGHT for p in plats)