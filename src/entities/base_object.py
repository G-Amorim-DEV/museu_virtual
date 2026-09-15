from abc import ABC, abstractmethod


class BaseObject(ABC):
    """Contrato mínimo para qualquer peça do acervo."""

    def __init__(self, title, author, position):
        self.title = title
        self.author = author
        self.x, self.y = position
        self.visible = True
        self.highlighted = False
        self.rotation = 0.0

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, renderer, camera):
        pass

    @abstractmethod
    def get_bounds(self):
        return (0.0, 0.0, 0.0, 0.0)
