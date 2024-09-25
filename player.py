# player.py

import pygame
from config import *

class Player:
    def __init__(self):
        # Load player image
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = PLAYER_START_POS
        self.vel_y = 0
        self.is_jumping = False
        self.press_time = 0

    def update(self):
        # Gravity and jump update
        if self.is_jumping:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y

    def check_collision(self, platforms):
        # Check collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.is_jumping = False
                self.vel_y = 0
                self.rect.bottom = platform.rect.top

    def draw(self, screen):
        screen.blit(self.image, self.rect)