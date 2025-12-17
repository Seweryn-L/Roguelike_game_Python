import pygame
from settings import *


class HUD:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()

        try:
            self.font = pygame.font.Font('fonts/Ac437_IBM_BIOS.ttf', 20)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 24)

        self.text_color = (255, 255, 255)

    def display(self):
        base_atk = self.player.stats['attack']
        weapon_dmg = WEAPONS[self.player.inventory['weapon']]['damage']
        total_atk = base_atk + weapon_dmg

        total_def = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.player.inventory.get(slot)
            if item_name:
                total_def += ARMORS[item_name]['defense']

        stats_info = [
            f"HP: {int(self.player.stats['health'])}",
            f"Gold: {self.player.money}",
            f"Dmg: {total_atk}",
            f"Armor: {total_def}"
        ]

        x, y = 10, 10
        for line in stats_info:
            shadow_surf = self.font.render(line, False, (0, 0, 0))
            self.display_surface.blit(shadow_surf, (x + 2, y + 2))

            text_surf = self.font.render(line, False, self.text_color)
            self.display_surface.blit(text_surf, (x, y))

            y += 30