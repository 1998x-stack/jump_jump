# main.py

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from player import Player
from jump_platform import generate_initial_platforms
import game_functions as gf


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jump Jump")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    state = "playing"
    score = 0
    platforms = generate_initial_platforms()
    player = Player()

    while True:
        clock.tick(FPS)
        action = gf.check_events(player)

        if action == "restart" and state == "game_over":
            state = "playing"
            score = 0
            platforms = generate_initial_platforms()
            player = Player()

        if state == "playing":
            scroll = gf.update_screen(screen, player, platforms)
            score += scroll
            score_surface = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_surface, (10, 10))
            if player.rect.top > SCREEN_HEIGHT:
                state = "game_over"
        else:
            screen.fill(WHITE)
            over = font.render(f"Game Over - Score: {score}", True, BLACK)
            prompt = font.render("Press SPACE to restart", True, BLACK)
            cx = SCREEN_WIDTH // 2
            screen.blit(over, (cx - over.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(prompt, (cx - prompt.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()


if __name__ == "__main__":
    run_game()