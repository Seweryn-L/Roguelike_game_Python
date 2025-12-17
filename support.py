import pygame


class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except FileNotFoundError:
            print(f"BŁĄD: Nie znaleziono pliku {filename}")
            raise SystemExit

    def get_image(self, col, row, width=16, height=16, scale=1):

        x = col * (width + 1)
        y = row * (height + 1)
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        return image