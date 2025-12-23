import pygame
from typing import List, Optional


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group]) -> None:
        super().__init__(*groups)
        self.frame_index: float = 0
        self.animation_speed: float = 0.15
        self.direction: pygame.math.Vector2 = pygame.math.Vector2()

        self.velocity: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self.speed: int = 0

        self.pos: pygame.math.Vector2 = pygame.math.Vector2(0.0, 0.0)

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.hitbox: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.obstacle_sprites: Optional[pygame.sprite.Group] = None

    def move(self, dt: float) -> None:
        if self.velocity.magnitude() > 0:
            self.velocity = self.velocity.normalize() * self.speed

        self.pos.x += self.velocity.x * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')

        self.pos.y += self.velocity.y * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def collision(self, direction: str) -> None:
        if self.obstacle_sprites is None:
            return

        for sprite in self.obstacle_sprites:
            obstacle_rect = getattr(sprite, 'hitbox', sprite.rect)

            if obstacle_rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.velocity.x > 0:
                        self.hitbox.right = obstacle_rect.left
                    if self.velocity.x < 0:
                        self.hitbox.left = obstacle_rect.right
                    self.pos.x = self.hitbox.centerx

                if direction == 'vertical':
                    if self.velocity.y > 0:
                        self.hitbox.bottom = obstacle_rect.top
                    if self.velocity.y < 0:
                        self.hitbox.top = obstacle_rect.bottom
                    self.pos.y = self.hitbox.centery
