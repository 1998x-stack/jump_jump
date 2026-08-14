import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest


@pytest.fixture(autouse=True)
def pygame_setup():
    pygame.init()
    yield
    pygame.quit()