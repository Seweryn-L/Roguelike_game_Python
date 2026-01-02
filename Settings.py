
from typing import Tuple,Final
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


VICTORY_TEXT: Final[str] = "WYGRALES 5 z PJF"
GOLD_COLOR: Final[Tuple[int, int, int]] = (255, 215, 0)