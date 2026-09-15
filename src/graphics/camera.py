from dataclasses import dataclass


@dataclass
class Camera:
    """Câmera 2.5D com interpolação linear de posição e zoom."""

    x: float = 0.0
    y: float = 0.0
    z: float = 900.0
    target_x: float = 0.0
    target_y: float = 0.0
    target_z: float = 900.0
    zoom: float = 1.0
    target_zoom: float = 1.0

    def set_general(self, x, y):
        self.target_x = x
        self.target_y = y
        self.target_z = 900.0
        self.target_zoom = 1.0

    def set_detail(self, x, y):
        self.target_x = x
        self.target_y = y
        self.target_z = 620.0
        self.target_zoom = 1.35

    def reset(self):
        self.set_general(0.0, 0.0)

    def update(self, dt):
        # Aproximação exponencial estável: resultado independente do FPS.
        factor = min(1.0, 7.0 * dt)
        self.x += (self.target_x - self.x) * factor
        self.y += (self.target_y - self.y) * factor
        self.z += (self.target_z - self.z) * factor
        self.zoom += (self.target_zoom - self.zoom) * factor
