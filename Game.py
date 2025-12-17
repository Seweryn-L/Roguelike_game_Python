import random
import sys
import pytmx
import pygame
from settings import *
from Camera import Camera
from ui import UpgradeMenu
from enemy import Enemy
from hud import HUD
from sprites import Player, Wall, Tile, FloatingText


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        self.font_big: pygame.font.Font
        self.font_small: pygame.font.Font
        try:
            self.font_big = pygame.font.Font('fonts/Ac437_IBM_BIOS.ttf', 90)
            self.font_small = pygame.font.Font('fonts/Ac437_IBM_BIOS.ttf', 30)
        except FileNotFoundError:
            self.font_big = pygame.font.Font(None, 100)
            self.font_small = pygame.font.Font(None, 40)

        self.all_sprites: Camera = None
        self.wall_sprites: pygame.sprite.Group = None
        self.enemy_sprites: pygame.sprite.Group = None
        self.coin_sprites: pygame.sprite.Group = None
        self.player_obstacles: pygame.sprite.Group = None
        self.enemy_obstacles: pygame.sprite.Group = None

        self.player: Player = None
        self.upgrade_menu: UpgradeMenu = None
        self.hud: HUD = None

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

        self.player = Player(self.all_sprites, self.player_obstacles)
        self.enemy_obstacles.add(self.player)

        self.create_map_tmx()

        self.upgrade_menu = UpgradeMenu(self.player)
        self.hud = HUD(self.player)

    def create_map_tmx(self) -> None:

        map_name = 'level1.tmx' if 'MAP1' not in globals() else MAP1

        try:
            tmx_data = pytmx.util_pygame.load_pygame(map_name)
        except FileNotFoundError:
            sys.exit()

        map_pixel_width = tmx_data.width * TILE_SIZE
        map_pixel_height = tmx_data.height * TILE_SIZE


        self.all_sprites.set_limits(map_pixel_width, map_pixel_height)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * TILE_SIZE, y * TILE_SIZE)

                    if layer.name == 'Walls':

                        wall = Wall([self.all_sprites, self.wall_sprites], pos, surf)
                        self.player_obstacles.add(wall)
                        self.enemy_obstacles.add(wall)

                    elif layer.name == 'Floor':
                        Tile(self.all_sprites, pos, surf)

                        if random.randint(0, 100) < 2:
                            dist_x = abs(x * TILE_SIZE - WIDTH / 2)
                            dist_y = abs(y * TILE_SIZE - HEIGHT / 2)

                            if dist_x > 500 or dist_y > 500:
                                Enemy(
                                    groups=[self.all_sprites, self.enemy_sprites],
                                    pos=pos,
                                    obstacles=self.enemy_obstacles,
                                    player=self.player,
                                    coin_group=self.coin_sprites
                                )

    def player_attack_logic(self) -> None:
        if self.enemy_sprites:
            for sprite in self.enemy_sprites:

                enemy: Enemy = sprite

                distance = enemy.pos.distance_to(self.player.pos)
                if distance < 80:
                    enemy.get_damage(self.player, 'weapon')

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(FPS) / 1000
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

                if self.game_over:

                    if event.key == pygame.K_SPACE:
                        self.new_game()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    return

                if event.key == pygame.K_LEFT:
                    if self.player.weapon_hand == 'left':
                        self.player.weapon_img = pygame.transform.flip(self.player.weapon_img, True, False)
                        self.player.weapon_hand = 'right'

                if event.key == pygame.K_RIGHT:
                    if self.player.weapon_hand == 'right':
                        self.player.weapon_img = pygame.transform.flip(self.player.weapon_img, True, False)
                        self.player.weapon_hand = 'left'

                if event.key == pygame.K_SPACE:
                    self.player.hit = True
                    self.player_attack_logic()

                if event.key == pygame.K_ESCAPE:
                    self.game_paused = not self.game_paused

            if event.type == pygame.KEYUP:
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.player.hit = False

    def update(self, dt: float) -> None:
        self.all_sprites.update(dt)

        collected_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)

        for coin in collected_coins:
            amount = COIN_DATA['amount']
            self.player.money += amount


            FloatingText(
                groups=[self.all_sprites],
                pos=self.player.rect.midtop,
                text=f"+{amount}",
                color=(255, 215, 0)
            )

            print(f"Podniesiono monetę! Złoto: {self.player.money}")

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

        restart_surf = self.font_small.render("Wcisnij SPACJE aby sprobowac ponownie", True, (255, 255, 255))
        restart_rect = restart_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))

        self.screen.blit(game_over_surf, game_over_rect)
        self.screen.blit(restart_surf, restart_rect)

        pygame.display.flip()