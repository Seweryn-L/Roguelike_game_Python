# hud.py
import pygame
from settings import *


class HUD:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()

        # Ładowanie czcionki
        try:
            self.font = pygame.font.Font('fonts/Ac437_IBM_BIOS.ttf', 20)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 24)

        self.text_color = (255, 255, 255)  # Biały

    def display(self):
        # 1. Pobieramy dane
        # Atak
        base_atk = self.player.stats['attack']
        weapon_dmg = WEAPONS[self.player.inventory['weapon']]['damage']
        total_atk = base_atk + weapon_dmg

        # Obrona
        total_def = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.player.inventory.get(slot)
            if item_name:
                total_def += ARMORS[item_name]['defense']

        # 2. Przygotowujemy listę tekstów
        stats_info = [
            f"HP: {int(self.player.stats['health'])}",
            f"Gold: {self.player.money}",
            f"Dmg: {total_atk}",
            f"Armor: {total_def}"
        ]

        # 3. Rysujemy
        x, y = 10, 10  # Pozycja startowa (lewy górny róg)
        for line in stats_info:
            # Cień (dla czytelności)
            shadow_surf = self.font.render(line, False, (0, 0, 0))
            self.display_surface.blit(shadow_surf, (x + 2, y + 2))

            # Właściwy tekst
            text_surf = self.font.render(line, False, self.text_color)
            self.display_surface.blit(text_surf, (x, y))

            y += 30  # Przesunięcie w dół dla kolejnej linii