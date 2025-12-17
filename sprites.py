import pygame
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
    def __init__(self, group: pygame.sprite.Group | list, pos: tuple[int, int], surface: pygame.Surface) -> None:
        super().__init__(group)
        self.z = LAYERS['floor']
        self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)


class Wall(pygame.sprite.Sprite):
    def __init__(self, groups: pygame.sprite.Group | list, pos: tuple[int, int], surface: pygame.Surface) -> None:
        super().__init__(*groups)
        self.z = LAYERS['main']
        self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group] | pygame.sprite.Group, pos: tuple[int, int], text: str,
                 color: tuple[int, int, int] | str) -> None:
        super().__init__(groups)

        try:
            font = pygame.font.Font(MAIN_FONT, 20)
        except FileNotFoundError:
            font = pygame.font.Font(None, 20)

        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(midbottom=pos)

        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, -60)

        self.timer = 0
        self.lifespan = 800

        self.z = LAYERS['main']

    def update(self, dt: float) -> None:
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.timer += dt * 1000
        if self.timer >= self.lifespan:
            self.kill()


class Player(Entity):
    def __init__(self, group: pygame.sprite.Group, obstacles: pygame.sprite.Group) -> None:
        super().__init__(group)

        self.display_group = group

        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.z = LAYERS['main']

        self.obstacle_sprites = obstacles
        self.hit = False

        self.sprite_sheet = SpriteSheet(PLAYER_CHARACTER)
        self.base_body_img = self.sprite_sheet.get_image(*PLAYER_ASSETS['body'], scale=SCALE_FACTOR)
        self.weapon_img = self.sprite_sheet.get_image(*WEAPONS['short_sword']['id'], scale=SCALE_FACTOR)

        self.armor_body_img = self.sprite_sheet.get_image(*ARMORS['Leather']['id'], scale=SCALE_FACTOR)
        self.armor_head_img = None
        self.armor_shield_img = None

        self.weapon_hand = 'left'

        self.inventory = {
            'weapon': 'short_sword',
            'body': 'Leather',
            'head': None,
            'shield': None
        }

        self.owned_weapons = ['short_sword']
        self.owned_armors = ['Leather']

        self.rect = self.image.get_rect(center=PLAYER_START_POS)
        self.hitbox = self.rect.inflate(-10, -26)

        self.speed = 300
        self.pos = pygame.math.Vector2(PLAYER_START_POS)
        self.velocity = pygame.math.Vector2(0, 0)
        self.money = 10000

        self.stats = {'health': 100, 'attack': 10, 'speed': 300}

        self.vulnerable = True
        self.hurt_time = 0
        self.invincibility_duration = 500

        self.rotate_weapon(self.weapon_hand, self.hit)
        self.setup_graphics()

    def get_damage(self, amount: int | float) -> None:
        if self.vulnerable:
            total_def = self.get_total_armor()

            actual_damage = amount - total_def
            if actual_damage < 1:
                actual_damage = 1

            self.stats['health'] -= actual_damage
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()

            FloatingText(
                groups=[self.display_group],
                pos=self.rect.midtop,
                text=f"-{int(actual_damage)}",
                color=(255, 0, 0)
            )



    def get_total_armor(self) -> int:
        total_def = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.inventory.get(slot)
            if item_name:
                total_def += ARMORS[item_name]['defense']
        return total_def

    def check_invincibility(self) -> None:
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time > self.invincibility_duration:
                self.vulnerable = True

    def get_full_weapon_damage(self) -> int:
        base_damage = self.stats['attack']
        weapon_damage = WEAPONS[self.inventory['weapon']]['damage']
        return base_damage + weapon_damage

    def setup_graphics(self) -> None:
        self.image.fill((0, 0, 0, 0))
        rotate_image, rotate_vector = self.rotate_weapon(self.weapon_hand, self.hit)

        self.image.blit(self.base_body_img, (0, 0))
        if self.armor_body_img:
            self.image.blit(self.armor_body_img, (0, 0))
        if self.armor_head_img:
            self.image.blit(self.armor_head_img, (0, 0))
        self.image.blit(rotate_image, rotate_vector)
        if self.armor_shield_img:
            shield_surf = self.armor_shield_img
            if self.weapon_hand == 'right':
                shield_surf = pygame.transform.flip(shield_surf, True, False)
            self.image.blit(shield_surf, (0, 0))

        if not self.vulnerable:
            tint_surf = pygame.Surface(self.image.get_size()).convert_alpha()
            tint_surf.fill((255, 0, 0, 0))
            self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def rotate_weapon(self, hand: str, hit: bool) -> tuple[pygame.Surface, tuple[int, int]]:
        rotate_vector = (0, 0)
        if hand == 'left' and hit:
            rotate_vector = (0, 27)
            image = pygame.transform.rotate(self.weapon_img, 90)
            image = pygame.transform.flip(image, True, True)
            return image, rotate_vector
        elif hand == 'right' and hit:
            rotate_vector = (0, 27)
            image = pygame.transform.rotate(self.weapon_img, 90)
            return image, rotate_vector

        return self.weapon_img, rotate_vector

    def update_weapon_graphics(self) -> None:
        weapon_name = self.inventory['weapon']
        weapon_data = WEAPONS[weapon_name]
        sheet_coords = weapon_data['id']
        self.weapon_img = self.sprite_sheet.get_image(*sheet_coords, scale=SCALE_FACTOR)
        self.setup_graphics()

    def update_armor_graphics(self) -> None:
        body_name = self.inventory['body']
        if body_name:
            data = ARMORS[body_name]
            self.armor_body_img = self.sprite_sheet.get_image(*data['id'], scale=SCALE_FACTOR)
        else:
            self.armor_body_img = self.sprite_sheet.get_image(*ARMORS['Leather']['id'], scale=SCALE_FACTOR)

        head_name = self.inventory['head']
        if head_name:
            data = ARMORS[head_name]
            self.armor_head_img = self.sprite_sheet.get_image(*data['id'], scale=SCALE_FACTOR)
        else:
            self.armor_head_img = None

        shield_name = self.inventory['shield']
        if shield_name:
            data = ARMORS[shield_name]
            self.armor_shield_img = self.sprite_sheet.get_image(*data['id'], scale=SCALE_FACTOR)
        else:
            self.armor_shield_img = None

        self.setup_graphics()

    def update(self, dt: float) -> None:
        self.check_invincibility()
        keys = pygame.key.get_pressed()
        direction = get_input_direction(keys)
        self.velocity = direction * self.speed
        self.move(dt)
        self.setup_graphics()


class Coin(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group] | pygame.sprite.Group, pos: tuple[int, int]) -> None:
        super().__init__(groups)

        self.frames: list[pygame.Surface] = []
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