# game_functions.py

import sys

import pygame
from config import SCREEN_HEIGHT, SHIFT_THRESHOLD, WHITE
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


def update_screen(screen, player, platforms):
    screen.fill(WHITE)

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