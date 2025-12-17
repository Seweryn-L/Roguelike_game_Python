import pygame
from settings import *
class UpgradeMenu:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        try:
            self.font = pygame.font.Font('fonts/Ac437_IBM_BIOS.ttf', 30)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 30)

        self.should_close = False

        self.state = 'main'

        self.menu_options = [
            {'name': 'stats_menu', 'label': '> UPGRADE STATS'},
            {'name': 'weapon_menu', 'label': '> SKLEP Z BRONIA'},
            {'name': 'armor_menu', 'label': '> SKLEP Z PANCERZEM'},
            {'name': 'exit', 'label': '> WYJDZ Z MENU'}
        ]

        self.stats_options = [
            {'name': 'health', 'cost': 50, 'increase': 20, 'label': 'Leczenie (+20 HP)'},
            {'name': 'attack', 'cost': 100, 'increase': 5, 'label': 'Sila (+5 Atk)'},
            {'name': 'speed', 'cost': 80, 'increase': 20, 'label': 'Szybkosc (+20 Speed)'},
            {'name': 'back', 'cost': 0, 'increase': 0, 'label': '<<< WROC'}
        ]

        self.weapon_options = []
        for key, data in WEAPONS.items():
            self.weapon_options.append({
                'name': key,
                'cost': data['cost'],
                'label': f"{data['name']} (Dmg: {data['damage']})",
                'type': 'item'
            })
        self.weapon_options.append({'name': 'back', 'cost': 0, 'label': '<<< WROC', 'type': 'nav'})

        self.armor_options = []
        for key, data in ARMORS.items():
            if key == 'Leather':
                continue

            self.armor_options.append({
                'name': key,
                'cost': data['cost'],
                'label': f"{data['name']} (Def: {data['defense']})",
                'type': 'item'
            })
        self.armor_options.append({'name': 'back', 'cost': 0, 'label': '<<< WROC', 'type': 'nav'})

        self.selection_index = 0
        self.can_click = True
        self.click_time = 0

    def get_current_options(self):
        if self.state == 'main': return self.menu_options
        if self.state == 'stats': return self.stats_options
        if self.state == 'weapon': return self.weapon_options
        if self.state == 'armor': return self.armor_options
        return []

    def calculate_total_stats(self):
        weapon_name = self.player.inventory['weapon']
        weapon_dmg = WEAPONS[weapon_name]['damage']
        total_attack = self.player.stats['attack'] + weapon_dmg

        total_defense = 0
        for slot in ['body', 'head', 'shield']:
            item_name = self.player.inventory.get(slot)
            if item_name:
                total_defense += ARMORS[item_name]['defense']

        return total_attack, total_defense

    def input(self):
        keys = pygame.key.get_pressed()
        options = self.get_current_options()

        if keys[pygame.K_UP] and self.can_click:
            self.selection_index = (self.selection_index - 1) % len(options)
            self.can_click = False
            self.click_time = pygame.time.get_ticks()

        if keys[pygame.K_DOWN] and self.can_click:
            self.selection_index = (self.selection_index + 1) % len(options)
            self.can_click = False
            self.click_time = pygame.time.get_ticks()

        if keys[pygame.K_SPACE] and self.can_click:
            self.trigger_item(options[self.selection_index])
            self.can_click = False
            self.click_time = pygame.time.get_ticks()

        if not self.can_click:
            if pygame.time.get_ticks() - self.click_time > 200:
                self.can_click = True

    def trigger_item(self, item):
        name = item['name']

        if name == 'back':
            self.state = 'main'
            self.selection_index = 0
            return

        if self.state == 'main':
            if name == 'stats_menu':
                self.state = 'stats'
            elif name == 'weapon_menu':
                self.state = 'weapon'
            elif name == 'armor_menu':
                self.state = 'armor'
            elif name == 'exit':
                self.should_close = True
            self.selection_index = 0

        elif self.state == 'stats':
            if self.player.money >= item['cost']:
                self.player.money -= item['cost']
                if name == 'health':
                    self.player.stats['health'] += item['increase']
                elif name == 'attack':
                    self.player.stats['attack'] += item['increase']
                elif name == 'speed':
                    self.player.speed += item['increase']

        elif self.state == 'weapon':
            self.player.weapon_hand = 'left'
            if name in self.player.owned_weapons:
                self.player.inventory['weapon'] = name
                self.player.update_weapon_graphics()
            else:
                if self.player.money >= item['cost']:
                    self.player.money -= item['cost']
                    self.player.owned_weapons.append(name)
                    self.player.inventory['weapon'] = name
                    self.player.update_weapon_graphics()

        elif self.state == 'armor':
            armor_data = ARMORS[name]
            slot_type = armor_data['slot']

            is_equipped = (self.player.inventory.get(slot_type) == name)

            if name in self.player.owned_armors:
                if is_equipped:
                    if slot_type == 'body':
                        self.player.inventory['body'] = 'Leather'
                        print("Zdjęto zbroję (powrót do Leather)")
                    else:
                        self.player.inventory[slot_type] = None
                        print(f"Zdjęto {name}")
                else:
                    self.player.inventory[slot_type] = name
                    print(f"Założono {name}")

                self.player.update_armor_graphics()

            else:
                if self.player.money >= item['cost']:
                    self.player.money -= item['cost']
                    self.player.owned_armors.append(name)

                    self.player.inventory[slot_type] = name
                    self.player.update_armor_graphics()
                    print(f"Kupiono i założono {name}")

    def display(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(210)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0, 0))

        total_atk, total_def = self.calculate_total_stats()

        hp_str = f"HP: {self.player.stats['health']}"
        atk_str = f"DMG: {total_atk}"
        def_str = f"DEF: {total_def}"
        money_str = f"Zloto: {self.player.money}"

        hp_surf = self.font.render(hp_str, True, (255, 100, 100))
        atk_surf = self.font.render(atk_str, True, (255, 100, 0))
        def_surf = self.font.render(def_str, True, (0, 255, 255))
        money_surf = self.font.render(money_str, True, (255, 215, 0))

        stats_y = 50
        col_width = WIDTH // 4

        self.display_surface.blit(hp_surf, (50, stats_y))
        self.display_surface.blit(atk_surf, (50 + col_width * 1, stats_y))
        self.display_surface.blit(def_surf, (50 + col_width * 2, stats_y))
        self.display_surface.blit(money_surf, (WIDTH - 50 - money_surf.get_width(), stats_y))

        pygame.draw.line(self.display_surface, (100, 100, 100), (0, 90), (WIDTH, 90), 2)

        title = ""
        if self.state == 'main':
            title = "MENU GLOWNE"
        elif self.state == 'stats':
            title = "ULEPSZENIA"
        elif self.state == 'weapon':
            title = "SKLEP Z BRONIA"
        elif self.state == 'armor':
            title = "SKLEP Z PANCERZEM"

        title_surf = self.font.render(title, True, (150, 150, 150))
        self.display_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 120))

        options = self.get_current_options()

        for index, item in enumerate(options):
            name = item['name']
            color = (255, 255, 255)
            for index, item in enumerate(options):
                color = (255, 215, 0) if index == self.selection_index else (255, 255, 255)
                label = item['label']
                if 'cost' in item and item['cost'] > 0:
                    label += f" - Koszt: {item['cost']}"
                option_surf = self.font.render(label, True, color)
                x = WIDTH // 2 - option_surf.get_width() // 2
                y = 250 + (index * 60)
                self.display_surface.blit(option_surf, (x, y))