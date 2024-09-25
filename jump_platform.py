# platform.py

import pygame
from config import *

class Platform:
    def __init__(self):
        # Load platform image
        self.image = pygame.Surface(PLATFORM_SIZE)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

    def draw(self, screen):
        screen.blit(self.image, self.rect)