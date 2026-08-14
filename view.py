"""pygame rendering layer. Takes a headless `Game` (or its snapshot) and draws
the output. This is the only module that talks to pygame/SDL. Keeping it
separate from `core` lets the simulation run anywhere."""

import random

import pygame

from core import (SCREEN_WIDTH, SCREEN_HEIGHT, PLATFORM_WIDTH, PLATFORM_HEIGHT,
                  PLAYER_WIDTH, PLAYER_HEIGHT)

# --------------------------------------------------------------------------- #
# Golden Hour theme tokens
# --------------------------------------------------------------------------- #
SKY_TOP_DUSK = (42, 47, 90)
SKY_MID_DUSK = (90, 91, 160)
SKY_TOP_DAWN = (252, 170, 138)
SKY_MID_DAWN = (255, 210, 166)
SKY_HORIZON = (246, 227, 201)

PLATFORM_TOP = (255, 246, 228)
PLATFORM_BODY = (216, 192, 142)
PLATFORM_EDGE = (196, 168, 116)

PLAYER_COLOR = (242, 104, 90)
PLAYER_CORE = (255, 191, 164)
PLAYER_OUTLINE = (148, 62, 66)

SCORE_TEXT = (255, 246, 228)
SHADOW = (30, 28, 55)
STAR_COLOR = (255, 246, 228)


# --------------------------------------------------------------------------- #
# Sky
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Atmosphere (drifting dust specks)
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Elements
# --------------------------------------------------------------------------- #
def _draw_platform(screen, plat):
    rect = pygame.Rect(plat.x, plat.y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    radius = 7
    pygame.draw.rect(screen, PLATFORM_EDGE, rect, border_radius=radius)
    pygame.draw.rect(screen, PLATFORM_BODY,
                     rect.inflate(-4, -2).move(0, 1), border_radius=radius - 1)
    pygame.draw.line(screen, PLATFORM_TOP,
                     (rect.left + radius, rect.top + 3),
                     (rect.right - radius, rect.top + 3), 2)


def _draw_player(screen, player):
    p = player
    w, h = PLAYER_WIDTH, PLAYER_HEIGHT
    rect = pygame.Rect(int(p.x), int(p.y), w, h)
    radius = 14
    pygame.draw.rect(screen, PLAYER_OUTLINE, rect, border_radius=radius)
    pygame.draw.rect(screen, PLAYER_COLOR, rect.inflate(-4, -4),
                     border_radius=radius - 2)
    pygame.draw.circle(screen, PLAYER_CORE, (rect.centerx, rect.centery - 6),
                       w // 4)
    pygame.draw.circle(screen, PLAYER_OUTLINE, (rect.centerx - 11,
                                                rect.centery + 4), 4)
    pygame.draw.circle(screen, PLAYER_OUTLINE, (rect.centerx + 11,
                                                rect.centery + 4), 4)


def _draw_text(screen, font, text, pos):
    shadow = font.render(text, True, SHADOW)
    label = font.render(text, True, SCORE_TEXT)
    screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
    screen.blit(label, pos)


# --------------------------------------------------------------------------- #
# Public draw entry points
# --------------------------------------------------------------------------- #
def render(screen, game, score_font):
    """Draw the currently-played frame of a `Game` onto `screen`."""
    screen.blit(gradient_surface(game.progress()), (0, 0))
    _draw_stars(screen)
    for plat in game.platforms:
        _draw_platform(screen, plat)
    _draw_player(screen, game.player)
    _draw_text(screen, score_font, f"Score: {int(game.score)}", (12, 12))


def render_game_over(screen, game, font, small_font):
    screen.blit(gradient_surface(game.progress()), (0, 0))
    _draw_stars(screen)
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((20, 20, 45, 130))
    screen.blit(dim, (0, 0))

    card = pygame.Rect(0, 0, 340, 180)
    card.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, PLATFORM_TOP, card, border_radius=20)
    pygame.draw.rect(screen, PLATFORM_EDGE, card, width=2, border_radius=20)

    title = font.render("You fell", True, SHADOW)
    sub = small_font.render(f"You reached {int(game.score)}", True, SHADOW)
    prompt = small_font.render("Press SPACE to rise again", True, SHADOW)
    cx = SCREEN_WIDTH // 2
    screen.blit(title, (cx - title.get_width() // 2, card.top + 24))
    screen.blit(sub, (cx - sub.get_width() // 2, card.top + 66))
    screen.blit(prompt, (cx - prompt.get_width() // 2, card.top + 112))