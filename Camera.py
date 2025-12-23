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

        if self.offset.x < 0: self.offset.x = 0
        if self.offset.y < 0: self.offset.y = 0

        right_limit = max(self.map_width - WIDTH, 0)
        if self.offset.x > right_limit:
            self.offset.x = right_limit

        bottom_limit = max(self.map_height - HEIGHT, 0)
        if self.offset.y > bottom_limit:
            self.offset.y = bottom_limit

        for sprite in self.sprites():
            if sprite.z == LAYERS['floor']:
                offset_pos = sprite.rect.topleft - self.offset
                if -TILE_SIZE < offset_pos.x < WIDTH and -TILE_SIZE < offset_pos.y < HEIGHT:
                    self.screen.blit(sprite.image, offset_pos)

        main_sprites = [s for s in self.sprites() if s.z == LAYERS['main']]
        main_sprites.sort(key=lambda s: s.rect.bottom)

        for sprite in main_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            if -TILE_SIZE < offset_pos.x < WIDTH and -TILE_SIZE < offset_pos.y < HEIGHT:
                self.screen.blit(sprite.image, offset_pos)

        for sprite in self.sprites():
            if sprite.z == LAYERS['overhead_always']:
                offset_pos = sprite.rect.topleft - self.offset
                if -TILE_SIZE < offset_pos.x < WIDTH and -TILE_SIZE < offset_pos.y < HEIGHT:
                    self.screen.blit(sprite.image, offset_pos)

        for sprite in self.sprites():
            if sprite.z == LAYERS['doors']:
                offset_pos = sprite.rect.topleft - self.offset
                if -TILE_SIZE < offset_pos.x < WIDTH and -TILE_SIZE < offset_pos.y < HEIGHT:
                    self.screen.blit(sprite.image, offset_pos)

        if player.hit:
            attack_range = player.get_effective_range()
            if attack_range > 0:
                circle_surf = pygame.Surface((attack_range * 2 + 4, attack_range * 2 + 4), pygame.SRCALPHA)
                center = (attack_range + 2, attack_range + 2)
                pygame.draw.circle(circle_surf, (255, 255, 255, 80), center, attack_range, 1)

                draw_pos = player.rect.center - self.offset
                draw_pos.x -= (attack_range + 2)
                draw_pos.y -= (attack_range + 2)

                self.screen.blit(circle_surf, draw_pos)