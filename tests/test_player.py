import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from config import GRAVITY, PLAYER_SPEED, BOUNCE_VELOCITY, SCREEN_WIDTH
from player import Player


def plat_at(left, top, width=100, height=20):
    return SimpleNamespace(rect=pygame.Rect(left, top, width, height))


def test_gravity_applies_when_moving():
    p = Player()
    p.vel_y = 0.0
    before_y = p.rect.y
    p.update()
    assert p.vel_y == GRAVITY
    assert p.rect.y > before_y


def test_horizontal_move_right():
    p = Player()
    p.direction = 1
    before_x = p.rect.x
    p.move_horizontal()
    assert p.rect.x == before_x + PLAYER_SPEED


def test_horizontal_clamped_to_left():
    p = Player()
    p.rect.left = 0
    p.direction = -1
    p.move_horizontal()
    assert p.rect.left == 0


def test_horizontal_clamped_to_right():
    p = Player()
    p.rect.right = SCREEN_WIDTH
    p.direction = 1
    p.move_horizontal()
    assert p.rect.right == SCREEN_WIDTH


def test_bounce_on_landing():
    p = Player()
    p.vel_y = 10
    plat = plat_at(0, 100)
    p.rect.left = plat.rect.left + 25   # overhang the platform horizontally
    p.rect.bottom = plat.rect.top + 5   # this frame landed a bit into the platform
    assert p.collide(plat) is True
    assert p.vel_y == BOUNCE_VELOCITY
    assert p.rect.bottom == plat.rect.top


def test_no_bounce_when_moving_up():
    p = Player()
    p.vel_y = -5
    plat = plat_at(0, 100)
    assert p.collide(plat) is False


def test_no_bounce_when_approaching_from_side():
    p = Player()
    p.vel_y = 10
    # overlapping horizontally, but previous frame's bottom was well below
    # the platform top -> this is a side hit, not a landing
    plat = plat_at(0, 100)
    p.rect.left = 0
    p.rect.top = 130  # bottom = 180, previous bottom = 170 > platform top(100)
    assert p.collide(plat) is False


def plat_at(left, top, width=100, height=20):
    return SimpleNamespace(rect=pygame.Rect(left, top, width, height))