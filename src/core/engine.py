"""Experiência unificada do Museu Virtual.

O controlador reúne a cena arquitetônica da AP1 com os modos, acervo e
serviços modulares da primeira implementação. A projeção é inteiramente
matemática e usa somente primitivas do Pygame.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame

from .state_machine import MuseumState, StateMachine
from ..audio.sound_manager import SoundManager
from ..graphics.raycaster import Raycaster
from ..museum.collisions import CollisionMap, Rect


@dataclass(frozen=True)
class Exhibit:
    title: str
    author: str
    room: str
    kind: str
    pos: tuple[float, float, float]
    audio: Optional[str] = None
    image: Optional[str] = None
    period: str = "Exposição de Computação Gráfica"


class Engine:
    """Loop, estados e renderização da única cena navegável do museu."""

    WIDTH, HEIGHT, FPS = 1150, 740, 60
    FLOOR_Y, CEILING_Y = -1.5, 4.2
    # Ordem do roteiro: as oito obras originais primeiro e as três da AP1 em seguida.
    EXHIBITS = (
        Exhibit("Mona Lisa", "Leonardo da Vinci", "Galeria Clássica", "painting", (-8, 1.4, 15), "01_mona_lisa.ogg", "Mona_Lisa.jpg", "c. 1503"),
        Exhibit("Autorretrato", "Rembrandt", "Galeria Clássica", "painting", (-2.7, 1.4, 15), "02_rembrandt.ogg", "Rembrandt.jpg", "c. 1660"),
        Exhibit("Guernica", "Pablo Picasso", "Galeria Clássica", "painting", (2.7, 1.4, 15), "03_guernica.ogg", "Guernica - Picasso.jpg", "1937"),
        Exhibit("Noite Estrelada", "Vincent van Gogh", "Galeria Clássica", "painting", (8, 1.4, 15), "04_noite_estrelada.ogg", "Noite_Estrelada.jpg", "1889"),
        Exhibit("Icosaedro Wireframe", "Geometria Computacional", "Galeria Matemática", "icosa", (-7, 0.4, 31), "05_icosaedro.ogg"),
        Exhibit("Espiral Áurea de Fibonacci", "Matemática", "Galeria Matemática", "spiral", (2, 0.3, 31), "06_espiral_aurea.ogg"),
        Exhibit("Servidor Monolítico", "Computação", "Galeria Tecnologia", "server", (13, 0.2, 31), "07_servidor_monolitico.ogg"),
        Exhibit("Fita Perfurada de Turing", "Alan Turing", "Galeria Tecnologia", "turing", (20, -0.2, 31), "08_tuning.ogg"),
        Exhibit("A Ilha dos Mortos", "Arnold Böcklin", "Galeria Antiguidade", "painting", (-17, 1.4, 15), None, "toteninsel.jpg", "1880, versão III"),
        Exhibit("Busto de Nefertiti", "Antigo Egito", "Galeria Antiguidade", "bust", (-20, 0.3, 9), None, None, "c. 1345 a.C."),
        Exhibit("Papiro de Ani / Livro dos Mortos", "Egito Antigo", "Galeria Antiguidade", "papyrus", (-14, -0.2, 9), None, "papyrus_ani.jpg", "c. 1250 a.C."),
    )

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Museu Virtual de Computação Gráfica")
        self.clock = pygame.time.Clock()
        self.state_machine = StateMachine()
        self.sound = SoundManager()
        self.font = pygame.font.Font(None, 22)
        self.small = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 42)
        self.images = self._load_images()
        self.nefertiti_mesh = self._load_nefertiti_mesh()
        self.active_index = 0
        self.tour_time = 0.0
        self.tour_durations = [self.sound.get_duration(e.audio) if e.audio else 4.0 for e in self.EXHIBITS]
        self.tour_total = sum(self.tour_durations)
        self.paused_from: Optional[MuseumState] = None
        self.status = "PRONTO"
        self.ray_enabled = True
        self.inspected_index: Optional[int] = None
        self.credits_return = MuseumState.MENU
        self.free_mode = False
        self.detail_focus = False
        self.image_cache = {}
        self.mouse_grabbed = False
        self.time = 0.0
        self.camera_pos = [0.0, 1.2, -8.0]
        self.camera_target = self.camera_pos[:]
        self.yaw = 0.0
        self.pitch = 0.0
        self.target_yaw = 0.0
        self.target_pitch = 0.0
        self.collision = self._build_collision_map()
        self.wall_segments = (
            ((-11, 5), (-11, 22)), ((-11, 25), (-11, 38)),
            ((8, 5), (8, 22)), ((8, 25), (8, 38)),
            ((-23, 22), (-13, 22)), ((-9, 22), (6, 22)), ((10, 22), (23, 22)),
        )

    def _build_collision_map(self):
        """Espelha a planta desenhada: paredes possuem vãos de portas reais."""
        walls = (
            Rect(-11.28, 5, -10.72, 22), Rect(-11.28, 25, -10.72, 38),
            Rect(7.72, 5, 8.28, 22), Rect(7.72, 25, 8.28, 38),
            Rect(-23, 21.72, -13, 22.28), Rect(-9, 21.72, 6, 22.28), Rect(10, 21.72, 23, 22.28),
        )
        exhibits = (
            Rect(-2, 4, 2, 8), Rect(-21.4, 7.4, -18.6, 10.8), Rect(-15.5, 7.3, -12.5, 10.7),
            Rect(-8.4, 29.3, -5.6, 32.7), Rect(.6, 29.3, 3.4, 32.7), Rect(11.6, 29, 14.4, 33), Rect(18.3, 29.7, 21.7, 32.3),
        )
        return CollisionMap(Rect(-23, -9, 23, 38), walls + exhibits)

    @property
    def active(self) -> Exhibit:
        return self.EXHIBITS[self.active_index]

    def _load_images(self):
        images = {}
        root = Path(__file__).resolve().parents[2] / "assets"
        for exhibit in self.EXHIBITS:
            if not exhibit.image or exhibit.image in images:
                continue
            path = root / "images" / exhibit.image
            if not path.exists():
                path = root / exhibit.image
            try:
                images[exhibit.image] = pygame.image.load(path).convert()
            except (pygame.error, OSError):
                images[exhibit.image] = None
        return images

    def _load_nefertiti_mesh(self):
        """Lê o OBJ opcional da AP1; uma malha pequena mantém a visita robusta."""
        path = Path(__file__).resolve().parents[2] / "assets" / "nefertiti_bust.obj"
        vertices, faces = [], []
        if path.exists():
            try:
                for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    values = line.split()
                    if values[:1] == ["v"] and len(values) >= 4:
                        vertices.append(tuple(map(float, values[1:4])))
                    elif values[:1] == ["f"] and len(values) >= 4:
                        faces.append(tuple(int(value.split("/")[0]) - 1 for value in values[1:]))
            except (OSError, ValueError):
                vertices, faces = [], []
        if vertices and faces:
            return vertices, faces
        print("[Museu] OBJ de Nefertiti ausente; usando malha procedural.")
        vertices = [(-.5,0,-.3),(.5,0,-.3),(.4,.7,-.25),(-.4,.7,-.25),
                    (-.5,0,.3),(.5,0,.3),(.4,.7,.25),(-.4,.7,.25),
                    (-.32,.7,-.22),(.32,.7,-.22),(.4,1.8,-.25),(-.4,1.8,-.25),
                    (-.32,.7,.22),(.32,.7,.22),(.4,1.8,.25),(-.4,1.8,.25)]
        faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(8,9,10,11),(12,15,14,13),(8,12,13,9),(11,10,14,15)]
        return vertices, faces

    def run(self):
        running = True
        while running:
            dt = min(0.05, self.clock.tick(self.FPS) / 1000.0)
            for event in pygame.event.get():
                running = self._event(event) and running
            if self.state_machine.current not in (MuseumState.MENU, MuseumState.CREDITS):
                self._update(dt)
            self._draw()
        self.sound.stop()
        pygame.quit()

    def _event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.MOUSEMOTION and self.free_mode and self.mouse_grabbed:
            self.yaw += event.rel[0] * .0035
            self.pitch = max(-1.0, min(1.0, self.pitch - event.rel[1] * .0035))
        if event.type != pygame.KEYDOWN:
            return True
        key, state = event.key, self.state_machine.current
        if key == pygame.K_ESCAPE:
            if state == MuseumState.MENU:
                return False
            if state == MuseumState.CREDITS:
                self._close_credits()
            else:
                self._menu()
        elif key == pygame.K_m:
            if state == MuseumState.MENU:
                self._start(MuseumState.EXPLORATION)
            else:
                self.free_mode = not self.free_mode
                self._set_mouse_capture(self.free_mode)
                self.status = "NAVEGAÇÃO LIVRE" if self.free_mode else "APRESENTAÇÃO"
        elif key == pygame.K_k:
            self._toggle_credits()
        elif state == MuseumState.CREDITS:
            self._close_credits()
        elif state == MuseumState.MENU:
            if key == pygame.K_1: self._start(MuseumState.BASIC_SCRIPT)
            elif key == pygame.K_2: self._start(MuseumState.CURATION)
            elif key == pygame.K_3: self._start(MuseumState.IMMERSIVE_TOUR)
            elif key == pygame.K_4: self._start(MuseumState.EXPLORATION)
            elif key == pygame.K_c: self._open_credits(MuseumState.MENU)
        elif key == pygame.K_r:
            self._start(MuseumState.EXPLORATION if self.free_mode else state)
        elif key == pygame.K_SPACE:
            self._toggle_pause()
        elif key in (pygame.K_n, pygame.K_RIGHT):
            self._select((self.active_index + 1) % len(self.EXHIBITS), focus=not self.free_mode)
        elif key in (pygame.K_b, pygame.K_LEFT):
            self._select((self.active_index - 1) % len(self.EXHIBITS), focus=not self.free_mode)
        elif key == pygame.K_c:
            self.detail_focus = not self.detail_focus
            self._focus_active(detail=self.detail_focus)
        elif key == pygame.K_l:
            self.ray_enabled = not self.ray_enabled
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            ranges = {pygame.K_1: 0, pygame.K_2: 8, pygame.K_3: 4, pygame.K_4: 6}
            self._select(ranges[key], focus=True)
        return True

    def _set_mouse_capture(self, captured):
        self.mouse_grabbed = captured
        pygame.event.set_grab(captured)
        pygame.mouse.set_visible(not captured)

    def _menu(self):
        self.sound.stop(); self._set_mouse_capture(False); self.free_mode = False
        self.state_machine.change(MuseumState.MENU); self.status = "PRONTO"; self.detail_focus = False

    def _start(self, state):
        self.sound.stop(); self.state_machine.change(state); self.paused_from = None
        self.active_index = 0; self.tour_time = 0; self.status = "EXECUTANDO"; self.free_mode = state == MuseumState.EXPLORATION; self.detail_focus = state == MuseumState.CURATION
        self.camera_pos = [0.0, 1.2, -8.0]; self.camera_target = self.camera_pos[:]; self.yaw = self.target_yaw = 0; self.pitch = self.target_pitch = 0
        self._set_mouse_capture(self.free_mode)
        if state == MuseumState.IMMERSIVE_TOUR:
            self.sound.play(self.active.audio)
        elif state in (MuseumState.BASIC_SCRIPT, MuseumState.CURATION):
            self._focus_active(detail=state == MuseumState.CURATION)

    def _open_credits(self, return_state):
        self.credits_return = return_state
        self._set_mouse_capture(False)
        self.state_machine.change(MuseumState.CREDITS)

    def _close_credits(self):
        self.state_machine.change(self.credits_return)
        self._set_mouse_capture(self.free_mode)

    def _toggle_credits(self):
        if self.state_machine.current == MuseumState.CREDITS:
            self._close_credits()
        else:
            self._open_credits(self.state_machine.current)

    def _toggle_pause(self):
        state = self.state_machine.current
        if state == MuseumState.PAUSED:
            self.state_machine.change(self.paused_from or MuseumState.EXPLORATION); self.status = "EXECUTANDO"; self.sound.resume()
        elif state != MuseumState.MENU:
            self.paused_from = state; self.state_machine.change(MuseumState.PAUSED); self.status = "PAUSADO"; self.sound.pause()

    def _select(self, index, focus=True):
        self.active_index = index
        if focus: self._focus_active(detail=True)
        if self.state_machine.current == MuseumState.IMMERSIVE_TOUR:
            self.sound.play(self.active.audio)

    def _focus_active(self, detail=False):
        x, y, z = self.active.pos
        distance = 5.5 if detail else 10.0
        self.camera_target = [x, max(.8, y + .3), z - distance]
        self.target_yaw = 0.0
        self.target_pitch = 0.0

    def _update(self, dt):
        self.time += dt
        state = self.state_machine.current
        if state == MuseumState.PAUSED: return
        if self.free_mode:
            self._move(dt)
            near = self._nearest_exhibit(4.0)
            if near is not None:
                self.active_index = near
        elif state == MuseumState.BASIC_SCRIPT:
            self.tour_time += dt; self.active_index = min(len(self.EXHIBITS)-1, int(self.tour_time / 3.0)); self._focus_active()
            if self.tour_time >= len(self.EXHIBITS) * 3:
                self.status = "CONCLUÍDO"; self.state_machine.change(MuseumState.COMPLETED)
        elif state == MuseumState.IMMERSIVE_TOUR:
            self.tour_time += dt
            passed = 0.0
            index = len(self.EXHIBITS)-1
            for i, duration in enumerate(self.tour_durations):
                passed += duration
                if self.tour_time < passed: index = i; break
            if index != self.active_index: self._select(index)
            self._focus_active(detail=True)
            if self.tour_time >= self.tour_total:
                self.status = "CONCLUÍDO"; self.state_machine.change(MuseumState.COMPLETED); self.sound.stop()
        self.inspected_index = self._inspect_hit() if self.ray_enabled else None
        blend = min(1.0, dt * 5.5)
        for i in range(3): self.camera_pos[i] += (self.camera_target[i] - self.camera_pos[i]) * blend
        self.yaw += (self.target_yaw - self.yaw) * blend
        self.pitch += (self.target_pitch - self.pitch) * blend

    def _move(self, dt):
        keys = pygame.key.get_pressed(); speed = 6.0 * dt
        forward = (math.sin(self.yaw), math.cos(self.yaw)); right = (math.cos(self.yaw), -math.sin(self.yaw))
        dx = dz = 0.0
        if keys[pygame.K_w]: dx += forward[0]*speed; dz += forward[1]*speed
        if keys[pygame.K_s]: dx -= forward[0]*speed; dz -= forward[1]*speed
        if keys[pygame.K_a]: dx -= right[0]*speed; dz -= right[1]*speed
        if keys[pygame.K_d]: dx += right[0]*speed; dz += right[1]*speed
        x, z = self.collision.move(self.camera_pos[0], self.camera_pos[2], dx, dz)
        self.camera_pos[0], self.camera_pos[2] = x, z
        self.camera_target = self.camera_pos[:]

    def _walkable(self, x, z):
        return self.collision.walkable(x, z)

    def _nearest_exhibit(self, radius):
        best, best_distance = None, radius
        for i, exhibit in enumerate(self.EXHIBITS):
            d = math.hypot(exhibit.pos[0]-self.camera_pos[0], exhibit.pos[2]-self.camera_pos[2])
            if d < best_distance: best, best_distance = i, d
        return best

    def _inspect_hit(self) -> Optional[int]:
        """Seleciona a primeira obra atravessada pelo raio horizontal da câmera."""
        origin = (self.camera_pos[0], self.camera_pos[2])
        direction = (math.sin(self.yaw), math.cos(self.yaw))
        best_index, best_t = None, float("inf")
        for index, exhibit in enumerate(self.EXHIBITS):
            half_x, half_z = (2.35, .45) if exhibit.kind == "painting" else (1.7, 1.35)
            bounds = (exhibit.pos[0] - half_x, exhibit.pos[2] - half_z,
                      exhibit.pos[0] + half_x, exhibit.pos[2] + half_z)
            if Raycaster.intersects(origin, direction, bounds):
                dx = exhibit.pos[0] - origin[0]
                dz = exhibit.pos[2] - origin[1]
                distance = dx * direction[0] + dz * direction[1]
                if 0 < distance < best_t:
                    best_index, best_t = index, distance
        return best_index

    def _project(self, p):
        dx, dy, dz = p[0]-self.camera_pos[0], p[1]-self.camera_pos[1], p[2]-self.camera_pos[2]
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x, z = dx*cy-dz*sy, dx*sy+dz*cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y, z = dy*cp-z*sp, dy*sp+z*cp
        if z <= .15: return None
        return (int(self.WIDTH/2 + 620*x/z), int(self.HEIGHT/2 - 620*y/z), z)

    def _poly(self, points, color, width=0):
        projected = [self._project(p) for p in points]
        if all(projected): pygame.draw.polygon(self.screen, color, [(p[0],p[1]) for p in projected], width)

    def _box(self, x,y,z,w,h,d, color):
        corners = [(x+a*w,y+b*h,z+c*d) for a,b,c in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
        faces = ((0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(3,2,6,7))
        for face in faces: self._poly([corners[i] for i in face], color, 1)

    def _draw(self):
        if self.state_machine.current == MuseumState.MENU:
            self._draw_menu()
        elif self.state_machine.current == MuseumState.CREDITS:
            self.screen.fill((9,14,23)); self._draw_credits()
        else:
            self.screen.fill((9,14,23)); self._draw_scene(); self._draw_hud()
        pygame.display.flip()

    def _draw_scene(self):
        # Piso, teto, paredes externas e divisórias formam uma planta contínua.
        self._poly([(-23,self.FLOOR_Y,-9),(23,self.FLOOR_Y,-9),(23,self.FLOOR_Y,38),(-23,self.FLOOR_Y,38)], (29,40,53))
        self._poly([(-23,self.CEILING_Y,-9),(23,self.CEILING_Y,-9),(23,self.CEILING_Y,38),(-23,self.CEILING_Y,38)], (20,27,39))
        for x in range(-22,24,4): self._poly([(x,self.FLOOR_Y,-9),(x,self.FLOOR_Y,38)], (50,65,80), 1)
        for z in range(-8,39,4): self._poly([(-23,self.FLOOR_Y,z),(23,self.FLOOR_Y,z)], (50,65,80), 1)
        outer_walls = [((-23,-9),(-23,38)), ((23,-9),(23,38)), ((-23,38),(23,38)), ((-23,-9),(23,-9))]
        for (x1,z1),(x2,z2) in outer_walls + list(self.wall_segments):
            self._poly([(x1,self.FLOOR_Y,z1),(x2,self.FLOOR_Y,z2),(x2,self.CEILING_Y,z2),(x1,self.CEILING_Y,z1)], (52,61,75))
        # Arcos/portais e sinalização da entrada.
        for x,z in ((-11,23),(8,23),(0,5)):
            self._box(x,2.2,z,.18,2,.35,(101,111,128))
        self._draw_world_label("ENTRADA • SAGUÃO CENTRAL", (0,2.8,-5), (255,207,80))
        for name, p, color in (("GALERIA CLÁSSICA",(0,3.2,10),(222,185,115)),("ANTIGUIDADE",(-17,3.2,10),(235,181,105)),("MATEMÁTICA",(-3,3.2,27),(150,220,205)),("TECNOLOGIA",(16,3.2,27),(125,195,245))): self._draw_world_label(name,p,color)
        for index, exhibit in sorted(enumerate(self.EXHIBITS), key=lambda item: -math.dist(self.camera_pos, item[1].pos)):
            self._draw_exhibit(exhibit, index == self.active_index or index == self.inspected_index)

    def _draw_exhibit(self, e, active):
        x,y,z=e.pos; glow = (255,215,100) if active else (125,145,165)
        # spot no teto e cone leve
        top, target = self._project((x,3.9,z-.5)), self._project((x,y,z))
        if top and target:
            pygame.draw.line(self.screen, glow, top[:2], target[:2], 2 if active else 1)
            pygame.draw.circle(self.screen, glow, top[:2], 5 if active else 3)
        if e.kind == "painting":
            self._box(x,y,z+.12,2.35,1.55,.10,(138,100,47) if active else (84,65,45))
            corners=[(x-2.1,y-1.3,z),(x+2.1,y-1.3,z),(x+2.1,y+1.3,z),(x-2.1,y+1.3,z)]
            pts=[self._project(p) for p in corners]
            image=self.images.get(e.image)
            if image and all(pts):
                minx,maxx=min(p[0] for p in pts),max(p[0] for p in pts); miny,maxy=min(p[1] for p in pts),max(p[1] for p in pts)
                if maxx-minx>8 and maxy-miny>8:
                    # Quantização evita redimensionamento em todos os frames durante uma transição.
                    size = (max(8, ((maxx-minx + 3) // 8) * 8), max(8, ((maxy-miny + 3) // 8) * 8))
                    cache_key = (e.image, size, active)
                    scaled = self.image_cache.get(cache_key)
                    if scaled is None:
                        scaled = pygame.transform.smoothscale(image, size)
                        if not active:
                            scaled.set_alpha(150)
                        self.image_cache[cache_key] = scaled
                    self.screen.blit(scaled,(minx,miny))
            else: self._poly(corners, (78,104,125) if active else (48,60,71))
        elif e.kind in ("icosa","spiral"):
            self._box(x,-.4,z,1.5,.65,1.5,(75,86,101))
            center=self._project((x,1,z))
            if center:
                if e.kind=="icosa":
                    pts=[]
                    for i in range(10):
                        a=self.time+i*math.tau/10; pts.append((center[0]+math.cos(a)*55,center[1]+math.sin(a)*55))
                    pygame.draw.lines(self.screen,glow,True,pts,2)
                else:
                    pts=[(center[0]+math.cos(self.time+t)*t*5,center[1]+math.sin(self.time+t)*t*5) for t in [i*.18 for i in range(55)]]; pygame.draw.lines(self.screen,(100,230,180),False,pts,2)
        elif e.kind=="server":
            self._box(x,1,z,1.3,2.2,.7,(35,53,70)); c=self._project((x,1,z-.75))
            if c:
                for row in range(6):
                    for col in range(3): pygame.draw.circle(self.screen,(70,int(150+90*(math.sin(self.time*4+row+col)+1)/2),160),(c[0]-24+col*24,c[1]-48+row*18),3)
        elif e.kind=="turing":
            self._box(x,.1,z,2.4,.55,.5,(66,76,89)); c=self._project((x,.1,z-.55))
            if c:
                offset = int((self.time * 24) % 14)
                for i in range(10): pygame.draw.circle(self.screen,(215,210,180),(c[0]-65 + i*14 + offset,c[1]),4)
        elif e.kind=="bust":
            self._box(x,-.5,z,1.25,.6,1.25,(170,175,180))
            vertices, faces = self.nefertiti_mesh
            angle = self.time * .22
            world = [(x + (vx * math.cos(angle) - vz * math.sin(angle))*.9, .1 + vy*.9,
                      z + (vx * math.sin(angle) + vz * math.cos(angle))*.9) for vx,vy,vz in vertices]
            for face in faces:
                if all(index < len(world) for index in face):
                    self._poly([world[index] for index in face], (220,198,161), 1)
        else:
            self._box(x,-.2,z,2.4,.7,1.3,(100,57,33)); self._box(x,.7,z,2.0,.25,1.0,(165,130,70))
        self._draw_world_label(e.title,(x,-1.0,z-1.1),glow)

    def _draw_world_label(self, text, pos, color):
        p=self._project(pos)
        if p and 0 <= p[0] < self.WIDTH: self._text(self.small,text,(p[0],p[1]),color,center=True)

    def _text(self,font,text,pos,color=(235,240,245),center=False):
        surf=font.render(text,True,color); self.screen.blit(surf,(pos[0]-surf.get_width()//2 if center else pos[0],pos[1]))

    def _draw_menu(self):
        self.screen.fill((10,16,27)); self._text(self.title_font,"MUSEU VIRTUAL DE COMPUTAÇÃO GRÁFICA",(self.WIDTH//2,92),(255,208,75),True)
        self._text(self.font,"Uma única cena 3D: saguão, galerias, corredores e acervo integrado.",(self.WIDTH//2,145),(205,218,235),True)
        options=(("[1]", "Roteiro Básico — visita automática pelas 11 obras"),("[2]","Curadoria Interativa — seleção, foco e raio de inspeção"),("[3]","Tour Imersivo — câmera, iluminação e audioguia"),("[4]","Navegação Livre — WASD + mouse, com colisões"),("[C]","Créditos"),("[ESC]","Sair"))
        for i,(key,label) in enumerate(options): self._text(self.font,f"{key}  {label}",(170,220+i*50),(255,210,110) if i<4 else (220,230,240))
        self._text(self.small,"Python + Pygame • projeção perspectiva matemática • sem OpenGL",(self.WIDTH//2,self.HEIGHT-65),(140,165,190),True)

    def _draw_hud(self):
        panel=pygame.Surface((self.WIDTH-32,76),pygame.SRCALPHA); panel.fill((9,15,25,220)); self.screen.blit(panel,(16,12))
        mode={MuseumState.EXPLORATION:"Navegação Livre",MuseumState.BASIC_SCRIPT:"Roteiro Básico",MuseumState.CURATION:"Curadoria Interativa",MuseumState.IMMERSIVE_TOUR:"Tour Imersivo",MuseumState.PAUSED:"Pausado",MuseumState.COMPLETED:"Concluído"}.get(self.state_machine.current,"Visita")
        self._text(self.font,"MUSEU VIRTUAL DE COMPUTAÇÃO GRÁFICA",(30,22),(255,207,80)); self._text(self.small,f"Modo: {mode} | Sala: {self.active.room} | Estado: {self.status}",(30,49))
        self._text(self.small,f"Obra: {self.active.title} — {self.active.author}",(550,49),(210,230,245))
        progress=(self.tour_time/self.tour_total if self.state_machine.current==MuseumState.IMMERSIVE_TOUR else (self.active_index+1)/len(self.EXHIBITS)); pygame.draw.rect(self.screen,(45,55,68),(30,self.HEIGHT-25,self.WIDTH-60,8)); pygame.draw.rect(self.screen,(100,195,225),(30,self.HEIGHT-25,int((self.WIDTH-60)*min(1,progress)),8))
        near=self._nearest_exhibit(4.0); hint="WASD + mouse: mover e olhar | M: alternar navegação/apresentação" if self.free_mode else "N/B: obras | C: foco | Espaço: pausar | R: reiniciar | M: navegação | K: créditos"
        if near is not None: hint=f"Próximo à obra: {self.active.title}. {hint}"
        self._text(self.small,hint,(30,self.HEIGHT-52),(255,224,160) if near is not None else (210,220,230))
        if self.ray_enabled:
            ray_color = (255,220,100) if self.inspected_index is not None else (150,170,190)
            pygame.draw.circle(self.screen, ray_color, (self.WIDTH//2,self.HEIGHT//2), 6, 1)
            if self.inspected_index is not None:
                self._text(self.small, f"Raio: {self.EXHIBITS[self.inspected_index].title}", (self.WIDTH//2 + 12, self.HEIGHT//2 - 9), ray_color)

    def _draw_credits(self):
        overlay=pygame.Surface((self.WIDTH,self.HEIGHT),pygame.SRCALPHA); overlay.fill((5,9,16,238)); self.screen.blit(overlay,(0,0))
        self._text(self.title_font,"CRÉDITOS E REFERÊNCIAS",(self.WIDTH//2,70),(255,207,80),True)
        lines=("Projeto acadêmico: Museu Virtual de Computação Gráfica","Tecnologia: Python 3 + Pygame; primitivas 2D e projeção perspectiva.","Acervo integrado: pinturas, matemática, tecnologia e antiguidade.","A Ilha dos Mortos — Arnold Böcklin (1880), domínio público.","Busto de Nefertiti — referência de digitalização Fraunhofer IGD / CultLab3D (CC BY-NC).","Papiro de Ani — British Museum / Wikimedia Commons.","Integrantes e papéis: preencher conforme a equipe acadêmica.","","K ou ESC — retornar ao museu.")
        for i,line in enumerate(lines): self._text(self.font,line,(100,160+i*42),(220,230,242))
