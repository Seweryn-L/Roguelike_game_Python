import random
import sys
import pytmx
import pygame
from typing import Optional, Callable

from settings import *
from support import load_font, SpriteSheet
from Camera import Camera
from ui import UpgradeMenu
from enemy import Enemy
from hud import HUD
from sprites import Player, Wall, Tile, FloatingText, Door, Chest


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        self.font_big: pygame.font.Font = load_font(MAIN_FONT, 90)
        self.font_small: pygame.font.Font = load_font(MAIN_FONT, 30)
        try:
            pygame.mixer.music.load('audio/Dungeon.wav')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

            print("Muzyka wystartowała!")
        except Exception as e:
            print(f"Nie udało się załadować muzyki: {e}")

        self.coin_sound = None
        try:
            self.coin_sound = pygame.mixer.Sound('audio/coins.wav')
            self.coin_sound.set_volume(0.4)
        except Exception as e:
            print(f"Nie udało się załadować dźwięku monety: {e}")

        self.all_sprites: Optional[Camera] = None
        self.wall_sprites: Optional[pygame.sprite.Group] = None
        self.enemy_sprites: Optional[pygame.sprite.Group] = None
        self.coin_sprites: Optional[pygame.sprite.Group] = None
        self.player_obstacles: Optional[pygame.sprite.Group] = None
        self.enemy_obstacles: Optional[pygame.sprite.Group] = None

        self.player: Optional[Player] = None
        self.upgrade_menu: Optional[UpgradeMenu] = None
        self.hud: Optional[HUD] = None
        self.door_sprites: Optional[pygame.sprite.Group] = None
        self.chest_sprites: Optional[pygame.sprite.Group] = None

        self.game_paused: bool = False
        self.game_over: bool = False

        self.new_game()

    def new_game(self) -> None:
        self.game_over = False
        self.game_paused = False

        self.all_sprites = Camera()
        self.wall_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        self.player_obstacles = pygame.sprite.Group()
        self.enemy_obstacles = pygame.sprite.Group()

        self.door_sprites = pygame.sprite.Group()
        self.chest_sprites = pygame.sprite.Group()

        self.player = Player(self.all_sprites, self.player_obstacles, self.door_sprites, self.chest_sprites)

        self.enemy_obstacles.add(self.player)

        self.create_map_tmx()
        self.player.set_enemy_group(self.enemy_sprites)

        self.upgrade_menu = UpgradeMenu(self.player)
        self.hud = HUD(self.player)

    def _create_floor(self, pos: Tuple[int, int], surf: pygame.Surface, x: int, y: int) -> None:
        Tile(self.all_sprites, pos, surf)
        self.spawn_enemies_randomly(x, y, pos)

    def _create_wall_main(self, pos: Tuple[int, int], surf: pygame.Surface, x: int, y: int) -> None:
        wall = Wall([self.all_sprites, self.wall_sprites], pos, surf)
        wall.z = LAYERS['main']
        self.player_obstacles.add(wall)
        self.enemy_obstacles.add(wall)

    def _create_overhead(self, pos: Tuple[int, int], surf: pygame.Surface, x: int, y: int) -> None:
        wall = Wall([self.all_sprites, self.wall_sprites], pos, surf)
        wall.z = LAYERS['main']
        self.enemy_obstacles.add(wall)

    def _create_overhead_always(self, pos: Tuple[int, int], surf: pygame.Surface, x: int, y: int) -> None:
        wall = Wall([self.all_sprites, self.wall_sprites], pos, surf)
        wall.z = LAYERS['overhead_always']
        self.enemy_obstacles.add(wall)


    def _create_door(self, obj: pytmx.TiledObject, pos: Tuple[int, int], spritesheet: SpriteSheet) -> None:
        Door(
            groups=[self.all_sprites, self.door_sprites],
            pos=pos,
            obstacles_group=self.player_obstacles,
            sprite_sheet=spritesheet,
            door_sprites=self.door_sprites,
            side=obj.name
        )

    def _create_chest(self, obj: pytmx.TiledObject, pos: Tuple[int, int], spritesheet: SpriteSheet) -> None:
        Chest(
            groups=[self.all_sprites, self.chest_sprites],
            pos=pos,
            obstacles_group=self.player_obstacles,
            sprite_sheet=spritesheet
        )


    def create_map_tmx(self) -> None:
        map_name: str = DEFAULT_MAP
        try:
            tmx_data: pytmx.TiledMap = pytmx.util_pygame.load_pygame(map_name)
        except FileNotFoundError:
            print(f"CRITICAL ERROR: Map {map_name} not found!")
            sys.exit()

        map_pixel_width: int = tmx_data.width * TILE_SIZE
        map_pixel_height: int = tmx_data.height * TILE_SIZE
        self.all_sprites.set_limits(map_pixel_width, map_pixel_height)

        map_spritesheet: SpriteSheet = SpriteSheet("rpg pack/Spritesheet/roguelikeSheet_transparent.png")

        tile_handler = Callable[[Tuple[int, int], pygame.Surface, int, int], None]
        object_handler = Callable[[pytmx.TiledObject, Tuple[int, int], SpriteSheet], None]

        tile_layer_handlers: Dict[str, tile_handler] = {
            'Floor': self._create_floor,
            'Walls': self._create_wall_main,
            'Overhead': self._create_overhead,
            'Overhead_Always': self._create_overhead_always
        }

        object_handlers: Dict[str, object_handler] = {
            'left': self._create_door,
            'right': self._create_door,
            'chest': self._create_chest
        }

        for layer in tmx_data.visible_layers:
            # --- Obsługa Warstw Kafelkowych ---
            if isinstance(layer, pytmx.TiledTileLayer) and hasattr(layer, 'tiles'):
                handler = tile_layer_handlers.get(layer.name)

                if handler:
                    for x, y, surf in layer.tiles():
                        pos = (x * TILE_SIZE, y * TILE_SIZE)
                        handler(pos, surf, x, y)

            # --- Obsługa Warstw Obiektów ---
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    # Obliczenia siatki
                    grid_x: int = round(obj.x / ORIGINAL_TILE_SIZE)
                    grid_y: int = round(obj.y / ORIGINAL_TILE_SIZE)
                    pos: Tuple[int, int] = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)

                    handler = object_handlers.get(obj.name)

                    if handler:
                        handler(obj, pos, map_spritesheet)
    def spawn_enemies_randomly(self, grid_x: int, grid_y: int, pos: tuple[int,int]) -> None:
        if random.randint(0, 100) < 2:
            dist_x = abs(grid_x * TILE_SIZE - WIDTH / 2)
            dist_y = abs(grid_y * TILE_SIZE - HEIGHT / 2)

            if dist_x > 500 or dist_y > 500:
                available_enemies = list(ENEMY_DATA.keys())
                enemy_name = random.choice(available_enemies)

                Enemy(
                    groups=[self.all_sprites, self.enemy_sprites, self.player_obstacles],
                    pos=pos,
                    obstacles=self.enemy_obstacles,
                    player=self.player,
                    coin_group=self.coin_sprites,
                    enemy_name=enemy_name
                )

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(FPS) / 1000.0
            self.events()

            if self.game_over:
                self.draw_game_over_screen()
            elif self.game_paused:
                self.upgrade_menu.display()
                self.upgrade_menu.input()
                if self.upgrade_menu.should_close:
                    self.game_paused = False
                    self.upgrade_menu.should_close = False
                    self.upgrade_menu.state = 'main'
                    self.upgrade_menu.selection_index = 0
                pygame.display.flip()
            else:
                self.update(dt)
                self.draw()

    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not self.game_paused:
                    self.handle_keydown(event)

            if event.type == pygame.KEYUP:
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.player.hit = False

            if event.type == pygame.MOUSEBUTTONUP:
                if not self.game_over:
                    if event.button == 1:
                        self.player.hit = False

    def handle_keydown(self, event: pygame.event.Event) -> None:
        if self.game_over:
            if event.key == pygame.K_ESCAPE:
                self.new_game()
            return

        if event.key == pygame.K_ESCAPE:
            if not self.game_paused:
                self.game_paused = True
                self.upgrade_menu.reset()

    def update(self, dt: float) -> None:
        self.all_sprites.update(dt)

        collected_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
        for coin in collected_coins:
            amount = COIN_DATA['amount']
            if self.coin_sound:
                self.coin_sound.play()
            self.player.money += amount
            FloatingText([self.all_sprites], self.player.rect.midtop, f"+{amount}", (255, 215, 0))

        if self.player.stats['health'] <= 0:
            self.game_over = True

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.all_sprites.custom_draw(self.player)
        self.hud.display()
        pygame.display.flip()

    def draw_game_over_screen(self) -> None:
        self.screen.fill(BLACK)
        game_over_surf = self.font_big.render("GAME OVER", True, (180, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        restart_surf = self.font_small.render("Press ESC to restart", True, (255, 255, 255))
        restart_rect = restart_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        self.screen.blit(game_over_surf, game_over_rect)
        self.screen.blit(restart_surf, restart_rect)
        pygame.display.flip()
