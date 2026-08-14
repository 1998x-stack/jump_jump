# main.py

import pygame
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SHADOW, SCORE_TEXT,
                    PLATFORM_TOP, PLATFORM_EDGE, STAR_COLOR)
from player import Player
from jump_platform import generate_initial_platforms
import game_functions as gf


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jump Jump — Golden Hour")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("verdana", 30, bold=True)
    small_font = pygame.font.SysFont("verdana", 22, bold=True)

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

        progress = min(1.0, score / 2000.0)

        if state == "playing":
            scroll = gf.update_screen(screen, player, platforms, progress)
            score += scroll
            draw_text(screen, font, f"Score: {score}", (12, 12))
            if player.rect.top > SCREEN_HEIGHT:
                state = "game_over"
        else:
            draw_game_over(screen, font, small_font, score, progress)

        pygame.display.flip()


def draw_text(screen, font, text, pos):
    shadow = font.render(text, True, SHADOW)
    label = font.render(text, True, SCORE_TEXT)
    screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
    screen.blit(label, pos)


def draw_game_over(screen, font, small_font, score, progress):
    screen.blit(gf.gradient_surface(progress), (0, 0))
    gf._draw_stars(screen)
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((20, 20, 45, 130))
    screen.blit(dim, (0, 0))

    card = pygame.Rect(0, 0, 340, 180)
    card.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, PLATFORM_TOP, card, border_radius=20)
    pygame.draw.rect(screen, PLATFORM_EDGE, card, width=2, border_radius=20)

    title = font.render("You fell", True, SHADOW)
    sub = small_font.render(f"You reached {score}", True, SHADOW)
    prompt = small_font.render("Press SPACE to rise again", True, SHADOW)
    cx = SCREEN_WIDTH // 2
    screen.blit(title, (cx - title.get_width() // 2, card.top + 24))
    screen.blit(sub, (cx - sub.get_width() // 2, card.top + 66))
    screen.blit(prompt, (cx - prompt.get_width() // 2, card.top + 112))


if __name__ == "__main__":
    run_game()