import pygame


class Menu:
    def __init__(self, renderer):
        self.renderer = renderer
        self.title_font = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 30)
        self.small = pygame.font.Font(None, 23)

    def draw(self):
        r = self.renderer
        r.clear()
        r.text(self.title_font, "MUSEU VIRTUAL DE COMPUTAÇÃO GRÁFICA",
               (55, 70), (240, 240, 245))
        options = [
            ("[1]", "Roteiro Básico"),
            ("[2]", "Curadoria Interativa"),
            ("[3]", "Tour Imersivo com Audioguia"),
            ("[C]", "Créditos"),
            ("[ESC / M]", "Sair / Menu"),
        ]
        y = 175
        for key, label in options:
            r.text(self.font, f"{key}  {label}", (85, y))
            y += 48
        r.text(self.small, "Python + Pygame | Projeção 3D matemática | Sem OpenGL",
               (55, r.height-55), (150,155,165))


class Credits:
    def __init__(self, renderer):
        self.renderer = renderer
        self.title_font = pygame.font.Font(None, 50)
        self.font = pygame.font.Font(None, 27)

    def draw(self):
        r = self.renderer
        r.clear()
        r.text(self.title_font, "CRÉDITOS E FICHA TÉCNICA", (60, 65))
        lines = [
            "Projeto: Mundo Virtual Animado",
            "Tema: Museu Virtual de Computação Gráfica",
            "Tecnologia: Python 3 + Pygame",
            "Renderização: primitivas 2D + projeção perspectiva matemática",
            "Arquitetura: POO, SRP, OCP, LSP e separação modular",
            "Áreas: Clássica, Matemática e Tecnológica",
            "",
            "Integrantes: preencher com os nomes do grupo",
            "Papéis: preencher conforme a divisão da equipe",
            "",
            "ESC / M — voltar ao menu",
        ]
        y = 145
        for line in lines:
            r.text(self.font, line, (75, y))
            y += 35
