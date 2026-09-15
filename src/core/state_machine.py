from enum import Enum, auto


class MuseumState(Enum):
    MENU = auto()
    EXPLORATION = auto()
    BASIC_SCRIPT = auto()
    CURATION = auto()
    IMMERSIVE_TOUR = auto()
    PAUSED = auto()
    CREDITS = auto()
    COMPLETED = auto()


class StateMachine:
    """Mantém exclusivamente o estado global da aplicação."""

    def __init__(self):
        self.current = MuseumState.MENU

    def change(self, state):
        self.current = state
