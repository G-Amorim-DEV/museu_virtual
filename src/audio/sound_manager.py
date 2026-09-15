from pathlib import Path
import pygame


class SoundManager:
    """Gerencia áudio opcional sem carregar todos os arquivos em RAM."""

    def __init__(self):
        self.enabled = False
        self.current = None
        self._durations = {}
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _path_for(self, filename):
        return Path(__file__).resolve().parents[2] / "assets" / "audio" / filename

    def get_duration(self, filename, fallback=4.0):
        """Retorna a duração do arquivo sem interromper a música em reprodução."""
        if filename in self._durations:
            return self._durations[filename]

        duration = fallback
        path = self._path_for(filename)
        if self.enabled and path.exists():
            try:
                duration = max(0.1, pygame.mixer.Sound(str(path)).get_length())
            except pygame.error:
                pass

        self._durations[filename] = duration
        return duration

    def play(self, filename):
        if not self.enabled:
            return
        path = self._path_for(filename)
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
            self.current = filename
        except pygame.error:
            self.current = None

    def pause(self):
        if self.enabled:
            pygame.mixer.music.pause()

    def resume(self):
        if self.enabled:
            pygame.mixer.music.unpause()

    def stop(self):
        if self.enabled:
            pygame.mixer.music.stop()
        self.current = None

    def restart(self):
        if self.enabled and self.current:
            pygame.mixer.music.stop()
            self.play(self.current)
