import pygame
from settings import *
from support import load_font
from sprites import Player


class HUD:
    def __init__(self, player: Player) -> None:
        self.player = player
        self.display_surface = pygame.display.get_surface()

        self.font = load_font('fonts/Ac437_IBM_BIOS.ttf', 20)
        self.text_color = (255, 255, 255)

    def display(self) -> None:
        base_atk = self.player.stats['attack']

        weapon_name = self.player.inventory['weapon']
        weapon_dmg = WEAPONS[weapon_name].damage

        total_atk = base_atk + weapon_dmg

        total_def = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.player.inventory.get(slot)
            if item_name:
                total_def += ARMORS[item_name].defense

        stats_info = [
            f"HP: {int(self.player.stats['health'])}",
            f"Gold: {self.player.money}",
            f"Dmg: {total_atk}",
            f"Armor: {total_def}"
        ]

        if self.player.inventory['weapon'] == 'bow':
            arrow_count = self.player.ammo['arrow']
            stats_info.append(f"Arrows: {arrow_count}")

        x, y = 10, 10
        for line in stats_info:
            shadow_surf = self.font.render(line, False, (0, 0, 0))
            self.display_surface.blit(shadow_surf, (x + 2, y + 2))

            text_surf = self.font.render(line, False, self.text_color)
            self.display_surface.blit(text_surf, (x, y))

            y += 30
