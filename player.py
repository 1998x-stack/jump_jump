# player.py

import pygame
from config import (PLAYER_SIZE, PLAYER_START_POS, GRAVITY, PLAYER_COLOR,
                    PLAYER_CORE, PLAYER_OUTLINE, PLAYER_SPEED, BOUNCE_VELOCITY,
                    SCREEN_WIDTH, MAX_FALL_SPEED)


class Player:
    def __init__(self):
        self.image = self._render(PLAYER_SIZE)
        self.rect = self.image.get_rect()
        self.rect.center = PLAYER_START_POS
        self.vel_y = 0.0
        self.direction = 0

    @staticmethod
    def _render(size):
        w, h = size
        img = pygame.Surface((w, h), pygame.SRCALPHA)
        radius = 14
        # body with outline
        pygame.draw.rect(img, PLAYER_OUTLINE, (0, 0, w, h), border_radius=radius)
        pygame.draw.rect(img, PLAYER_COLOR, (2, 2, w - 4, h - 4),
                         border_radius=radius - 2)
        # warm core glow near the top
        pygame.draw.circle(img, PLAYER_CORE, (w // 2, h // 2 - 6), w // 4)
        # eyes
        pygame.draw.circle(img, PLAYER_OUTLINE, (w // 2 - 11, h // 2 + 4), 4)
        pygame.draw.circle(img, PLAYER_OUTLINE, (w // 2 + 11, h // 2 + 4), 4)
        return img

    def update(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
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