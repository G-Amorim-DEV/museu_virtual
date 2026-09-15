import sys
import pygame

from .state_machine import StateMachine, MuseumState
from ..graphics.renderer import Renderer
from ..graphics.camera import Camera
from ..graphics.raycaster import Raycaster
from ..audio.sound_manager import SoundManager
from ..ui.menu import Menu, Credits
from ..ui.hud import HUD
from ..entities.artwork import PainelExposicao
from ..entities.math_sculpture import Icosaedro, EspiralAurea
from ..entities.tech_monolith import ServidorMonolitico, FitaTuring


class Engine:
    WIDTH = 1100
    HEIGHT = 700
    FPS = 60
    TOUR_AUDIO = (
        "01_mona_lisa.ogg", "02_rembrandt.ogg", "03_guernica.ogg",
        "04_noite_estrelada.ogg", "05_icosaedro.ogg", "06_espiral_aurea.ogg",
        "07_servidor_monolitico.ogg", "08_tuning.ogg",
    )

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Museu Virtual de Computação Gráfica")
        self.clock = pygame.time.Clock()

        self.renderer = Renderer(self.screen)
        self.camera = Camera()
        self.state_machine = StateMachine()
        self.sound = SoundManager()
        self.menu = Menu(self.renderer)
        self.credits = Credits(self.renderer)
        self.hud = HUD(self.renderer)

        self.objects = self._create_collection()
        self.active_index = 0
        self.paused = False
        self.ray_enabled = True
        self.tour_time = 0.0
        self.status = "PARADO"
        self.tour_durations = [self.sound.get_duration(filename) for filename in self.TOUR_AUDIO]
        self.tour_total_duration = sum(self.tour_durations)

    def _create_collection(self):
        return [
            PainelExposicao("Mona Lisa", "Leonardo da Vinci", (-450, 0), "Mona_Lisa.jpg", (116, 92, 65)),
            PainelExposicao("Autorretrato", "Rembrandt", (-150, 0), "Rembrandt.jpg", (82, 60, 48)),
            PainelExposicao("Guernica", "Pablo Picasso", (150, 0), "Guernica - Picasso.jpg", (80, 80, 78)),
            PainelExposicao("Noite Estrelada", "Vincent van Gogh", (450, 0), "Noite_Estrelada.jpg", (48, 75, 120)),
            Icosaedro((0, -35)),
            EspiralAurea((0, 0)),
            ServidorMonolitico((0, 0)),
            FitaTuring((0, 0)),
        ]

    @property
    def active(self):
        return self.objects[self.active_index]

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key)

            if not self.paused:
                self._update(dt)
            self._draw()

        self.sound.stop()
        pygame.quit()
        sys.exit()

    def _handle_key(self, key):
        state = self.state_machine.current

        if key == pygame.K_ESCAPE:
            if state == MuseumState.MENU:
                return False
            self._go_menu()
            return True

        if key == pygame.K_m:
            self._go_menu()
            return True

        if state == MuseumState.MENU:
            if key == pygame.K_1:
                self._start_basic()
            elif key == pygame.K_2:
                self._start_curation()
            elif key == pygame.K_3:
                self._start_tour()
            elif key == pygame.K_c:
                self.state_machine.change(MuseumState.CREDITS)

        elif state == MuseumState.CREDITS:
            pass

        elif state == MuseumState.CURATION:
            if key == pygame.K_LEFT:
                self.active_index = (self.active_index - 1) % len(self.objects)
            elif key == pygame.K_RIGHT:
                self.active_index = (self.active_index + 1) % len(self.objects)
            elif key == pygame.K_1:
                self.camera.set_general(self.active.x, self.active.y)
            elif key == pygame.K_2:
                self.camera.set_detail(self.active.x, self.active.y)
            elif key == pygame.K_l:
                self.ray_enabled = not self.ray_enabled
            elif key == pygame.K_SPACE:
                self.paused = not self.paused
                self.status = "PAUSADO" if self.paused else "EXECUTANDO"
            elif key == pygame.K_r:
                self._start_curation()

        elif state == MuseumState.BASIC_SCRIPT:
            if key == pygame.K_SPACE:
                self.paused = not self.paused
                self.status = "PAUSADO" if self.paused else "EXECUTANDO"
            elif key == pygame.K_r:
                self._start_basic()

        elif state == MuseumState.IMMERSIVE_TOUR:
            if key == pygame.K_SPACE:
                self.paused = not self.paused
                if self.paused:
                    self.sound.pause()
                    self.status = "PAUSADO"
                else:
                    self.sound.resume()
                    self.status = "EXECUTANDO"
            elif key == pygame.K_r:
                self._start_tour()

        return True

    def _go_menu(self):
        self.sound.stop()
        self.state_machine.change(MuseumState.MENU)
        self.paused = False
        self.status = "PARADO"

    def _start_basic(self):
        self.state_machine.change(MuseumState.BASIC_SCRIPT)
        self.active_index = 0
        self.tour_time = 0
        self.paused = False
        self.status = "EXECUTANDO"
        self.camera.reset()

    def _start_curation(self):
        self.state_machine.change(MuseumState.CURATION)
        self.active_index = 0
        self.paused = False
        self.status = "EXECUTANDO"
        self.camera.set_general(self.active.x, self.active.y)

    def _start_tour(self):
        self.state_machine.change(MuseumState.IMMERSIVE_TOUR)
        self.active_index = 0
        self.tour_time = 0
        self.paused = False
        self.status = "EXECUTANDO"
        self.camera.set_general(self.active.x, self.active.y)
        self.sound.play("01_mona_lisa.ogg")

    def _tour_index_at(self, elapsed):
        position = 0.0
        for index, duration in enumerate(self.tour_durations):
            position += duration
            if elapsed < position:
                return index
        return len(self.objects) - 1

    def _update(self, dt):
        self.camera.update(dt)

        if self.state_machine.current == MuseumState.BASIC_SCRIPT:
            self.tour_time += dt
            self.active_index = min(len(self.objects)-1, int(self.tour_time / 3.0))
            self.camera.set_general(self.active.x, self.active.y)
            if self.tour_time >= len(self.objects)*3.0:
                self.status = "CONCLUIDO"

        elif self.state_machine.current == MuseumState.IMMERSIVE_TOUR:
            self.tour_time += dt
            next_index = self._tour_index_at(self.tour_time)
            if next_index != self.active_index:
                self.active_index = next_index
                self.sound.play(self.TOUR_AUDIO[self.active_index])
            self.camera.set_detail(self.active.x, self.active.y)
            if self.tour_time >= self.tour_total_duration:
                self.status = "CONCLUIDO"
                self.sound.stop()

        for obj in self.objects:
            obj.update(dt)

        if self.ray_enabled:
            bounds = self._screen_bounds(self.active.get_bounds())
            origin = (self.renderer.width/2, self.renderer.height/2)
            target = ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
            direction = (target[0] - origin[0], target[1] - origin[1])
            self.active.highlighted = Raycaster.intersects(origin, direction, bounds)
        else:
            self.active.highlighted = False

    def _screen_bounds(self, bounds):
        left, top, right, bottom = bounds
        center_x = self.renderer.width * 0.5
        center_y = self.renderer.height * 0.48
        return (
            center_x + (left - self.camera.x) * self.camera.zoom,
            center_y + (top - self.camera.y) * self.camera.zoom,
            center_x + (right - self.camera.x) * self.camera.zoom,
            center_y + (bottom - self.camera.y) * self.camera.zoom,
        )

    def _draw(self):
        state = self.state_machine.current

        if state == MuseumState.MENU:
            self.menu.draw()
        elif state == MuseumState.CREDITS:
            self.credits.draw()
        else:
            self.renderer.clear()
            self._draw_environment()
            self.active.draw(self.renderer, self.camera)
            self._draw_hud(state)

        pygame.display.flip()

    def _draw_environment(self):
        r = self.renderer
        # Ambiente estático: barato para CPU e evita criação de superfícies por frame.
        r.rect((70, 125, r.width-140, 8), (80, 82, 88))
        r.rect((90, 510, r.width-180, 80), (35, 37, 43))
        for x in range(120, r.width-100, 110):
            r.rect((x, 120, 4, 400), (38, 40, 46))

    def _draw_hud(self, state):
        names = {
            MuseumState.BASIC_SCRIPT: "Roteiro Básico",
            MuseumState.CURATION: "Curadoria Interativa",
            MuseumState.IMMERSIVE_TOUR: "Tour Imersivo + Audioguia",
        }
        if state == MuseumState.IMMERSIVE_TOUR:
            progress = min(1.0, self.tour_time / self.tour_total_duration)
        else:
            progress = (self.active_index + 1) / len(self.objects)
        if state == MuseumState.CURATION:
            shortcuts = "←/→ Obra | 1 Geral | 2 Foco | L Raio | ESPAÇO Pausa | R Reiniciar | M Menu"
        else:
            shortcuts = "ESPAÇO Pausa/Retoma | R Reiniciar | M/ESC Menu"

        self.hud.draw(
            names[state],
            f"{self.active.title} — {self.active.author}",
            self.status,
            progress,
            shortcuts
        )
