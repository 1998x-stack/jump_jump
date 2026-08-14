# player.py

import pygame
from config import (PLAYER_SIZE, PLAYER_START_POS, GRAVITY, PLAYER_COLOR,
                    PLAYER_SPEED, BOUNCE_VELOCITY, SCREEN_WIDTH)


class Player:
    def __init__(self):
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = PLAYER_START_POS
        self.vel_y = 0.0
        self.direction = 0

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

    def move_horizontal(self):
        self.rect.x += self.direction * PLAYER_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def collide(self, platform):
        if (self.vel_y > 0 and self.rect.colliderect(platform.rect)
                and self.rect.bottom - self.vel_y <= platform.rect.top):
            self.vel_y = BOUNCE_VELOCITY
            self.rect.bottom = platform.rect.top
            return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)