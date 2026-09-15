import math
import pygame


class Renderer:
    """Renderizador 2D/3D leve baseado apenas nas primitivas do Pygame."""

    def __init__(self, surface):
        self.surface = surface
        self.width, self.height = surface.get_size()

    def clear(self):
        self.surface.fill((10, 12, 18))

    def project(self, point, camera):
        x, y, z = point
        depth = max(80.0, z - camera.z + 900.0)
        scale = 500.0 / depth
        sx = self.width * 0.5 + (x - camera.x) * scale * camera.zoom
        sy = self.height * 0.5 + (y - camera.y) * scale * camera.zoom
        return int(sx), int(sy)

    def polygon(self, points, color, width=0):
        pygame.draw.polygon(self.surface, color, points, width)

    def line(self, points, color, width=1):
        if len(points) >= 2:
            pygame.draw.lines(self.surface, color, False, points, width)

    def circle(self, center, radius, color, width=0):
        pygame.draw.circle(self.surface, color, center, radius, width)

    def rect(self, rect, color, width=0):
        pygame.draw.rect(self.surface, color, rect, width)

    def text(self, font, value, position, color=(235, 238, 245)):
        self.surface.blit(font.render(value, True, color), position)

    def wireframe(self, vertices, edges, camera, color=(120, 220, 255), width=2):
        projected = [self.project(v, camera) for v in vertices]
        for a, b in edges:
            pygame.draw.line(self.surface, color, projected[a], projected[b], width)
        return projected

    def draw_3d_box(self, x, y, z, w, h, d, camera):
        vertices = [
            (x-w, y-h, z-d), (x+w, y-h, z-d),
            (x+w, y+h, z-d), (x-w, y+h, z-d),
            (x-w, y-h, z+d), (x+w, y-h, z+d),
            (x+w, y+h, z+d), (x-w, y+h, z+d)
        ]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]
        return self.wireframe(vertices, edges, camera)

    @staticmethod
    def regular_polygon(cx, cy, radius, sides, rotation=0.0):
        return [
            (cx + math.cos(rotation + i * math.tau / sides) * radius,
             cy + math.sin(rotation + i * math.tau / sides) * radius)
            for i in range(sides)
        ]
