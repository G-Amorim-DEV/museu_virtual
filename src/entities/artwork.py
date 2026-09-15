from pathlib import Path
import pygame
from .base_object import BaseObject


class PainelExposicao(BaseObject):
    """Painel clássico reutilizável para todas as quatro pinturas."""

    def __init__(self, title, author, position, image_name, color):
        super().__init__(title, author, position)
        self.image_name = image_name
        self.color = color
        self.image = self._load_image(image_name)
        self._scaled_images = {}

    def _load_image(self, name):
        path = Path(__file__).resolve().parents[2] / "assets" / "images" / name
        if not path.exists():
            return None
        try:
            return pygame.image.load(path).convert()
        except (pygame.error, OSError):
            return None

    def update(self, dt):
        pass

    def draw(self, renderer, camera):
        cx = int(renderer.width * 0.5 + (self.x - camera.x) * camera.zoom)
        cy = int(renderer.height * 0.48 + (self.y - camera.y) * camera.zoom)
        scale = camera.zoom
        w = max(180, int(250 * scale))
        h = max(130, int(180 * scale))
        frame = pygame.Rect(cx - w//2 - 14, cy - h//2 - 14, w + 28, h + 28)

        renderer.rect(frame, (55, 42, 28))
        renderer.rect(frame.inflate(-8, -8), (125, 91, 48), 3)

        if self.image:
            size = (w, h)
            image = self._scaled_images.get(size)
            if image is None:
                image = pygame.transform.smoothscale(self.image, size)
                self._scaled_images[size] = image
            renderer.surface.blit(image, (cx - w//2, cy - h//2))
        else:
            renderer.rect((cx-w//2, cy-h//2, w, h), self.color)
            # Fallback procedural: composição abstrata para manter o projeto autônomo.
            renderer.circle((cx - w//7, cy - h//8), max(8, h//7), (235, 190, 140))
            renderer.circle((cx + w//5, cy - h//10), max(7, h//9), (220, 180, 130))
            renderer.line([(cx-w//2, cy+h//4), (cx, cy-h//8), (cx+w//2, cy+h//4)], (55, 75, 90), 4)

        if self.highlighted:
            renderer.rect(frame.inflate(12, 12), (255, 235, 140), 3)

    def get_bounds(self):
        return (self.x - 145, self.y - 105, self.x + 145, self.y + 105)
