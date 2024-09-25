# main.py

import pygame
import sys
from config import *
from player import Player
from jump_platform import Platform
import game_functions as gf

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("jumping")
    clock = pygame.time.Clock()

    # Initialize player and platforms
    player = Player()
    platforms = [Platform()]

    # Font and score
    font = pygame.font.SysFont(None, 36)
    score = 0

    # Game loop
    while True:
        clock.tick(FPS)
        gf.check_events(player)

        # Update and draw
        gf.update_screen(screen, player, platforms)

        # Update score and display it
        score_surface = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

if __name__ == '__main__':
    run_game()