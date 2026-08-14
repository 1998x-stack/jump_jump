# jump_platform.py

import random

import pygame
from config import (PLATFORM_SIZE, PLATFORM_COLOR, PLATFORM_MIN_GAP,
                    PLATFORM_MAX_GAP, SCREEN_WIDTH, SCREEN_HEIGHT, HORIZ_REACH)


class Platform:
    def __init__(self, x, y):
        self.image = pygame.Surface(PLATFORM_SIZE)
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def _next_y(top):
    return top - random.randint(PLATFORM_MIN_GAP, PLATFORM_MAX_GAP)


def _next_x(prev_center):
    # keep the new platform's center within horizontal reach of the previous one
    center = prev_center + random.randint(-HORIZ_REACH, HORIZ_REACH)
    center = max(PLATFORM_SIZE[0] // 2,
                 min(SCREEN_WIDTH - PLATFORM_SIZE[0] // 2, center))
    return center - PLATFORM_SIZE[0] // 2


def _seed_platform(start_x=None):
    # first platform is centered under the player's spawn point
    if start_x is None:
        start_x = (SCREEN_WIDTH - PLATFORM_SIZE[0]) // 2
    return Platform(start_x, SCREEN_HEIGHT - 100)


def generate_initial_platforms():
    platforms = [_seed_platform()]
    prev_center = platforms[0].rect.centerx
    while platforms[-1].rect.top > 0:
        x = _next_x(prev_center)
        platforms.append(Platform(x, _next_y(platforms[-1].rect.top)))
        prev_center = platforms[-1].rect.centerx
    return platforms


def refill_platforms(platforms):
    if not platforms:
        platforms.append(_seed_platform())
    prev_center = platforms[-1].rect.centerx
    while platforms[-1].rect.top > 0:
        x = _next_x(prev_center)
        platforms.append(Platform(x, _next_y(platforms[-1].rect.top)))
        prev_center = platforms[-1].rect.centerx


def remove_platforms_below(platforms, screen_height):
    for p in list(platforms):
        if p.rect.top > screen_height:
            platforms.remove(p)