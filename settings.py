import pygame
from dataclasses import dataclass
from typing import Tuple, Dict, Final
from enum import IntEnum

WIDTH: Final[int] = 1280
HEIGHT: Final[int] = 720
FPS: Final[int] = 60
TITLE: Final[str] = "Knight vs Sceletors"
DEFAULT_MAP: Final[str] = "level2.tmx"

BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
MAIN_FONT: Final[str] = 'fonts/Ac437_IBM_BIOS.ttf'

ORIGINAL_TILE_SIZE: Final[int] = 16
SCALE_FACTOR: Final[int] = 3
TILE_SIZE: Final[int] = ORIGINAL_TILE_SIZE * SCALE_FACTOR

MAP_WIDTH: Final[int] = 4000
MAP_HEIGHT: Final[int] = 4000


class Layer(IntEnum):
    FLOOR = 0
    MAIN = 1
    OVERHEAD_ALWAYS = 2
    DOORS = 3

LAYERS = {
    'floor': Layer.FLOOR,
    'main': Layer.MAIN,
    'overhead_always': Layer.OVERHEAD_ALWAYS,
    'doors': Layer.DOORS
}

PLAYER_START_POS: Tuple[int, int] = (400, 400)
PLAYER_CHARACTER: Final[str] = "sprites/character/Spritesheet/roguelikeChar_transparent.png"
PLAYER_ASSETS = {'body': (0, 0)}

ARROW_COST: int = 50
ARROW_BUNDLE: int = 10
BOW_INITIAL_ARROWS: int = 20



@dataclass(frozen=True)
class WeaponData:
    name: str
    damage: int
    cost: int
    range: int
    id: Tuple[int, int]
    graphic_path: str = PLAYER_CHARACTER
    flip_horizontal: bool = False
    scale: float = SCALE_FACTOR
    offset: Tuple[int, int] = (0, 0)
    rotates_to_mouse: bool = False

@dataclass(frozen=True)
class ArmorData:
    name: str
    defense: int
    cost: int
    slot: str
    id: Tuple[int, int]
    graphic_path: str = PLAYER_CHARACTER

@dataclass(frozen=True)
class EnemyData:
    health: int
    damage: int
    attack_type: str
    speed: int
    resistance: int
    attack_radius: int
    notice_radius: int
    attack_cooldown: int
    image: str
    gold_drop: int
    projectile_type: str = 'None'

@dataclass(frozen=True)
class ProjectileData:
    damage: int
    speed: int
    image: str
    id: Tuple[int, int]
    lifetime: int
    scale: float = SCALE_FACTOR


WEAPONS: Dict[str, WeaponData] = {
    'short_sword': WeaponData('short sword', 1, 0, 1, (45, 7)),
    'axe': WeaponData('axe', 3, 250, 1, (48, 7)),
    'long_sword': WeaponData('long sword', 6, 600, 2, (45, 6)),
    'pique': WeaponData('pique', 5, 1200, 3, (47, 5)),
    'bow': WeaponData(
        name='bow', damage=12, cost=1500, range=-1,
        id=(0, 0), graphic_path="sprites/Bow and Arrows.png",
        scale=2, offset=(8, 8), rotates_to_mouse=True
    )
}

PROJECTILES: Dict[str, ProjectileData] = {
    'arrow': ProjectileData(
        damage=15,
        speed=600,
        image="sprites/Bow and Arrows.png",
        id=(2, 1),
        lifetime=3000,
        scale=1.5,
    ),
    'venom': ProjectileData(
        damage=10,
        speed=400,
        image="sprites/venom_red.png",
        id=(0, 0),
        lifetime=3000,
        scale=1.5,
    )
}

ARMORS: Dict[str, ArmorData] = {
    'Leather': ArmorData('Leather Armor', 3, 150, 'body', (6, 0)),
    'steel': ArmorData('Steel Armor', 8, 800, 'body', (12, 4)),
    'helmet': ArmorData('Helmet', 3, 400, 'head', (30, 0)),
    'shield': ArmorData('Shield', 10, 1000, 'shield', (40, 0))
}

ENEMY_DATA: Dict[str, EnemyData] = {
    'ghoul': EnemyData(
        health=100, damage=15, attack_type='slash', speed=160, resistance=3,
        attack_radius=60, notice_radius=400, attack_cooldown=1000,
        image='sprites/SandGhoul.gif',
        gold_drop=40,
        projectile_type='None'
    ),
    'skeleton': EnemyData(
        health=60, damage=10, attack_type='projectile', speed=110, resistance=1,
        attack_radius=250, notice_radius=550, attack_cooldown=2000,
        image='sprites/BrittleArcher.gif',
        gold_drop=50,
        projectile_type='arrow'
    ),
    'ghastlyEye': EnemyData(
        health=30, damage=5, attack_type='projectile', speed=140, resistance=1,
        attack_radius=250, notice_radius=700, attack_cooldown=1000,
        image='sprites/GhastlyEye.gif',
        gold_drop=30,
        projectile_type='venom'
    )
}

DOOR_CONFIG = {
    'left': {'open': (28, 8), 'closed': (28, 7)},
    'right': {'open': (29, 8), 'closed': (29, 7)}
}

CHEST_CONFIG = {
    'closed': (38, 10),
    'open': (38, 11),
    'amount': 200
}

COIN_DATA = {
    'amount': 100, 
    'image': 'sprites/coin.png', 
    'frames': 7, 
    'cols': 3, 
    'scale': 2, 
    'speed': 6
}

VICTORY_TEXT: Final[str] = "WYGRALES 5 z PJF"
GOLD_COLOR: Final[Tuple[int, int, int]] = (255, 215, 0)