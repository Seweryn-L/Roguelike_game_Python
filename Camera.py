import pygame
from settings import *


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        # self.all_sprites = pygame.sprite.Group()
        self.offset = pygame.math.Vector2(0, 0)
        self.center = (WIDTH / 2, HEIGHT / 2)

        # --- NOWOŚĆ: Domyślne wymiary mapy ---
        self.map_width = 4000
        self.map_height = 4000

    # --- NOWOŚĆ: Metoda do ustawiania granic (wywoływana w Game.py) ---
    def set_limits(self, width, height):
        self.map_width = width
        self.map_height = height

    def custom_draw(self, player):
        # 1. Obliczanie pozycji kamery (tak by gracz był na środku)
        self.offset.x = player.rect.centerx - self.center[0]
        self.offset.y = player.rect.centery - self.center[1]

        # --- NOWOŚĆ: Blokowanie kamery (Clamping) ---
        # Nie pozwól wyjechać w lewo (x < 0)
        if self.offset.x < 0:
            self.offset.x = 0
        # Nie pozwól wyjechać w górę (y < 0)
        if self.offset.y < 0:
            self.offset.y = 0

        # Nie pozwól wyjechać w prawo (szerokość mapy - szerokość ekranu)
        # max(..., 0) zapobiega błędom, gdyby mapa była mniejsza niż ekran
        right_limit = max(self.map_width - WIDTH, 0)
        if self.offset.x > right_limit:
            self.offset.x = right_limit

        # Nie pozwól wyjechać w dół (wysokość mapy - wysokość ekranu)
        bottom_limit = max(self.map_height - HEIGHT, 0)
        if self.offset.y > bottom_limit:
            self.offset.y = bottom_limit
        # ---------------------------------------------

        # --- ORYGINALNY KOD RYSOWANIA (BEZ ZMIAN) ---
        for sprite in self.sprites():
            if sprite.z == LAYERS['floor']:
                offset_pos = sprite.rect.topleft - self.offset
                self.screen.blit(sprite.image, offset_pos)

        for sprite in self.sprites():
            if sprite.z == LAYERS['main']:
                offset_pos = sprite.rect.topleft - self.offset
                self.screen.blit(sprite.image, offset_pos)