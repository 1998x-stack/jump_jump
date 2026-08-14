import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (PLATFORM_MIN_GAP, PLATFORM_MAX_GAP, SCREEN_WIDTH,
                    SCREEN_HEIGHT, PLATFORM_SIZE, HORIZ_REACH)
from jump_platform import (generate_initial_platforms, refill_platforms,
                           remove_platforms_below)


def check_gaps(platforms):
    for a, b in zip(platforms, platforms[1:]):
        gap = a.rect.top - b.rect.top  # a lower, b higher (list order)
        assert PLATFORM_MIN_GAP <= gap <= PLATFORM_MAX_GAP, gap


def test_initial_platforms_reach_above_screen():
    platforms = generate_initial_platforms()
    assert platforms
    tops = sorted(p.rect.top for p in platforms)
    assert tops[0] <= 0  # highest reaches the top of the viewport
    assert tops[-1] >= SCREEN_HEIGHT - 150  # bottom is near the start zone


def test_initial_gaps_within_reachable_range():
    check_gaps(generate_initial_platforms())


def test_platforms_inside_horizontal_bounds():
    for p in generate_initial_platforms():
        assert p.rect.left >= 0
        assert p.rect.right <= SCREEN_WIDTH


def test_consecutive_platforms_within_horizontal_reach():
    platforms = generate_initial_platforms()
    for a, b in zip(platforms, platforms[1:]):
        # a below, b above; their centers must be within HORIZ_REACH
        assert abs(a.rect.centerx - b.rect.centerx) <= HORIZ_REACH


def test_refill_extends_to_top():
    platforms = generate_initial_platforms()
    for p in platforms:
        p.rect.y += 400  # simulate the world scrolling down
    assert min(p.rect.top for p in platforms) > 0
    refill_platforms(platforms)
    assert min(p.rect.top for p in platforms) <= 0
    check_gaps(platforms)


def test_remove_platforms_below_screen():
    platforms = generate_initial_platforms()
    total = len(platforms)
    # push a couple of the lowest platforms fully below the screen
    pushed = 0
    for p in platforms:
        if p.rect.top <= SCREEN_HEIGHT - PLATFORM_SIZE[1]:
            p.rect.y = SCREEN_HEIGHT + 100
            pushed += 1
            if pushed == 3:
                break
    remove_platforms_below(platforms, SCREEN_HEIGHT)
    assert all(p.rect.top <= SCREEN_HEIGHT for p in platforms)
    assert len(platforms) == total - pushed