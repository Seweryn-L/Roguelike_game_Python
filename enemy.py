import pygame
from entity import Entity
from settings import *
from sprites import Coin


class Enemy(Entity):
    def __init__(self, groups, pos, obstacles, player, coin_group):
        super().__init__(groups)
        self.all_sprites_ref = groups[0]


        enemy_info = ENEMY_DATA['ghoul']
        try:
            full_image = pygame.image.load(enemy_info['image']).convert_alpha()
            self.image = pygame.transform.scale(full_image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill('red')

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)
        self.z = LAYERS['main']

        self.speed = enemy_info['speed']
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)

        self.obstacle_sprites = obstacles
        self.player = player
        self.notice_radius = enemy_info['notice_radius']

        self.health = enemy_info['health']
        self.max_health = self.health
        self.attack_damage = enemy_info['damage']
        self.attack_cooldown = enemy_info.get('attack_cooldown', 1000)
        self.last_attack_time = 0

        self.resistance = enemy_info['resistance']
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 400
        self.coin_group = coin_group

        self.knockback_direction = pygame.math.Vector2(0, 0)

    def apply_health_color(self):
        self.image = self.original_image.copy()
        if self.health < self.max_health:
            missing_hp_ratio = 1.0 - (self.health / self.max_health)
            tint_intensity = int(missing_hp_ratio * 255)
            tint_intensity = min(tint_intensity, 255)
            tint_surface = pygame.Surface(self.image.get_size()).convert_alpha()
            tint_surface.fill((tint_intensity, 0, 0, 0))
            self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def get_player_distance_direction(self):
        enemy_vec = self.pos
        player_vec = self.player.pos
        distance_vec = player_vec - enemy_vec
        distance = distance_vec.length()
        if distance > 0:
            direction = distance_vec.normalize()
        else:
            direction = pygame.math.Vector2()
        return distance, direction

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            damage = player.get_full_weapon_damage()
            self.health -= damage
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

            enemy_vec = self.pos
            player_vec = player.pos
            knockback_vec = enemy_vec - player_vec

            if knockback_vec.length() > 0:
                self.knockback_direction = knockback_vec.normalize()
            else:
                self.knockback_direction = pygame.math.Vector2(1, 0)

            if self.health <= 0:
                Coin([self.all_sprites_ref, self.coin_group], self.rect.center)
                self.kill()

    def check_hit_cooldown(self):
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time > self.invincibility_duration:
                self.vulnerable = True

    def check_attack_collision(self):
        attack_range_rect = self.hitbox.inflate(20, 20)
        if attack_range_rect.colliderect(self.player.hitbox):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.attack_cooldown:
                self.player.get_damage(self.attack_damage)
                self.last_attack_time = current_time

    def update(self, dt):
        self.check_hit_cooldown()
        self.apply_health_color()
        self.check_attack_collision()

        distance, direction = self.get_player_distance_direction()

        if not self.vulnerable:
            self.velocity = self.knockback_direction * self.speed
        elif distance < self.notice_radius:
            self.velocity = direction
        else:
            self.velocity = pygame.math.Vector2(0, 0)

        self.move(dt)