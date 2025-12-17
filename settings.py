WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Knight vs Sceletors"
MAP1 = "level1.tmx"

MAIN_FONT = 'fonts/Ac437_IBM_BIOS.ttf'
PLAYER_CHARACTER = "sprites/character/Spritesheet/roguelikeChar_transparent.png"
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)

ORIGINAL_TILE_SIZE = 16
SCALE_FACTOR = 3
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR

MAP_WIDTH = 4000
MAP_HEIGHT = 4000

PLAYER_START_POS = (400, 400)
PLAYER_SIZE = 16

HAND_POS = {
    'left': (0, 0),
    'right': (32, 0),
}

PLAYER_ASSETS = {
    'body': (0, 0)
}
LAYERS = {
    'floor': 0,
    'main': 1
}

WEAPONS = {
    'short_sword': {
        'name': 'short sword',
        'damage': 1,
        'cost': 100,
        'range': 1,
        'id': (45, 7)
    },
    'axe': {
        'name': 'axe',
        'damage': 2,
        'range': 1,
        'cost': 200,
        'id': (48, 7)
    },
    'long_sword': {
        'name': 'long sword',
        'damage': 5,
        'range': 1,
        'cost': 500,
        'id': (45, 6)
    },
    'pique': {
        'name': 'pique',
        'damage': 5,
        'range': 2,
        'cost': 1000,
        'id': (47, 5)
    }

}

ARMORS = {
    'Leather': {
        'name': 'Leather Armor',
        'defense': 5,
        'cost': 0,
        'slot': 'body',
        'id': (6, 0)
    },
    'steel': {
        'name': 'Steel Armor',
        'defense': 10,
        'cost': 300,
        'slot': 'body',
        'id': (12, 4)
    },
    'helmet': {
        'name': 'Helmet',
        'defense': 5,
        'cost': 600,
        'slot': 'head',
        'id': (30, 0)
    },
    'shield': {
        'name': 'Shield',
        'defense': 15,
        'cost': 1500,
        'slot': 'shield',
        'id': (40, 0)
    }
}

COIN_DATA = {
    'amount': 100,
    'image': 'sprites/coin.png',
    'frames': 7,
    'cols': 3,
    'scale': 2,
    'speed': 6
}

ENEMY_DATA = {
    'ghoul': {
        'health': 100,
        'damage': 20,
        'attack_type': 'slash',
        'speed': 150,
        'resistance': 3,
        'attack_radius': 60,
        'notice_radius': 400,
        'attack_cooldown': 1000,
        'image': 'sprites/SandGhoul.gif',
    },

    'skeleton': {
        'health': 60,
        'damage': 10,
        'attack_type': 'slash',
        'speed': 250,
        'resistance': 1,
        'attack_radius': 50,
        'notice_radius': 500,
        'attack_cooldown': 600,
        'image': 'basic asset pack/basic asset pack/Basic Undead Animations/Skeleton/Skeleton.gif',
    },

    'ogre': {
        'health': 300,
        'damage': 40,
        'attack_type': 'slam',
        'speed': 80,
        'resistance': 5,
        'attack_radius': 80,
        'notice_radius': 300,
        'attack_cooldown': 2000,
        'image': 'basic asset pack/basic asset pack/Basic Undead Animations/Sand Ghoul/SandGhoul.gif',
    }
}