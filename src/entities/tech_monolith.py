import math
from .base_object import BaseObject


class ServidorMonolitico(BaseObject):
    """Servidor estilizado com matriz de LEDs pulsantes."""

    def __init__(self, position):
        super().__init__("Servidor Monolítico", "Computação", position)
        self.phase = 0.0

    def update(self, dt):
        self.phase += dt * 4.0

    def draw(self, renderer, camera):
        cx = int(renderer.width*.5 + (self.x-camera.x)*camera.zoom)
        cy = int(renderer.height*.48 + (self.y-camera.y)*camera.zoom)
        w, h = int(190*camera.zoom), int(250*camera.zoom)
        body = (cx-w//2, cy-h//2, w, h)
        renderer.rect(body, (35,40,48))
        renderer.rect((cx-w//2+10,cy-h//2+10,w-20,h-20), (80,85,92), 2)

        for row in range(7):
            for col in range(4):
                pulse = (math.sin(self.phase + row*.8 + col*.45) + 1) * .5
                r = max(2, int((3 + pulse*4) * camera.zoom))
                x = cx - 58*camera.zoom + col*38*camera.zoom
                y = cy - 85*camera.zoom + row*27*camera.zoom
                renderer.circle((int(x),int(y)), r, (80, 230, 150))

        renderer.rect((cx-w//2-8,cy+h//2,w+16,18), (95,100,110))
        if self.highlighted:
            renderer.rect((cx-w//2-12,cy-h//2-12,w+24,h+24), (255,235,140), 3)

    def get_bounds(self):
        return (self.x-105,self.y-145,self.x+105,self.y+145)


class FitaTuring(BaseObject):
    """Fita perfurada/placa de silício minimalista."""

    def __init__(self, position):
        super().__init__("Fita Perfurada de Turing", "Alan Turing", position)

    def update(self, dt):
        pass

    def draw(self, renderer, camera):
        cx = int(renderer.width*.5 + (self.x-camera.x)*camera.zoom)
        cy = int(renderer.height*.48 + (self.y-camera.y)*camera.zoom)
        w, h = int(310*camera.zoom), int(115*camera.zoom)
        renderer.rect((cx-w//2,cy-h//2,w,h), (55,62,70))
        renderer.rect((cx-w//2+8,cy-h//2+8,w-16,h-16), (28,33,40), 2)
        for i in range(10):
            x = cx - w//2 + int((i+.5)*w/10)
            renderer.circle((x,cy), max(3,int(8*camera.zoom)), (210,210,190))
            renderer.circle((x,cy-h//4), max(2,int(5*camera.zoom)), (120,170,220))
            renderer.circle((x,cy+h//4), max(2,int(5*camera.zoom)), (120,170,220))

        if self.highlighted:
            renderer.rect((cx-w//2-10, cy-h//2-10, w+20, h+20), (255,235,140), 3)

    def get_bounds(self):
        return (self.x-165,self.y-70,self.x+165,self.y+70)
