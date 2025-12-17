import pygame
from settings import *


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(0, 0)
        self.center = (WIDTH / 2, HEIGHT / 2)
        self.map_width = 4000
        self.map_height = 4000
    def set_limits(self, width, height):
        self.map_width = width
        self.map_height = height

    def custom_draw(self, player):

        self.offset.x = player.rect.centerx - self.center[0]
        self.offset.y = player.rect.centery - self.center[1]


        if self.offset.x < 0:
            self.offset.x = 0
        if self.offset.y < 0:
            self.offset.y = 0


        right_limit = max(self.map_width - WIDTH, 0)
        if self.offset.x > right_limit:
            self.offset.x = right_limit


        bottom_limit = max(self.map_height - HEIGHT, 0)
        if self.offset.y > bottom_limit:
            self.offset.y = bottom_limit



        for sprite in self.sprites():
            if sprite.z == LAYERS['floor']:
                offset_pos = sprite.rect.topleft - self.offset
                self.screen.blit(sprite.image, offset_pos)

        for sprite in self.sprites():
            if sprite.z == LAYERS['main']:
                offset_pos = sprite.rect.topleft - self.offset
                self.screen.blit(sprite.image, offset_pos)