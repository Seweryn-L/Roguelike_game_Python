import pygame

def load_font(path: str, size: int) -> pygame.font.Font:
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        print(f"Warning: Font {path} not found. Loading default system font.")
        return pygame.font.Font(None, size)


class SpriteSheet:
    def __init__(self, filename: str):
        self.filename = filename
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except (FileNotFoundError, pygame.error) as e:
            raise FileNotFoundError(f"Unable to load spritesheet: {filename}") from e

    def get_image(self, col: int, row: int, width: int = 16, height: int = 16, scale: int = 1) -> pygame.Surface:
        x = col * (width + 1)
        y = row * (height + 1)

        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        return image
