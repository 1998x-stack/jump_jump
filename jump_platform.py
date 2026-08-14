# jump_platform.py

import random

import pygame
from config import (PLATFORM_SIZE, PLATFORM_COLOR, PLATFORM_MIN_GAP,
                    PLATFORM_MAX_GAP, SCREEN_WIDTH, SCREEN_HEIGHT)


class Platform:
    def __init__(self, x, y):
        self.image = pygame.Surface(PLATFORM_SIZE)
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def _random_x():
    return random.randint(0, SCREEN_WIDTH - PLATFORM_SIZE[0])


def _next_y(top):
    return top - random.randint(PLATFORM_MIN_GAP, PLATFORM_MAX_GAP)


def generate_initial_platforms():
    platforms = [Platform(_random_x(), SCREEN_HEIGHT - 150)]
    while platforms[-1].rect.top > 0:
        platforms.append(Platform(_random_x(), _next_y(platforms[-1].rect.top)))
    return platforms


def refill_platforms(platforms):
    if not platforms:
        platforms.append(Platform(_random_x(), SCREEN_HEIGHT - 150))
    while platforms[-1].rect.top > 0:
        platforms.append(Platform(_random_x(), _next_y(platforms[-1].rect.top)))


def remove_platforms_below(platforms, screen_height):
    for p in list(platforms):
        if p.rect.top > screen_height:
            platforms.remove(p)