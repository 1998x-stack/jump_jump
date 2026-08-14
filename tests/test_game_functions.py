import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from config import SCREEN_HEIGHT, SHIFT_THRESHOLD
from player import Player
from jump_platform import generate_initial_platforms
import game_functions as gf


def test_update_screen_scrolls_when_player_high():
    screen = pygame.display.set_mode((10, 10))
    player = Player()
    platforms = generate_initial_platforms()
    player.rect.top = 0  # too high -> must scroll
    scroll = gf.update_screen(screen, player, platforms)
    assert scroll > 0
    assert player.rect.top == SHIFT_THRESHOLD


def test_update_screen_no_scroll_when_below_threshold():
    screen = pygame.display.set_mode((10, 10))
    player = Player()
    player.rect.top = SHIFT_THRESHOLD + 50
    platforms = generate_initial_platforms()
    scroll = gf.update_screen(screen, player, platforms)
    assert scroll == 0


def test_platforms_scroll_down_together():
    screen = pygame.display.set_mode((10, 10))
    player = Player()
    platforms = generate_initial_platforms()
    before = [p.rect.y for p in platforms]
    player.rect.top = 100  # small scroll, so no platform is pruned (keeps N stable)
    scroll = gf.update_screen(screen, player, platforms)
    assert scroll > 0
    after = [p.rect.y for p in platforms]
    assert all(a == b + scroll for a, b in zip(after, before))