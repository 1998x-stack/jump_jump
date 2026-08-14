"""Smoke tests for the pygame render layer (needs a display, so headless dummy)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from core import Game, SCREEN_WIDTH, SCREEN_HEIGHT
import view


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def screen():
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


@pytest.fixture
def fonts():
    f = pygame.font.SysFont("verdana", 30, bold=True)
    s = pygame.font.SysFont("verdana", 22, bold=True)
    return f, s


def test_render_playing_frame(screen, fonts):
    game = Game(seed=1)
    view.render(screen, game, fonts[0])
    assert screen.get_at((1, 1)) is not None


def test_render_game_over_card(screen, fonts):
    game = Game(seed=1)
    game.state = "game_over"
    game.score = 42
    view.render_game_over(screen, game, *fonts)
    pygame.image.save(screen, "/tmp/render_game_over.png")


def test_sky_shifts_between_palettes(screen):
    dusk = view.gradient_surface(0.0).get_at((5, 5))[:3]
    dawn = view.gradient_surface(1.0).get_at((5, 5))[:3]
    assert dusk[0] < dawn[0]  # red channel climbs with altitude


def test_sky_is_cached(screen):
    a = view.gradient_surface(0.5)
    b = view.gradient_surface(0.5)
    assert a is b