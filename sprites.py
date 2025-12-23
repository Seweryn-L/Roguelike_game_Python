import pygame
from typing import List, Optional, Union, Sequence

from settings import *
from entity import Entity
from support import SpriteSheet


def get_input_direction(keys: pygame.key.ScancodeWrapper) -> pygame.math.Vector2:
    direction = pygame.math.Vector2(0, 0)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction.x = -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction.x = 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        direction.y = -1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        direction.y = 1

    if direction.length() > 0:
        return direction.normalize()
    return direction


class Tile(pygame.sprite.Sprite):
    def __init__(self, group: Union[pygame.sprite.Group, List], pos: Tuple[int, int], surface: pygame.Surface) -> None:
        if isinstance(group, list):
            super().__init__(*group)
        else:
            super().__init__(group)
        self.z = LAYERS['floor']
        self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)


class Wall(pygame.sprite.Sprite):
    def __init__(self, groups: Sequence[pygame.sprite.AbstractGroup], pos: Tuple[int, int], surface: pygame.Surface) -> None:
        super().__init__(*groups)
        self.z = LAYERS['main']
        self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group], pos: Tuple[int, int], text: str,
                 color: Tuple[int, int, int]) -> None:
        super().__init__(groups)
        try:
            font = pygame.font.Font(MAIN_FONT, 20)
        except FileNotFoundError:
            font = pygame.font.Font(None, 20)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, -60)
        self.timer: float = 0
        self.lifespan: int = 800
        self.z = LAYERS['main']

    def update(self, dt: float) -> None:
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.timer += dt * 1000
        if self.timer >= self.lifespan:
            self.kill()


class Player(Entity):
    def __init__(self, group: pygame.sprite.Group, obstacles: pygame.sprite.Group,
                 door_group: pygame.sprite.Group, chest_group: pygame.sprite.Group) -> None:
        super().__init__([group])

        self.door_group = door_group
        self.chest_group = chest_group
        self.display_group = group
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.z = LAYERS['main']

        self.obstacle_sprites = obstacles
        self.door_group = door_group

        self.hit: bool = False
        self.enemy_group: Optional[pygame.sprite.Group] = None
        self.can_shoot: bool = True
        self.shoot_time: int = 0
        self.shoot_cooldown: int = 400

        self.sprite_sheet = SpriteSheet(PLAYER_CHARACTER)
        self.base_body_img = self.sprite_sheet.get_image(*PLAYER_ASSETS['body'], scale=SCALE_FACTOR)
        self.weapon_img = self.sprite_sheet.get_image(*WEAPONS['short_sword'].id, scale=SCALE_FACTOR)
        self.armor_body_img = self.sprite_sheet.get_image(*ARMORS['Leather'].id, scale=SCALE_FACTOR)
        self.armor_head_img: Optional[pygame.Surface] = None
        self.armor_shield_img: Optional[pygame.Surface] = None

        self.weapon_hand: str = 'left'

        self.inventory: Dict[str, Optional[str]] = {
            'weapon': 'short_sword',
            'body': 'Leather',
            'head': None,
            'shield': None
        }
        self.ammo: Dict[str, int] = {'arrow': 0}
        self.owned_weapons: List[str] = ['short_sword']
        self.owned_armors: List[str] = ['Leather']

        self.can_switch_weapon: bool = True
        self.switch_weapon_time: int = 0
        self.switch_weapon_cooldown: int = 200

        self.rect = self.image.get_rect(center=PLAYER_START_POS)
        self.hitbox = self.rect.inflate(-10, -26)
        self.speed = 300
        self.pos = pygame.math.Vector2(PLAYER_START_POS)
        self.money: int = 10000
        self.stats: Dict[str, int] = {'health': 100, 'attack': 10, 'speed': 300}
        self.vulnerable: bool = True
        self.hurt_time: int = 0
        self.invincibility_duration: int = 500

        self.attack_sound = None
        try:
            self.attack_sound = pygame.mixer.Sound('audio/sword.wav')
            self.attack_sound.set_volume(0.3)
            self.pain_sound = pygame.mixer.Sound('audio/pain.wav')
            self.pain_sound.set_volume(0.3)
            self.arrow_sound = pygame.mixer.Sound('audio/arrow.mp3')
        except Exception as e:
            print(f"Brak dźwięku: {e}")

        self.weapon_offset: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self.update_weapon_graphics()
        self.setup_graphics()

    def input_attack(self) -> None:
        if not self.can_shoot:
            return

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        weapon_name = self.inventory['weapon']

        if mouse_pressed[0] and weapon_name == 'bow':
            if self.ammo['arrow'] > 0:
                self.ammo['arrow'] -= 1
                self.arrow_sound.play()
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

                mouse_pos_screen = pygame.mouse.get_pos()
                camera_offset = pygame.math.Vector2(0, 0)
                if hasattr(self.display_group, 'offset'):
                    camera_offset = self.display_group.offset
                mouse_pos_world = pygame.math.Vector2(mouse_pos_screen) + camera_offset

                direction_vector = mouse_pos_world - self.pos
                if direction_vector.length() > 0:
                    direction = direction_vector.normalize()
                    target_group = self.enemy_group if self.enemy_group else pygame.sprite.Group()
                    Projectile(self.rect.center, direction, [self.display_group], self.obstacle_sprites,
                               target_group,
                               PROJECTILES['arrow'])

        elif keys[pygame.K_SPACE]:
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

            interaction_area = self.hitbox.inflate(40, 40)

            doors_hit = [sprite for sprite in self.door_group if sprite.hitbox.colliderect(interaction_area)]
            if doors_hit:
                doors_hit[0].toggle()
                return

            chests_hit = [sprite for sprite in self.chest_group if sprite.hitbox.colliderect(interaction_area)]
            if chests_hit:
                chests_hit[0].open(self)
                return

        elif mouse_pressed[0] and weapon_name != 'bow':
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

            self.hit = True
            if self.attack_sound:
                self.attack_sound.play()

            if self.enemy_group:
                effective_range = self.get_effective_range()
                for enemy in self.enemy_group:
                    distance = enemy.pos.distance_to(self.pos)
                    if distance < effective_range:
                        enemy.get_damage(self)

    def set_enemy_group(self, enemy_group: pygame.sprite.Group) -> None:
        self.enemy_group = enemy_group

    def get_status(self) -> None:
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > self.shoot_cooldown:
                self.can_shoot = True

    def input_weapon_switch(self) -> None:
        keys = pygame.key.get_pressed()

        if not self.can_switch_weapon:
            current_time = pygame.time.get_ticks()
            if current_time - self.switch_weapon_time > self.switch_weapon_cooldown:
                self.can_switch_weapon = True
            else:
                return

        if not self.owned_weapons:
            return

        current_weapon = self.inventory['weapon']
        try:
            index = self.owned_weapons.index(current_weapon)
        except ValueError:
            index = 0

        changed = False

        if keys[pygame.K_q]:
            index = (index - 1) % len(self.owned_weapons)
            changed = True

        elif keys[pygame.K_e]:
            index = (index + 1) % len(self.owned_weapons)
            changed = True

        if changed:
            self.inventory['weapon'] = self.owned_weapons[index]
            self.update_weapon_graphics()

            self.can_switch_weapon = False
            self.switch_weapon_time = pygame.time.get_ticks()

    def input_hand_swap(self) -> None:
        keys = pygame.key.get_pressed()
        weapon_name = self.inventory['weapon']

        if not weapon_name:
            return
        weapon_data = WEAPONS[weapon_name]
        if weapon_data.rotates_to_mouse:
            return

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.weapon_hand == 'right':
                self.weapon_img = pygame.transform.flip(self.weapon_img, True, False)
                self.weapon_hand = 'left'

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.weapon_hand == 'left':
                self.weapon_img = pygame.transform.flip(self.weapon_img, True, False)
                self.weapon_hand = 'right'

    def get_effective_range(self) -> int:
        weapon_name = self.inventory['weapon']

        if not weapon_name or weapon_name == 'bow':
            return 0

        weapon_data = WEAPONS[weapon_name]
        return TILE_SIZE + (weapon_data.range * 16)

    def get_damage(self, amount: float) -> None:
        if self.vulnerable:
            total_def = self.get_total_armor()
            actual_damage = amount - total_def
            actual_damage = max(1, actual_damage)
            self.stats['health'] -= actual_damage
            if self.pain_sound:
                self.pain_sound.play()
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            FloatingText([self.display_group], self.rect.midtop, f"-{int(actual_damage)}", (255, 0, 0))

    def get_total_armor(self) -> int:
        total_def = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.inventory.get(slot)
            if item_name:
                total_def += ARMORS[item_name].defense
        return total_def

    def check_invincibility(self) -> None:
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time > self.invincibility_duration:
                self.vulnerable = True

    def get_full_weapon_damage(self) -> int:
        base_damage = self.stats['attack']
        weapon_name = self.inventory['weapon']
        if weapon_name:
            weapon_damage = WEAPONS[weapon_name].damage
            return base_damage + weapon_damage
        return base_damage

    def rotate_weapon(self, hand: str, hit: bool) -> Tuple[pygame.Surface, Tuple[int, int]]:
        rotate_vector = (0, 0)
        image = self.weapon_img

        weapon_name = self.inventory['weapon']
        if not weapon_name:
            return image, rotate_vector

        weapon_data = WEAPONS[weapon_name]

        if weapon_data.rotates_to_mouse:
            camera_offset = pygame.math.Vector2(0, 0)
            if hasattr(self.display_group, 'offset'):
                camera_offset = self.display_group.offset
            mouse_pos_world = pygame.math.Vector2(pygame.mouse.get_pos()) + camera_offset
            direction_vector = mouse_pos_world - self.pos

            if direction_vector.length() > 0:
                angle = direction_vector.angle_to(pygame.math.Vector2(1, 0))
            else:
                angle = 0

            image = pygame.transform.rotate(image, angle)
            rotate_vector = (0, 0)

        else:
            if hit:
                rotate_vector = (0, 0)
                image = pygame.transform.rotate(image, 90)
                image = pygame.transform.flip(image, False, True)
                if hand == 'right':
                    rotate_vector = (0, 27)
                    image = pygame.transform.flip(image, True, False)

        return image, rotate_vector

    def update_weapon_graphics(self) -> None:
        weapon_name = self.inventory['weapon']

        if weapon_name == 'bow':
            if self.inventory['shield'] is not None:
                self.inventory['shield'] = None
                self.update_armor_graphics()

        if weapon_name:
            weapon_data = WEAPONS[weapon_name]
            try:
                temp_sheet = SpriteSheet(weapon_data.graphic_path)
                self.weapon_img = temp_sheet.get_image(*weapon_data.id, scale=weapon_data.scale)
            except Exception as e:
                print(f"Error loading weapon: {e}")
                self.weapon_img = pygame.Surface((10, 10))
                self.weapon_img.fill('red')

            if weapon_data.flip_horizontal:
                self.weapon_img = pygame.transform.flip(self.weapon_img, True, False)

            self.weapon_hand = 'right'

            self.weapon_offset = pygame.math.Vector2(weapon_data.offset)
            self.setup_graphics()

    def update_armor_graphics(self) -> None:
        body_name = self.inventory['body']
        if body_name:
            self.armor_body_img = self.sprite_sheet.get_image(*ARMORS[body_name].id, scale=SCALE_FACTOR)
        else:
            self.armor_body_img = self.sprite_sheet.get_image(*ARMORS['Leather'].id, scale=SCALE_FACTOR)

        head_name = self.inventory['head']
        if head_name:
            self.armor_head_img = self.sprite_sheet.get_image(*ARMORS[head_name].id, scale=SCALE_FACTOR)
        else:
            self.armor_head_img = None

        shield_name = self.inventory['shield']
        if shield_name:
            self.armor_shield_img = pygame.transform.flip(self.sprite_sheet.get_image(*ARMORS[shield_name].id, scale=SCALE_FACTOR),True,False)
        else:
            self.armor_shield_img = None

        self.setup_graphics()

    def setup_graphics(self) -> None:
        self.image.fill((0, 0, 0, 0))
        rotate_image, rotate_vector = self.rotate_weapon(self.weapon_hand, self.hit)

        self.image.blit(self.base_body_img, (0, 0))
        if self.armor_body_img: self.image.blit(self.armor_body_img, (0, 0))
        if self.armor_head_img: self.image.blit(self.armor_head_img, (0, 0))

        if self.armor_shield_img:
            shield_surf = self.armor_shield_img
            if self.weapon_hand == 'right':
                shield_surf = pygame.transform.flip(shield_surf, True, False)
            self.image.blit(shield_surf, (0, 0))

        weapon_data = WEAPONS.get(self.inventory['weapon'])
        center_x = TILE_SIZE // 2
        center_y = TILE_SIZE // 2
        pivot_pos = pygame.math.Vector2(center_x, center_y) + self.weapon_offset

        if weapon_data and not weapon_data.rotates_to_mouse:
            if self.weapon_hand == 'left':
                pivot_pos.x = TILE_SIZE - pivot_pos.x

        weapon_rect = rotate_image.get_rect(center=(int(pivot_pos.x), int(pivot_pos.y)))
        weapon_rect.x += rotate_vector[0]
        weapon_rect.y += rotate_vector[1]

        self.image.blit(rotate_image, weapon_rect)

        if not self.vulnerable:
            tint_surf = pygame.Surface(self.image.get_size()).convert_alpha()
            tint_surf.fill((255, 0, 0, 0))
            self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def update(self, dt: float) -> None:
        self.get_status()
        self.check_invincibility()

        keys = pygame.key.get_pressed()
        direction = get_input_direction(keys)
        self.velocity = direction * self.speed
        self.move(dt)

        self.input_hand_swap()
        self.input_weapon_switch()
        self.input_attack()
        self.setup_graphics()


class Coin(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group], pos: Tuple[int, int]) -> None:
        super().__init__(groups)

        self.frames: List[pygame.Surface] = []
        self.frame_index: float = 0
        self.animation_speed: float = COIN_DATA['speed']

        try:
            ss = SpriteSheet(COIN_DATA['image'])
            sheet_w = ss.sheet.get_width()
            sheet_h = ss.sheet.get_height()

            cols = COIN_DATA['cols']
            frame_w = sheet_w // cols
            frame_h = sheet_h // 3
            scale = COIN_DATA['scale']

            for i in range(COIN_DATA['frames']):
                col = i % cols
                row = i // cols
                img = ss.get_image(col, row, frame_w, frame_h, scale)
                self.frames.append(img)

        except Exception as e:
            print(f"Error loading coin: {e}")
            self.image = pygame.Surface((20, 20))
            self.image.fill('yellow')

        if self.frames:
            self.image = self.frames[int(self.frame_index)]
        else:
            self.image = pygame.Surface((20, 20))

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.z = LAYERS['main']

    def update(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]


class Projectile(pygame.sprite.Sprite):
    def __init__(self,
                 pos: Tuple[int, int],
                 direction: pygame.math.Vector2,
                 groups: List[pygame.sprite.Group],
                 obstacles: pygame.sprite.Group,
                 damage_group: pygame.sprite.Group,
                 projectile_data: ProjectileData) -> None:
        super().__init__(groups)

        self.damage = projectile_data.damage
        self.speed = projectile_data.speed
        self.lifetime = projectile_data.lifetime
        self.start_time = pygame.time.get_ticks()
        self.obstacles = obstacles
        self.damage_group = damage_group
        self.arrow_hit = pygame.mixer.Sound('audio/arrow_hit.mp3')

        try:
            ss = SpriteSheet(projectile_data.image)
            original_image = ss.get_image(*projectile_data.id, scale=projectile_data.scale)

        except (FileNotFoundError, Exception) as e:
            print(f"Error loading projectile sprite: {e}")
            original_image = pygame.Surface((20, 5))
            original_image.fill((200, 200, 200))

        angle = direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(original_image, angle)

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)

        self.pos = pygame.math.Vector2(pos)
        self.direction = direction.normalize()
        self.z = LAYERS['main']

    def update(self, dt: float) -> None:
        self.pos += self.direction * self.speed * dt
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        self.rect.center = self.hitbox.center

        if pygame.sprite.spritecollide(self, self.obstacles, False):
            self.kill()

        hits = pygame.sprite.spritecollide(self, self.damage_group, False)
        for target in hits:
            if self.arrow_hit:
                self.arrow_hit.play()

            if isinstance(target, Player):
                target.get_damage(self.damage)
                self.kill()

            elif hasattr(target, 'health'):
                if getattr(target, 'vulnerable', True):
                    target.health -= self.damage
                    target.vulnerable = False
                    target.hit_time = pygame.time.get_ticks()

                    if hasattr(target, 'knockback_direction'):
                        target.knockback_direction = self.direction.normalize()

                    self.kill()


class Door(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group], pos: Tuple[int, int],
                 obstacles_group: pygame.sprite.Group, sprite_sheet: SpriteSheet,
                 door_sprites: pygame.sprite.Group, side: str) -> None:
        super().__init__(groups)

        self.door_sprites = door_sprites
        self.side = side

        config = DOOR_CONFIG.get(side)
        if config:
            self.closed_image = sprite_sheet.get_image(*config['closed'], scale=SCALE_FACTOR)
            self.open_image = sprite_sheet.get_image(*config['open'], scale=SCALE_FACTOR)
        else:
            self.closed_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.closed_image.fill('brown')
            self.open_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.open_image.fill('black')

        self.image = self.closed_image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.z = LAYERS['main']

        self.is_open = False
        self.obstacles_group = obstacles_group
        self.obstacles_group.add(self)

        try:
            self.open_sound = pygame.mixer.Sound('audio/door_open.mp3')
            self.open_sound.set_volume(0.3)
        except (FileNotFoundError, Exception):
            self.open_sound = None

    def toggle(self, from_neighbor: bool = False) -> None:
        if self.is_open:
            self.is_open = False
            self.image = self.closed_image
            self.obstacles_group.add(self)
        else:
            self.is_open = True
            self.image = self.open_image
            self.obstacles_group.remove(self)
            if self.open_sound and not from_neighbor:
                self.open_sound.play()

        if not from_neighbor:
            neighbor = self.find_neighbor()
            if neighbor:
                neighbor.toggle(from_neighbor=True)

    def find_neighbor(self):
        offset = 0
        if self.side == 'left':
            offset = TILE_SIZE
        elif self.side == 'right':
            offset = -TILE_SIZE

        if offset != 0:
            target_pos = (self.rect.x + offset, self.rect.y)
            for sprite in self.door_sprites:
                if sprite.rect.collidepoint(target_pos) and sprite != self:
                    return sprite
        return None


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group], pos: Tuple[int, int],
                 obstacles_group: pygame.sprite.Group, sprite_sheet: SpriteSheet) -> None:
        super().__init__(groups)

        self.closed_image = sprite_sheet.get_image(*CHEST_CONFIG['closed'], scale=SCALE_FACTOR)
        self.open_image = sprite_sheet.get_image(*CHEST_CONFIG['open'], scale=SCALE_FACTOR)

        self.image = self.closed_image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

        self.z = LAYERS['main']

        self.is_open = False
        self.amount = CHEST_CONFIG['amount']

        self.obstacles_group = obstacles_group
        self.obstacles_group.add(self)

    def open(self, player) -> None:
        if not self.is_open:
            self.is_open = True
            self.image = self.open_image

            player.money += self.amount

            FloatingText(self.groups(), self.rect.midtop, f"+{self.amount} Gold", (255, 215, 0))

            if hasattr(player, 'coin_sound') and player.coin_sound:
                player.coin_sound.play()