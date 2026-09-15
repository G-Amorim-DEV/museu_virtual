"""Colisões 2D no plano do piso, independentes do renderizador."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    """Retângulo alinhado aos eixos no plano X/Z."""
    left: float
    near: float
    right: float
    far: float

    def expanded(self, radius: float) -> "Rect":
        return Rect(self.left - radius, self.near - radius, self.right + radius, self.far + radius)

    def contains(self, x: float, z: float) -> bool:
        return self.left <= x <= self.right and self.near <= z <= self.far


class CollisionMap:
    """Limites, paredes sólidas e bases expositivas da planta do museu."""

    def __init__(self, bounds: Rect, solids: tuple[Rect, ...], visitor_radius: float = .42):
        self.bounds = bounds
        self.solids = solids
        self.visitor_radius = visitor_radius

    def walkable(self, x: float, z: float) -> bool:
        safe = self.bounds.expanded(-self.visitor_radius)
        if not safe.contains(x, z):
            return False
        return not any(solid.expanded(self.visitor_radius).contains(x, z) for solid in self.solids)

    def move(self, x: float, z: float, dx: float, dz: float) -> tuple[float, float]:
        """Desliza ao longo de paredes em vez de bloquear todo movimento diagonal."""
        if self.walkable(x + dx, z + dz):
            return x + dx, z + dz
        if self.walkable(x + dx, z):
            return x + dx, z
        if self.walkable(x, z + dz):
            return x, z + dz
        return x, z
