from typing import List, Any, Callable, Optional
from functools import partial

from settings import *
from support import load_font
from sprites import Player


class UpgradeMenu:
    def __init__(self, player: Player) -> None:
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = load_font('fonts/Ac437_IBM_BIOS.ttf', 30)

        self.should_close: bool = False
        self.state: str = 'main'
        self.selection_index: int = 0
        self.can_click: bool = True
        self.click_time: int = 0

        self.option_rects: List[Tuple[int, pygame.Rect]] = []

        self.select_sound: Optional[pygame.mixer.Sound] = None
        self.buy_sound: Optional[pygame.mixer.Sound] = None
        self.error_sound: Optional[pygame.mixer.Sound] = None
        self._load_audio()

        self.menu_options: List[Dict[str, Any]] = [
            {'name': 'stats_menu', 'label': '> UPGRADE STATS'},
            {'name': 'weapon_menu', 'label': '> WEAPON SHOP'},
            {'name': 'armor_menu', 'label': '> ARMOR SHOP'},
            {'name': 'exit', 'label': '> EXIT MENU'}
        ]

        self.stats_options: List[Dict[str, Any]] = [
            {'name': 'health', 'cost': 50, 'increase': 20, 'label': 'Heal (+20 HP)'},
            {'name': 'attack', 'cost': 100, 'increase': 2, 'label': 'Strength (+2 Atk)'},
            {'name': 'speed', 'cost': 80, 'increase': 20, 'label': 'Speed (+20 Speed)'},
            {'name': 'back', 'cost': 0, 'increase': 0, 'label': '<<< BACK'}
        ]

        self._init_dispatch_tables()

    def _load_audio(self) -> None:
        try:
            self.select_sound = pygame.mixer.Sound('audio/menu_selection.mp3')
            self.select_sound.set_volume(0.2)
            self.buy_sound = pygame.mixer.Sound('audio/buy_sound.mp3')
            self.buy_sound.set_volume(0.3)
            self.error_sound = pygame.mixer.Sound('audio/error_sound.mp3')
            self.error_sound.set_volume(0.3)
        except Exception as e:
            print(f"UI Sound Error: {e}")

    def _init_dispatch_tables(self) -> None:
        self.state_handlers: Dict[str, Callable[[str, Dict[str, Any]], None]] = {
            'main': self._handle_main_state,
            'stats': self._handle_stats_state,
            'weapon': self._handle_weapon_state,
            'armor': self._handle_armor_state
        }
        self.main_menu_actions: Dict[str, Callable[[], None]] = {
            'stats_menu': partial(self._switch_state, 'stats'),
            'weapon_menu': partial(self._switch_state, 'weapon'),
            'armor_menu': partial(self._switch_state, 'armor'),
            'exit': self._close_game_menu
        }
        self.stats_actions: Dict[str, Callable[[int], None]] = {
            'health': lambda inc: self._modify_stat_dict('health', inc),
            'attack': lambda inc: self._modify_stat_dict('attack', inc),
            'speed': lambda inc: self._modify_attribute('speed', inc),
        }

    def _switch_state(self, new_state: str) -> None:
        self.state = new_state
        self.selection_index = 0
        if self.select_sound: self.select_sound.play()

    def _close_game_menu(self) -> None:
        self.should_close = True
        if self.select_sound: self.select_sound.play()

    def _go_back(self) -> None:
        self._switch_state('main')

    def _modify_stat_dict(self, key: str, amount: int) -> None:
        self.player.stats[key] += amount

    def _modify_attribute(self, attr_name: str, amount: int) -> None:
        if hasattr(self.player, attr_name):
            current_val = getattr(self.player, attr_name)
            setattr(self.player, attr_name, current_val + amount)

    def _try_buy(self, cost: int) -> bool:
        if self.player.money >= cost:
            self.player.money -= cost
            if self.buy_sound: self.buy_sound.play()
            return True
        else:
            if self.error_sound: self.error_sound.play()
            return False



    def trigger_item(self, item: Dict[str, Any]) -> None:
        name = item['name']
        if name == 'back':
            self._go_back()
            return

        handler = self.state_handlers.get(self.state)

        if handler:
            handler(name, item)
        else:
            print(f"Warning: No handler for state {self.state}")

    def _handle_main_state(self, name: str, item: Dict[str, Any]) -> None:
        action = self.main_menu_actions.get(name)
        if action:
            action()

    def _handle_stats_state(self, name: str, item: Dict[str, Any]) -> None:
        cost = item.get('cost', 0)
        increase = item.get('increase', 0)

        action = self.stats_actions.get(name)

        if action:
            if self._try_buy(cost):
                action(increase)

    def _handle_weapon_state(self, name: str, item: Dict[str, Any]) -> None:
        if name == 'buy_arrows':
            self._buy_arrows()
        else:
            self._handle_weapon_purchase(name)

    def _handle_armor_state(self, name: str, item: Dict[str, Any]) -> None:
        self._handle_armor_purchase(name)

    def _buy_arrows(self) -> None:
        if self._try_buy(ARROW_COST):
            self.player.ammo['arrow'] += ARROW_BUNDLE

    def _handle_weapon_purchase(self, name: str) -> None:

        if name in self.player.owned_weapons:
            self._equip_weapon(name)
        else:
            weapon_data = WEAPONS.get(name)
            if weapon_data and self._try_buy(weapon_data.cost):
                self.player.owned_weapons.append(name)
                if name == 'bow':
                    self.player.ammo['arrow'] += BOW_INITIAL_ARROWS
                self._equip_weapon(name)

    def _equip_weapon(self, name: str) -> None:
        if self.buy_sound: self.buy_sound.play()
        self.player.weapon_hand = 'right'
        self.player.inventory['weapon'] = name
        self.player.update_weapon_graphics()

    def _handle_armor_purchase(self, name: str) -> None:
        armor_data = ARMORS.get(name)
        if not armor_data: return

        if name in self.player.owned_armors:
            self._equip_or_unequip_armor(name, armor_data)
        else:
            if self._try_buy(armor_data.cost):
                self.player.owned_armors.append(name)
                self._equip_or_unequip_armor(name, armor_data, force_equip=True)

    def _equip_or_unequip_armor(self, name: str, data: Any, force_equip: bool = False) -> None:
        if not force_equip and self.buy_sound: self.buy_sound.play()

        slot = data.slot
        is_equipped = (self.player.inventory.get(slot) == name)

        if is_equipped and not force_equip:
            if slot == 'body':
                self.player.inventory['body'] = 'Leather'
            else:
                self.player.inventory[slot] = None
        else:
            self.player.inventory[slot] = name

            if slot == 'shield' and self.player.inventory['weapon'] == 'bow':
                self.player.inventory['weapon'] = 'short_sword'
                self.player.update_weapon_graphics()

        self.player.update_armor_graphics()

    def get_current_options(self) -> List[Dict[str, Any]]:
        options_map = {
            'main': self.menu_options,
            'stats': self.stats_options,
            'weapon': self._get_weapon_options,  # Lazy loading (funkcja)
            'armor': self._get_armor_options  # Lazy loading (funkcja)
        }

        options = options_map.get(self.state, [])
        if callable(options):
            return options()
        return options

    def _get_weapon_options(self) -> List[Dict[str, Any]]:
        options = [{'name': key, 'type': 'item'} for key in WEAPONS.keys()]
        options.append({'name': 'buy_arrows', 'type': 'item'})
        options.append({'name': 'back', 'label': '<<< BACK', 'type': 'nav'})
        return options

    def _get_armor_options(self) -> List[Dict[str, Any]]:
        # Generowanie dynamiczne
        options = [{'name': key, 'type': 'item'} for key in ARMORS.keys() if key != 'Leather']
        options.append({'name': 'back', 'label': '<<< BACK', 'type': 'nav'})
        return options


    def reset(self) -> None:
        self.state = 'main'
        self.selection_index = 0
        self.can_click = False
        self.click_time = pygame.time.get_ticks()

    def calculate_total_stats(self) -> Tuple[int, int]:
        weapon_name = self.player.inventory.get('weapon')
        weapon_dmg = WEAPONS[weapon_name].damage if weapon_name else 0
        total_attack = self.player.stats['attack'] + weapon_dmg

        total_defense = sum(
            ARMORS[self.player.inventory[slot]].defense
            for slot in ['body', 'head', 'shield']
            if self.player.inventory.get(slot)
        )
        return total_attack, total_defense

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        options = self.get_current_options()

        for index, rect in self.option_rects:
            if rect.collidepoint(mouse_pos):
                if self.selection_index != index:
                    self.selection_index = index
                    if self.select_sound: self.select_sound.play()

                if mouse_pressed[0] and self.can_click:
                    self.trigger_item(options[index])
                    self.can_click = False
                    self.click_time = pygame.time.get_ticks()

        if self.can_click:
            if keys[pygame.K_UP]:
                self._change_selection(-1, len(options))
            elif keys[pygame.K_DOWN]:
                self._change_selection(1, len(options))
            elif keys[pygame.K_SPACE]:
                self.trigger_item(options[self.selection_index])
                self._lock_input()
            elif keys[pygame.K_ESCAPE]:
                if self.state != 'main':
                    self._go_back()
                else:
                    self._close_game_menu()  # Escape w menu głównym też może zamykać
                self._lock_input()

        if not self.can_click:
            if pygame.time.get_ticks() - self.click_time > 200:
                self.can_click = True

    def _change_selection(self, direction: int, max_len: int) -> None:
        self.selection_index = (self.selection_index + direction) % max_len
        if self.select_sound: self.select_sound.play()
        self._lock_input()

    def _lock_input(self) -> None:
        self.can_click = False
        self.click_time = pygame.time.get_ticks()

    def display(self) -> None:
        self.option_rects.clear()
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(210)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0, 0))

        total_atk, total_def = self.calculate_total_stats()
        self.draw_text(f"HP: {self.player.stats['health']}", (255, 100, 100), 50, 50)
        self.draw_text(f"DMG: {total_atk}", (255, 100, 0), WIDTH // 4 + 50, 50)
        self.draw_text(f"DEF: {total_def}", (0, 255, 255), WIDTH // 2 + 50, 50)

        money_surf = self.font.render(f"Gold: {self.player.money}", True, (255, 215, 0))
        self.display_surface.blit(money_surf, (WIDTH - 50 - money_surf.get_width(), 50))

        pygame.draw.line(self.display_surface, (100, 100, 100), (0, 90), (WIDTH, 90), 2)

        title_map = {'main': "MAIN MENU", 'stats': "UPGRADES", 'weapon': "WEAPON SHOP", 'armor': "ARMOR SHOP"}
        title = title_map.get(self.state, "")
        title_surf = self.font.render(title, True, (150, 150, 150))
        self.display_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 120))

        options = self.get_current_options()
        for index, item in enumerate(options):
            self._draw_option(index, item, index == self.selection_index)

    def _draw_option(self, index: int, item: Dict[str, Any], is_selected: bool) -> None:
        name = item['name']
        label = item.get('label', name)
        color = (255, 255, 255)
        suffix = ""
        if self.state == 'weapon':
            if name == 'buy_arrows':
                label = f"ARROWS (+{ARROW_BUNDLE})"
                suffix = f" - Cost: {ARROW_COST}"
                if self.player.money < ARROW_COST: color = (100, 100, 100)
            elif name != 'back':
                data = WEAPONS[name]
                label = f"{data.name} (Dmg: {data.damage})"
                if self.player.inventory['weapon'] == name:
                    color = (0, 255, 0)
                    suffix = " (EQUIPPED)"
                elif name in self.player.owned_weapons:
                    color = (255, 255, 0)
                    suffix = " (OWNED)"
                else:
                    suffix = f" - Cost: {data.cost}"
                    if self.player.money < data.cost: color = (100, 100, 100)

        elif self.state == 'armor':
            if name != 'back':
                data = ARMORS[name]
                label = f"{data.name} (Def: {data.defense})"
                if self.player.inventory.get(data.slot) == name:
                    color = (0, 255, 0)
                    suffix = " (EQUIPPED)"
                elif name in self.player.owned_armors:
                    color = (255, 255, 0)
                    suffix = " (OWNED)"
                else:
                    suffix = f" - Cost: {data.cost}"
                    if self.player.money < data.cost: color = (100, 100, 100)

        elif self.state == 'stats':
            if 'cost' in item and item['cost'] > 0:
                suffix = f" - Cost: {item['cost']}"
                if self.player.money < item['cost']: color = (100, 100, 100)

        final_text = f"> {label}{suffix} <" if is_selected else f"  {label}{suffix}  "

        text_surf = self.font.render(final_text, True, color)
        x = WIDTH // 2 - text_surf.get_width() // 2
        y = 250 + (index * 60)

        rect = self.display_surface.blit(text_surf, (x, y))
        self.option_rects.append((index, rect))

    def draw_text(self, text: str, color: Tuple[int, int, int], x: int, y: int) -> None:
        surf = self.font.render(text, True, color)
        self.display_surface.blit(surf, (x, y))