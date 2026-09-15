import math
from .base_object import BaseObject


class Icosaedro(BaseObject):
    """Icosaedro wireframe com rotação contínua e pedestal chanfrado."""

    def __init__(self, position):
        super().__init__("Icosaedro Wireframe", "Geometria Computacional", position)
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        self.base_vertices = [
            (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
            (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
            (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
        ]
        self.edges = [
            (0,1),(0,5),(0,7),(0,11),(0,10),(1,5),(1,7),(1,8),(1,9),
            (2,3),(2,4),(2,6),(2,10),(2,11),(3,4),(3,6),(3,8),(3,9),
            (4,5),(4,9),(4,11),(5,9),(5,11),(6,7),(6,8),(6,10),
            (7,8),(7,10),(8,9),(10,11)
        ]

    def update(self, dt):
        self.rotation += 0.9 * dt

    def _vertices(self):
        sin_r, cos_r = math.sin(self.rotation), math.cos(self.rotation)
        result = []
        for x, y, z in self.base_vertices:
            rx = x * cos_r - z * sin_r
            rz = x * sin_r + z * cos_r
            result.append((self.x + rx * 65, self.y + y * 55, 900 + rz * 65))
        return result

    def draw(self, renderer, camera):
        cx = int(renderer.width * 0.5 + (self.x - camera.x) * camera.zoom)
        cy = int(renderer.height * 0.48 + (self.y - camera.y) * camera.zoom)
        pedestal = [(cx-100,cy+120),(cx-72,cy+90),(cx+72,cy+90),(cx+100,cy+120),
                    (cx+82,cy+155),(cx-82,cy+155)]
        renderer.polygon(pedestal, (70, 74, 82))
        renderer.polygon([(cx-72,cy+90),(cx+72,cy+90),(cx+55,cy+108),(cx-55,cy+108)], (105,110,120))
        renderer.wireframe(self._vertices(), self.edges, camera, (255, 205, 80), 2)
        if self.highlighted:
            renderer.circle((cx, cy), 105, (255, 235, 140), 3)

    def get_bounds(self):
        return (self.x-120,self.y-120,self.x+120,self.y+160)


class EspiralAurea(BaseObject):
    """Espiral de Fibonacci aproximada por arcos proporcionais."""

    def __init__(self, position):
        super().__init__("Espiral Áurea de Fibonacci", "Matemática", position)
        self.angle = 0.0

    def update(self, dt):
        self.angle += 0.15 * dt

    def draw(self, renderer, camera):
        cx = int(renderer.width * .5 + (self.x-camera.x)*camera.zoom)
        cy = int(renderer.height * .48 + (self.y-camera.y)*camera.zoom)
        points = []
        radius = 6.0
        for i in range(95):
            theta = self.angle + i * 0.19
            radius *= 1.025 if i else 1
            if radius > 105:
                radius = 105
            points.append((cx + math.cos(theta)*radius*camera.zoom,
                           cy + math.sin(theta)*radius*camera.zoom))
        renderer.line(points, (100, 220, 170), 3)
        renderer.circle((cx, cy), 6, (240, 220, 100))
        if self.highlighted:
            renderer.circle((cx, cy), int(120 * camera.zoom), (255, 235, 140), 3)

    def get_bounds(self):
        return (self.x-125,self.y-125,self.x+125,self.y+125)
