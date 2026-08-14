# game_functions.py

import random
import sys

import pygame
from config import (SCREEN_HEIGHT, SCREEN_WIDTH, SHIFT_THRESHOLD,
                    SKY_TOP_DUSK, SKY_MID_DUSK, SKY_TOP_DAWN, SKY_MID_DAWN,
                    SKY_HORIZON, STAR_COLOR)
from jump_platform import refill_platforms, remove_platforms_below


def check_events(player):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                player.direction = -1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                player.direction = 1
            elif event.key == pygame.K_SPACE:
                return "restart"
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a) and player.direction == -1:
                player.direction = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and player.direction == 1:
                player.direction = 0
    return None


# --- Sky -------------------------------------------------------------------

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


_grad_cache = {}


def gradient_surface(progress):
    """Vertical dusk sky that tilts toward dawn as the player climbs."""
    key = int(max(0.0, min(1.0, progress)) * 100)
    if key in _grad_cache:
        return _grad_cache[key]
    t = max(0.0, min(1.0, progress))
    top = _lerp(SKY_TOP_DUSK, SKY_TOP_DAWN, t)
    mid = _lerp(SKY_MID_DUSK, SKY_MID_DAWN, t)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        if y < SCREEN_HEIGHT * 0.45:
            f = y / (SCREEN_HEIGHT * 0.45)
            color = _lerp(top, mid, f)
        else:
            f = (y - SCREEN_HEIGHT * 0.45) / (SCREEN_HEIGHT * 0.55)
            color = _lerp(mid, SKY_HORIZON, f)
        pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
    _grad_cache[key] = surf.convert()
    return _grad_cache[key]


# --- Atmosphere (drifting dust specks) -------------------------------------

_STARS = []


def _ensure_stars():
    if _STARS:
        return
    for _ in range(70):
        _STARS.append([random.randint(0, SCREEN_WIDTH),
                       random.randint(0, SCREEN_HEIGHT),
                       random.choice([1, 1, 2]),
                       random.uniform(0.2, 0.8)])


def _draw_stars(screen):
    _ensure_stars()
    for star in _STARS:
        star[1] += star[3]
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(screen, STAR_COLOR, (int(star[0]), int(star[1])),
                           star[2])


# --- Main render/update -----------------------------------------------------

def update_screen(screen, player, platforms, progress=0.0):
    screen.blit(gradient_surface(progress), (0, 0))
    _draw_stars(screen)

    player.move_horizontal()
    player.update()
    for platform in platforms:
        player.collide(platform)

    scroll = 0
    if player.rect.top < SHIFT_THRESHOLD:
        scroll = SHIFT_THRESHOLD - player.rect.top
        player.rect.top = SHIFT_THRESHOLD
        for platform in platforms:
            platform.rect.y += scroll

    refill_platforms(platforms)
    remove_platforms_below(platforms, SCREEN_HEIGHT)

    for platform in platforms:
        platform.draw(screen)
    player.draw(screen)

    return scroll