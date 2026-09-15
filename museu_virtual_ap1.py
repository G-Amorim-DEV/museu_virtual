"""Compatibilidade da AP1: a experiência principal agora é o motor unificado."""
from src.core.engine import Engine

# Mantém o nome público usado na entrega AP1, sem criar uma segunda experiência.
MuseuVirtual3D = Engine

if __name__ == "__main__":
    Engine().run()
