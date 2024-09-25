# game_functions.py

import sys
import pygame
from config import *

def check_events(player):
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.is_jumping = False
                player.press_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                current_time = pygame.time.get_ticks()
                hold_time = current_time - player.press_time
                player.is_jumping = True
                player.vel_y = -hold_time / 100 * FORCE_FACTOR

def update_screen(screen, player, platforms):
    # Update screen visuals
    screen.fill(WHITE)
    player.update()
    player.check_collision(platforms)

    # Draw platforms
    for platform in platforms:
        platform.draw(screen)
    
    # Draw player
    player.draw(screen)