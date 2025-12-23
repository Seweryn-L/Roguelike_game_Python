import pygame
from typing import List, Any

from entity import Entity
from settings import *


from sprites import Coin, Player, Projectile


class Enemy(Entity):


    def __init__(self, groups: List[pygame.sprite.Group], pos: Tuple[int, int],
                 obstacles: pygame.sprite.Group, player: Any, coin_group: pygame.sprite.Group,
                 enemy_name: str) -> None:
        super().__init__(groups)

        self.all_sprites_ref = groups[0]

        enemy_info = ENEMY_DATA.get(enemy_name, ENEMY_DATA['ghoul'])

        try:
            full_image = pygame.image.load(enemy_info.image).convert_alpha()
            self.image = pygame.transform.scale(full_image, (TILE_SIZE, TILE_SIZE))
            self.death_sound = pygame.mixer.Sound('audio/kill.wav')

        except (FileNotFoundError, pygame.error) as e:
            print(f"Error ({enemy_name}): {e}")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill('red')

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)
        self.z = LAYERS['main']
        self.czy_pierwszy_raz = True
        self.zombie_sound = pygame.mixer.Sound('audio/zombie.wav')
        self.zombie_sound.set_volume(0.01)

        self.speed = enemy_info.speed
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)

        self.obstacle_sprites = obstacles
        self.player = player

        self.health = enemy_info.health
        self.max_health = self.health
        self.attack_damage = enemy_info.damage
        self.attack_type = enemy_info.attack_type
        self.projectile_type = getattr(enemy_info, 'projectile_type', 'None')

        self.attack_radius = enemy_info.attack_radius
        self.notice_radius = enemy_info.notice_radius
        self.attack_cooldown = enemy_info.attack_cooldown

        self.last_attack_time = 0
        self.resistance = enemy_info.resistance

        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 400

        self.coin_group = coin_group
        self.knockback_direction = pygame.math.Vector2(0, 0)

    def apply_health_color(self) -> None:
        self.image = self.original_image.copy()
        if self.health < self.max_health:
            current_health = max(0, self.health)
            missing_hp_ratio = 1.0 - (current_health / self.max_health)

            tint_intensity = int(missing_hp_ratio * 255)
            tint_intensity = min(max(tint_intensity, 0), 255)

            tint_surface = pygame.Surface(self.image.get_size()).convert_alpha()
            tint_surface.fill((tint_intensity, 0, 0, 0))
            self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def get_player_distance_direction(self) -> Tuple[float, pygame.math.Vector2]:
        enemy_vec = self.pos
        player_vec = self.player.pos
        distance_vec = player_vec - enemy_vec
        distance = distance_vec.length()

        if distance > 0:
            direction = distance_vec.normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def get_damage(self, player: Player) -> None:
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

    def check_death(self) -> None:
        if self.health <= 0:
            if self.death_sound:
                self.death_sound.play()
            Coin([self.all_sprites_ref, self.coin_group], self.rect.center)
            self.kill()

    def check_hit_cooldown(self) -> None:
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time > self.invincibility_duration:
                self.vulnerable = True

    def attack_behavior(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        if self.attack_type == 'projectile':
            self.last_attack_time = current_time

            _, direction = self.get_player_distance_direction()

            if self.projectile_type in PROJECTILES:
                target_group = pygame.sprite.Group()
                target_group.add(self.player)

                Projectile(
                    pos=self.rect.center,
                    direction=direction,
                    groups=[self.all_sprites_ref],
                    obstacles=self.obstacle_sprites,
                    damage_group=target_group,
                    projectile_data=PROJECTILES[self.projectile_type]
                )

    def check_attack_collision(self) -> None:
        attack_range_rect = self.hitbox.inflate(20, 20)

        if attack_range_rect.colliderect(self.player.hitbox):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.attack_cooldown:
                self.player.get_damage(self.attack_damage)
                self.last_attack_time = current_time

    def check_line_of_sight(self) -> bool:
        if not self.obstacle_sprites:
            return True

        enemy_center = self.rect.center
        player_center = self.player.rect.center

        for obstacle in self.obstacle_sprites:
            if obstacle is self.player:
                continue

            if obstacle.rect.clipline(enemy_center, player_center):
                return False

        return True

    def update(self, dt: float) -> None:
        self.check_death()
        self.check_hit_cooldown()
        self.apply_health_color()

        if self.attack_type != 'projectile':
            self.check_attack_collision()

        distance, direction = self.get_player_distance_direction()

        if not self.vulnerable:
            self.velocity = self.knockback_direction * self.speed

            if self.obstacle_sprites and self.player in self.obstacle_sprites:
                self.obstacle_sprites.remove(self.player)
                self.move(dt)
                self.obstacle_sprites.add(self.player)
            else:
                self.move(dt)

        elif distance < self.notice_radius and self.check_line_of_sight():
            if self.attack_type == 'projectile' and distance < self.attack_radius:
                self.velocity = pygame.math.Vector2(0, 0)
                self.attack_behavior()
            else:
                self.velocity = direction * self.speed

            self.move(dt)

        else:
            self.velocity = pygame.math.Vector2(0, 0)
            self.move(dt)
