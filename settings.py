from dataclasses import dataclass
from typing import Tuple, Dict, Final

WIDTH: Final[int] = 1280
HEIGHT: Final[int] = 720
FPS: Final[int] = 60
TITLE: Final[str] = "Knight vs Sceletors"
DEFAULT_MAP: Final[str] = "level2.tmx"

MAIN_FONT: Final[str] = 'fonts/Ac437_IBM_BIOS.ttf'
PLAYER_CHARACTER: Final[str] = "sprites/character/Spritesheet/roguelikeChar_transparent.png"

DOOR_CONFIG = {
    'left': {
        'open': (28, 8),
        'closed': (28, 7)
    },
    'right': {
        'open': (29, 8),
        'closed': (29, 7)
    }
}

BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
DARK_GREY: Final[Tuple[int, int, int]] = (40, 40, 40)

ORIGINAL_TILE_SIZE: Final[int] = 16
SCALE_FACTOR: Final[int] = 3
TILE_SIZE: Final[int] = ORIGINAL_TILE_SIZE * SCALE_FACTOR

MAP_WIDTH: int = 4000
MAP_HEIGHT: int = 4000

PLAYER_START_POS: Tuple[int, int] = (400, 400)

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
    'short_sword': WeaponData('short sword', 1, 100, 1, (45, 7)),
    'axe': WeaponData('axe', 2, 200, 1, (48, 7)),
    'long_sword': WeaponData('long sword', 5, 500, 2, (45, 6)),
    'pique': WeaponData('pique', 5, 1000, 3, (47, 5)),
    'bow' : WeaponData('bow',20,1000,-1,(0,0 ),"sprites/Bow and Arrows.png", scale=2, offset=(8,8),rotates_to_mouse=True)
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
    'Leather': ArmorData('Leather Armor', 5, 0, 'body', (6, 0)),
    'steel': ArmorData('Steel Armor', 10, 300, 'body', (12, 4)),
    'helmet': ArmorData('Helmet', 5, 600, 'head', (30, 0)),
    'shield': ArmorData('Shield', 15, 1500, 'shield', (40, 0))
}

ENEMY_DATA: Dict[str, EnemyData] = {
    'ghoul': EnemyData(100, 20, 'slash', 150, 3, 60, 400, 1000, 'sprites/SandGhoul.gif'),
    'skeleton': EnemyData(
        health=50,
        damage=10,
        attack_type='projectile',
        speed=100,
        resistance=1,
        attack_radius=250,
        notice_radius=500,
        attack_cooldown=2000,
        image='sprites/BrittleArcher.gif',
        projectile_type='arrow'
    ),
    'ghastlyEye': EnemyData(
        health=20,
        damage=5,
        attack_type='projectile',
        speed=150,
        resistance=1,
        attack_radius=250,
        notice_radius=700,
        attack_cooldown=1000,
        image='sprites/GhastlyEye.gif',
        projectile_type='venom'
    )
}

LAYERS = {
    'floor': 0,
    'main': 1,
    'overhead_always': 2,
    'doors': 3
}

CHEST_CONFIG = {
    'closed': (38, 10),
    'open': (38, 11),
    'amount': 500
}

COIN_DATA = {'amount': 100, 'image': 'sprites/coin.png', 'frames': 7, 'cols': 3, 'scale': 2, 'speed': 6}
PLAYER_ASSETS = {'body': (0, 0)}
