# entity.py
import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

        # --- FIX: DEKLARACJA ZMIENNYCH ---
        # Tworzymy te zmienne tutaj z wartościami "pustymi",
        # tylko po to, żeby metody move() i collision() wiedziały, że one istnieją.
        # Klasy Player i Enemy natychmiast je nadpiszą swoimi wartościami.

        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 0
        self.pos = pygame.math.Vector2(0, 0)

        # Tworzymy pusty prostokąt jako placeholder
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        # To już miałeś
        self.obstacle_sprites = None

    def move(self, dt):
        # Normalizacja prędkości
        if self.velocity.magnitude() > 0:
            self.velocity = self.velocity.normalize() * self.speed

        # Ruch X
        self.pos.x += self.velocity.x * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')

        # Ruch Y
        self.pos.y += self.velocity.y * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if self.obstacle_sprites is None:
            return

        for sprite in self.obstacle_sprites:
            # --- NOWOŚĆ: Wybór właściwego prostokąta kolizji ---
            # Jeśli przeszkoda (np. Gracz) ma hitbox, używamy go.
            # Jeśli to zwykła ściana bez hitboxa, używamy jej rect.
            if hasattr(sprite, 'hitbox'):
                obstacle_rect = sprite.hitbox
            else:
                obstacle_rect = sprite.rect

            # --- ZMIANA: Wszędzie poniżej używamy obstacle_rect zamiast sprite.rect ---
            if obstacle_rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.velocity.x > 0:  # Prawo
                        self.hitbox.right = obstacle_rect.left
                    if self.velocity.x < 0:  # Lewo
                        self.hitbox.left = obstacle_rect.right
                    self.pos.x = self.hitbox.centerx

                if direction == 'vertical':
                    if self.velocity.y > 0:  # Dół
                        self.hitbox.bottom = obstacle_rect.top
                    if self.velocity.y < 0:  # Góra
                        self.hitbox.top = obstacle_rect.bottom
                    self.pos.y = self.hitbox.centery