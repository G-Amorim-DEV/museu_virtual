import pygame


class HUD:
    def __init__(self, renderer):
        self.renderer = renderer
        self.font = pygame.font.Font(None, 23)
        self.title = pygame.font.Font(None, 28)

    def draw(self, mode, artwork, status, progress, shortcuts):
        r = self.renderer
        bar = pygame.Rect(0, 0, r.width, 78)
        pygame.draw.rect(r.surface, (18, 21, 28), bar)
        r.text(self.title, "MUSEU VIRTUAL", (18, 10))
        r.text(self.font, f"Modo: {mode}", (18, 42))
        r.text(self.font, f"Obra: {artwork}", (235, 42))
        r.text(self.font, f"Status: {status}", (r.width-230, 10))

        x, y, w, h = 18, r.height-48, r.width-36, 12
        pygame.draw.rect(r.surface, (45, 48, 56), (x,y,w,h))
        pygame.draw.rect(r.surface, (110,190,220), (x,y,int(w*max(0,min(1,progress))),h))
        r.text(self.font, shortcuts, (18, r.height-78))
