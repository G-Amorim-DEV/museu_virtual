"""
===============================================================================
PROJETO AP 1 — COMPUTAÇÃO GRÁFICA E RA/RV (FACULDADE IMPACTA)
MUNDO VIRTUAL ANIMADO: MUSEU VIRTUAL DE HISTÓRIA DA ARTE E DA ANTIGUIDADE
===============================================================================
Variação Temática Escolhida: Variação 1 — Museu Virtual
Tecnologias: Python 3 + Pygame (sem OpenGL ou motores 3D)

Obras em Exposição:
  1. Sala Central (Pinturas):
     "A Ilha dos Mortos" (Die Toteninsel) — Arnold Böcklin (1880, Versão III)
     Moldura clássica 3D entalhada, tela rasterizada, iluminação de trilho LED.
  2. Sala Oeste (Esculturas da Antiguidade):
     "Busto de Nefertiti" — Antigo Egito (c. 1345 a.C., XVIII Dinastia)
     Malha 3D low-poly (Fraunhofer IGD CC BY-NC) sobre pedestal clássico de mármore.
  3. Sala Leste (Manuscritos e Documentos Históricos):
     "Papiro de Ani (Livro dos Mortos)" — Tebas, Egito Antigo (c. 1250 a.C.)
     Vitrine expositora 3D com mesa de mogno, redoma de vidro e cilindros de papiro.

Modos de Operação (Alternáveis por [M]):
  - MODO APRESENTAÇÃO AP1 (Comandos Discretos / Avaliação Acadêmica):
    [ESPAÇO] : Iniciar / Pausar / Retomar Visita Guiada
    [R]       : Reiniciar visita, estados e posições
    [C]       : Alternar Modo de Câmera (Plano Geral <-> Foco Animado na Obra)
    [1, 2, 3] : Focar e transitar diretamente para a Sala 1, Sala 2 ou Sala 3
    [N] / [B] : Avançar / Voltar manualmente entre as obras
    [K]       : Alternar Tela de Créditos do Grupo (4 Integrantes + Referências)
    [ESC]     : Sair da aplicação

  - MODO NAVEGAÇÃO LIVRE DO VISITANTE:
    [W] / [S] : Mover para frente / trás na direção da visão
    [A] / [D] : Deslocar (strafe) para esquerda / direita
    [Mouse]   : Olhar livremente em 360° (Pitch e Yaw — cima, baixo, lados)
    Colisões  : Não atravessa paredes externas, divisórias nem entra nos pedestais
    Proximidade: Ao se aproximar de uma obra, surge a placa informativa didática!
===============================================================================
"""

import math
import os
import sys
import pygame

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES GERAIS E PALETA DE CORES DO MUSEU
# -----------------------------------------------------------------------------
LARGURA, ALTURA = 1150, 740
FPS = 60

# Diretório base e caminhos de assets
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_ASSETS = os.path.join(DIR_BASE, "assets")
PATH_TOTENINSEL = os.path.join(DIR_ASSETS, "toteninsel.jpg")
PATH_PAPYRUS    = os.path.join(DIR_ASSETS, "papyrus_ani.jpg")
PATH_NEFERTITI  = os.path.join(DIR_ASSETS, "nefertiti_bust.obj")

# Cores Arquitetônicas e de Iluminação (RGB)
COR_FUNDO          = (10, 14, 22)       # Azul escuro muito suave (ambiente de galeria)
COR_PISO_GRADE     = (28, 38, 54)       # Grade de mármore do piso
COR_PISO_LINHAS    = (45, 60, 85)       # Contorno dos ladrilhos do piso
COR_PAREDE         = (36, 44, 58)       # Paredes principais do museu
COR_PAREDE_BORDA   = (55, 68, 88)       # Contorno arquitetônico das paredes
COR_RODAPE         = (20, 25, 34)       # Rodapé e sancas
COR_PORTAL         = (85, 100, 125)     # Moldura dos portais/arcos de passagem

# Cores de Objetos
COR_MARMORE_PED    = (165, 172, 185)    # Pedestal de mármore claro (Sala 2)
COR_MOGNO_VITRINE  = (85, 45, 25)       # Madeira nobre mogno (Sala 3)
COR_VIDRO_BORDA    = (160, 220, 240)    # Arestas da redoma de vidro
COR_VIDRO_FACE     = (180, 230, 255, 40)# Vidro transparente com alpha
COR_MOLDURA_OURO   = (195, 155, 45)     # Moldura clássica dourada (Sala 1)
COR_PLACA_BRONZE   = (175, 130, 40)     # Placas de identificação
COR_TEXTO_PLACA    = (255, 245, 220)    # Texto da placa física

# Cores de Iluminação e HUD
COR_LUZ_LED        = (255, 250, 220)    # LED quente para iluminação de obras
COR_CONE_LUZ       = (255, 245, 190, 30)# Feixe translúcido do cone de luz
COR_TEXTO_HUD      = (240, 245, 255)    # Texto principal
COR_DESTAQUE_HUD   = (255, 205, 50)     # Dourado para ênfase
COR_HUD_BG         = (14, 20, 32, 220)  # Fundo translúcido do HUD


# -----------------------------------------------------------------------------
# 2. FUNÇÕES VETORIAIS E MATEMÁTICA DA CÂMERA 3D (PROJEÇÃO PERSPECTIVA)
# -----------------------------------------------------------------------------
def vet_sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])

def vet_produto_vetorial(u, v):
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )

def vet_produto_escalar(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def vet_normalizar(v):
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag < 1e-7:
        return (0.0, 1.0, 0.0)
    return (v[0]/mag, v[1]/mag, v[2]/mag)

def rotacionar_ponto(p, rot):
    """Aplica rotação sequencial nos eixos X, Y e Z."""
    x, y, z = p
    rx, ry, rz = rot
    if rx != 0:
        cx, sx = math.cos(rx), math.sin(rx)
        y, z = y*cx - z*sx, y*sx + z*cx
    if ry != 0:
        cy, sy = math.cos(ry), math.sin(ry)
        x, z = x*cy + z*sy, -x*sy + z*cy
    if rz != 0:
        cz, sz = math.cos(rz), math.sin(rz)
        x, y = x*cz - y*sz, x*sz + y*cz
    return (x, y, z)

def transformar_vertice(p, pos, rot, escala):
    """Transformação local do objeto: Escala -> Rotação -> Translação no mundo."""
    x = p[0] * escala[0]
    y = p[1] * escala[1]
    z = p[2] * escala[2]
    rx, ry, rz = rotacionar_ponto((x, y, z), rot)
    return (rx + pos[0], ry + pos[1], rz + pos[2])

def projetar_para_camera(ponto_mundo, cam_pos, cam_yaw, cam_pitch, foco=620.0):
    """
    Transforma coordenadas do Mundo para o Espaço da Câmera (com rotação Yaw e Pitch)
    e em seguida aplica a Projeção Perspectiva para Coordenadas de Tela (2D).
    Retorna: (x_tela, y_tela, z_cam) ou None caso o ponto esteja atrás da câmera.
    """
    # 1. Translação em relação à câmera
    dx = ponto_mundo[0] - cam_pos[0]
    dy = ponto_mundo[1] - cam_pos[1]
    dz = ponto_mundo[2] - cam_pos[2]

    # 2. Rotação de Yaw (olhar esquerda / direita em torno do eixo Y)
    cy, sy = math.cos(cam_yaw), math.sin(cam_yaw)
    x1 = dx * cy - dz * sy
    z1 = dx * sy + dz * cy
    y1 = dy

    # 3. Rotação de Pitch (olhar cima / baixo em torno do eixo X)
    cp, sp = math.cos(cam_pitch), math.sin(cam_pitch)
    y_cam = y1 * cp - z1 * sp
    z_cam = y1 * sp + z1 * cp
    x_cam = x1

    # Plano de corte próximo (near clipping plane)
    if z_cam <= 0.25:
        return None

    tela_x = (LARGURA / 2.0) + (foco * x_cam / z_cam)
    tela_y = (ALTURA / 2.0)  - (foco * y_cam / z_cam)
    return (int(tela_x), int(tela_y), z_cam)


# -----------------------------------------------------------------------------
# 3. CARREGADOR DE MODELOS 3D E MALHAS GEOMÉTRICAS
# -----------------------------------------------------------------------------
def carregar_obj(caminho):
    """Carrega uma malha 3D simples em formato OBJ."""
    vertices = []
    faces = []
    if not os.path.exists(caminho):
        return None, None

    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("v "):
                partes = linha.split()
                vertices.append((float(partes[1]), float(partes[2]), float(partes[3])))
            elif linha.startswith("f "):
                partes = linha.split()[1:]
                indices = [int(p.split("/")[0]) - 1 for p in partes]
                if len(indices) >= 3:
                    faces.append(tuple(indices))
    return vertices, faces

def gerar_malha_busto_fallback():
    """Gera uma geometria de busto escultórico procedural caso o OBJ não esteja presente."""
    verts = [
        # Base e tronco
        (-0.5, 0.0, -0.3), (0.5, 0.0, -0.3), (0.4, 0.6, -0.2), (-0.4, 0.6, -0.2),
        (-0.5, 0.0,  0.3), (0.5, 0.0,  0.3), (0.4, 0.6,  0.2), (-0.4, 0.6,  0.2),
        # Pescoço e queixo
        (-0.2, 0.6, -0.15), (0.2, 0.6, -0.15), (0.2, 1.0, -0.15), (-0.2, 1.0, -0.15),
        (-0.2, 0.6,  0.15), (0.2, 0.6,  0.15), (0.2, 1.0,  0.15), (-0.2, 1.0,  0.15),
        # Cabeça / Coroa de Nefertiti
        (-0.35, 1.0, -0.2), (0.35, 1.0, -0.2), (0.45, 1.8, -0.35), (-0.45, 1.8, -0.35),
        (-0.35, 1.0,  0.2), (0.35, 1.0,  0.2), (0.45, 1.8,  0.35), (-0.45, 1.8,  0.35),
        ( 0.0,  1.9,  0.0) # Topo da coroa
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4),
        (8, 9, 10, 11), (12, 15, 14, 13), (8, 12, 13, 9), (11, 10, 14, 15),
        (16, 17, 18, 19), (20, 23, 22, 21), (16, 20, 21, 17), (19, 18, 22, 23),
        (18, 19, 24), (19, 23, 24), (23, 22, 24), (22, 18, 24)
    ]
    return verts, faces

# Definição do Modelo do Pedestal (Base, Coluna e Capitel - Instanciável)
VERTICES_PEDESTAL_COMPLETO = [
    # 1. Base Inferior Larga (0 a 7)
    (-0.9, 0.0, -0.9), ( 0.9, 0.0, -0.9), ( 0.9, 0.3, -0.9), (-0.9, 0.3, -0.9),
    (-0.9, 0.0,  0.9), ( 0.9, 0.0,  0.9), ( 0.9, 0.3,  0.9), (-0.9, 0.3,  0.9),
    # 2. Coluna Central (8 a 15)
    (-0.6, 0.3, -0.6), ( 0.6, 0.3, -0.6), ( 0.6, 1.5, -0.6), (-0.6, 1.5, -0.6),
    (-0.6, 0.3,  0.6), ( 0.6, 0.3,  0.6), ( 0.6, 1.5,  0.6), (-0.6, 1.5,  0.6),
    # 3. Capitel Superior (16 a 23)
    (-0.8, 1.5, -0.8), ( 0.8, 1.5, -0.8), ( 0.8, 1.7, -0.8), (-0.8, 1.7, -0.8),
    (-0.8, 1.5,  0.8), ( 0.8, 1.5,  0.8), ( 0.8, 1.7,  0.8), (-0.8, 1.7,  0.8)
]
FACES_PEDESTAL_COMPLETO = [
    # Base
    (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4),
    # Coluna
    (8, 9, 10, 11), (12, 15, 14, 13), (8, 12, 13, 9), (11, 10, 14, 15), (9, 13, 14, 10), (8, 11, 15, 12),
    # Capitel
    (16, 17, 18, 19), (20, 23, 22, 21), (16, 20, 21, 17), (19, 18, 22, 23), (17, 21, 22, 18), (16, 19, 23, 20)
]

# Definição do Modelo da Moldura 3D de A Ilha dos Mortos (Sala 1)
VERTICES_MOLDURA_PINTURA = [
    # Moldura Externa (0 a 7)
    (-2.8, -1.6, -0.15), ( 2.8, -1.6, -0.15), ( 2.8,  1.6, -0.15), (-2.8,  1.6, -0.15),
    (-2.8, -1.6,  0.10), ( 2.8, -1.6,  0.10), ( 2.8,  1.6,  0.10), (-2.8,  1.6,  0.10),
    # Friso Interno de Apoio da Tela (8 a 11)
    (-2.4, -1.3, 0.05), ( 2.4, -1.3, 0.05), ( 2.4,  1.3, 0.05), (-2.4,  1.3, 0.05),
    # Haste da Luminária Superior (12 a 15)
    (-0.8, 1.6, 0.0), (0.8, 1.6, 0.0), (0.8, 2.0, 0.5), (-0.8, 2.0, 0.5)
]
FACES_MOLDURA_PINTURA = [
    # Borda externa
    (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4),
    # Tela frontal
    (8, 9, 10, 11),
    # Luminária superior
    (12, 13, 14, 15)
]

# Definição do Modelo da Vitrine e Suporte de Manuscritos (Sala 3)
VERTICES_VITRINE_MANUSCRITO = [
    # Mesa de Madeira / Gabinete Inferior (0 a 7)
    (-1.6, 0.0, -1.0), ( 1.6, 0.0, -1.0), ( 1.6, 1.0, -1.0), (-1.6, 1.0, -1.0),
    (-1.6, 0.0,  1.0), ( 1.6, 0.0,  1.0), ( 1.6, 1.0,  1.0), (-1.6, 1.0,  1.0),
    # Tampo Inclinado de Apoio ao Papiro (8 a 11)
    (-1.4, 1.0, -0.8), ( 1.4, 1.0, -0.8), ( 1.4, 1.3,  0.7), (-1.4, 1.3,  0.7),
    # Cilindros/Hastes Laterais do Papiro (12 a 15)
    (-1.45, 1.0, -0.85), (-1.45, 1.3, 0.75), ( 1.45, 1.0, -0.85), ( 1.45, 1.3, 0.75),
    # Cúpula / Redoma de Vidro Transparente 3D (16 a 23)
    (-1.5, 1.0, -0.9), ( 1.5, 1.0, -0.9), ( 1.5, 1.7, -0.9), (-1.5, 1.7, -0.9),
    (-1.5, 1.0,  0.9), ( 1.5, 1.0,  0.9), ( 1.5, 1.7,  0.9), (-1.5, 1.7,  0.9)
]
FACES_VITRINE_MANUSCRITO = [
    # Gabinete de Madeira
    (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4),
    # Tampo Inclinado com Manuscrito
    (8, 9, 10, 11),
    # Redoma de Vidro (Faces translúcidas)
    (16, 17, 18, 19), (20, 23, 22, 21), (16, 20, 21, 17), (19, 18, 22, 23), (17, 21, 22, 18), (16, 19, 23, 20)
]

# Objeto Simples sem partes: Placa de Identificação de Bronze (Requisito 3.2)
VERTICES_PLACA = [
    (-0.7, -0.25, 0.0), (0.7, -0.25, 0.0), (0.7, 0.25, 0.0), (-0.7, 0.25, 0.0)
]
FACES_PLACA = [(0, 1, 2, 3)]


# -----------------------------------------------------------------------------
# 4. CLASSE DE OBJETO 3D E COMPOSIÇÃO DE CENA
# -----------------------------------------------------------------------------
class Objeto3D:
    def __init__(self, nome, vertices, faces, pos, escala=(1.0, 1.0, 1.0), rot=(0.0, 0.0, 0.0),
                 cor_base=(160, 160, 160), eh_vidro=False, eh_superficie_arte=False):
        self.nome = nome
        self.vertices = vertices
        self.faces = faces
        self.pos_base = list(pos)
        self.pos = list(pos)
        self.escala_base = list(escala)
        self.escala = list(escala)
        self.rot_base = list(rot)
        self.rot = list(rot)
        self.cor_base = cor_base
        self.eh_vidro = eh_vidro
        self.eh_superficie_arte = eh_superficie_arte
        self.iluminado = False # Flag para teste de iluminação binária (Requisito 3.9)

    def resetar(self):
        self.pos = list(self.pos_base)
        self.escala = list(self.escala_base)
        self.rot = list(self.rot_base)
        self.iluminado = False


# -----------------------------------------------------------------------------
# 5. GERENCIADOR DO MUSEU VIRTUAL 3D (ARQUITETURA COMPLETA)
# -----------------------------------------------------------------------------
class MuseuVirtual3D:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Museu Virtual 3D — História da Arte e da Antiguidade (AP1)")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()

        # Fontes Tipográficas
        self.fonte_titulo = pygame.font.SysFont("Georgia", 22, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("Arial", 16, bold=True)
        self.fonte_hud = pygame.font.SysFont("Arial", 15)
        self.fonte_pequena = pygame.font.SysFont("Arial", 12)
        self.fonte_placa = pygame.font.SysFont("Georgia", 11, bold=True)

        # Máquina de Estados da Visita Guiada (Requisito Obrigatório AP1)
        self.ESTADO_PARADO = "PARADO"
        self.ESTADO_EXECUTANDO = "EXECUTANDO"
        self.ESTADO_PAUSADO = "PAUSADO"
        self.ESTADO_CONCLUIDO = "CONCLUIDO"
        self.estado_atual = self.ESTADO_PARADO

        # Modos de Apresentação e Navegação da Câmera
        self.MODO_APRESENTACAO = "APRESENTAÇÃO AP1 (DISCRETO)"
        self.MODO_NAVEGACAO_LIVRE = "NAVEGAÇÃO LIVRE (WASD + MOUSE)"
        self.modo_operacao = self.MODO_APRESENTACAO

        # Submodos de Câmera da Apresentação
        self.MODO_CAM_GERAL = "PLANO_GERAL"
        self.MODO_CAM_FOCO  = "FOCO_ANIMADO"
        self.submodo_cam = self.MODO_CAM_GERAL

        # Coordenadas e Ângulos da Câmera
        self.cam_pos_geral = [0.0, 1.8, -1.8]
        self.cam_pos_atual = list(self.cam_pos_geral)
        self.cam_pos_alvo  = list(self.cam_pos_geral)
        self.cam_yaw_atual = 0.0
        self.cam_yaw_alvo  = 0.0
        self.cam_pitch_atual = 0.0
        self.cam_pitch_alvo  = 0.0

        # Mouse look
        self.mouse_arrastando = False
        self.mouse_ultimo_pos = (0, 0)
        self.sensibilidade_mouse = 0.0035

        # Cronômetro e Etapas
        self.obra_foco_idx = 0
        self.tempo_animacao = 0.0
        self.duracao_etapa = 7.5 # Segundos por sala na visita guiada
        self.exibir_creditos = False

        # Carregar Texturas/Imagens das Obras de Arte
        self.carregar_imagens_obras()

        # Inicializar Cena 3D, Galerias, Modelos e Spots
        self.inicializar_obras_e_galerias()

    # -------------------------------------------------------------------------
    # INICIALIZAÇÃO DE ASSETS E MATERIAIS
    # -------------------------------------------------------------------------
    def carregar_imagens_obras(self):
        """Carrega e prepara as superfícies das obras históricas em domínio público."""
        # 1. A Ilha dos Mortos
        if os.path.exists(PATH_TOTENINSEL):
            img_bruta = pygame.image.load(PATH_TOTENINSEL).convert()
            # Escala prévia para manter alto desempenho no laço principal
            self.img_toteninsel = pygame.transform.smoothscale(img_bruta, (860, 480))
        else:
            self.img_toteninsel = pygame.Surface((860, 480))
            self.img_toteninsel.fill((20, 30, 45))
            pygame.draw.circle(self.img_toteninsel, (200, 220, 255), (430, 200), 70)

        # 2. Papiro de Ani (Livro dos Mortos)
        if os.path.exists(PATH_PAPYRUS):
            img_bruta = pygame.image.load(PATH_PAPYRUS).convert()
            self.img_papiro = pygame.transform.smoothscale(img_bruta, (780, 420))
        else:
            self.img_papiro = pygame.Surface((780, 420))
            self.img_papiro.fill((210, 180, 130))

    def inicializar_obras_e_galerias(self):
        """Monta a planta baixa do museu com 3 salas temáticas e objetos 3D."""
        # Metadados Didáticos e Históricos das Três Obras (Itens 2 e 7 do Prompt)
        self.info_obras = [
            {
                "sala": "SALA 1: GALERIA DE PINTURAS SIMBOLISTAS",
                "titulo": "A Ilha dos Mortos (Die Toteninsel)",
                "artista": "Arnold Böcklin (1827–1901)",
                "periodo": "Simbolismo (Século XIX)",
                "data": "1880 (Versão III)",
                "material": "Óleo sobre tela de madeira (111 × 155 cm)",
                "localizacao": "Alte Nationalgalerie, Berlim",
                "desc": "Obra-prima mística retratando uma ilha rochosa cercada por ciprestes escuros e um barco fúnebre conduzido por Caronte em direção aos portais da eternidade.",
                "cor_spot": (255, 245, 200),
                "pos_foco_cam": [0.0, 1.7, 7.5],
                "yaw_foco": 0.0,
                "pitch_foco": 0.04
            },
            {
                "sala": "SALA 2: GALERIA DE ESCULTURAS DA ANTIGUIDADE",
                "titulo": "Busto de Nefertiti",
                "artista": "Tutmés (Escultor Real da Corte de Amarna)",
                "periodo": "Novo Império Egípcio (XVIII Dinastia)",
                "data": "c. 1345 a.C.",
                "material": "Calcário revestido de estuque policromado (48 cm)",
                "localizacao": "Museu Egípcio e Coleção de Papiros, Berlim",
                "desc": "Ícone supremo da arte e da elegância clássica egípcia, retratando Nefertiti com sua emblemática coroa azul cilíndrica e uraeus real.",
                "cor_spot": (255, 250, 220),
                "pos_foco_cam": [-8.0, 1.4, 5.0],
                "yaw_foco": 0.0,
                "pitch_foco": 0.02
            },
            {
                "sala": "SALA 3: GALERIA DE MANUSCRITOS E ANTIGUIDADES",
                "titulo": "Papiro de Ani (Livro dos Mortos)",
                "artista": "Escribas Teólogos e Iluminadores de Tebas",
                "periodo": "Império Novo do Antigo Egito",
                "data": "c. 1250 a.C. (XIX Dinastia)",
                "material": "Papiro manuscrito com escrita hieroglífica e vinhetas (23,6 m)",
                "localizacao": "British Museum, Londres",
                "desc": "O mais completo e ricamente iluminado rolo funerário sobrevivente da antiguidade, contendo hinos, litanias e o julgamento da alma (pesagem do coração).",
                "cor_spot": (255, 240, 195),
                "pos_foco_cam": [8.0, 1.7, 5.5],
                "yaw_foco": 0.0,
                "pitch_foco": -0.22 # Câmera angulada suavemente para baixo para ver a vitrine
            }
        ]

        # 3 Luminárias LED no Teto com feixes cônicos (Sala 1, Sala 2, Sala 3)
        self.spots_led = [
            {"pos": [ 0.0, 3.8, 11.2], "alvo": [ 0.0, 1.6, 12.8], "cor": self.info_obras[0]["cor_spot"], "raio_cone": 2.4},
            {"pos": [-8.0, 3.8,  8.5], "alvo": [-8.0, 1.4,  8.5], "cor": self.info_obras[1]["cor_spot"], "raio_cone": 2.0},
            {"pos": [ 8.0, 3.8,  8.5], "alvo": [ 8.0, 1.1,  8.5], "cor": self.info_obras[2]["cor_spot"], "raio_cone": 2.2}
        ]

        # ---------------------------------------------------------------------
        # CRIAÇÃO DOS OBJETOS DA CENA (Atende ao Requisito 3 da AP1)
        # ---------------------------------------------------------------------
        self.objetos = []

        # 1. Três Instâncias de Pedestais com parâmetros diferentes (Requisito 3.1):
        # Pedestal 1: Sala de Pinturas (suporte decorativo/banco central)
        ped1 = Objeto3D("Pedestal_Sala1", VERTICES_PEDESTAL_COMPLETO, FACES_PEDESTAL_COMPLETO,
                        pos=(0.0, -1.2, 5.0), escala=(0.8, 0.45, 0.8), cor_base=(100, 110, 130))
        # Pedestal 2: Sala de Esculturas (pedestal de mármore esbelto para Nefertiti)
        ped2 = Objeto3D("Pedestal_Sala2", VERTICES_PEDESTAL_COMPLETO, FACES_PEDESTAL_COMPLETO,
                        pos=(-8.0, -1.2, 8.5), escala=(1.0, 0.9, 1.0), cor_base=COR_MARMORE_PED)
        # Pedestal 3: Sala de Manuscritos (base de apoio arquitetônica)
        ped3 = Objeto3D("Pedestal_Sala3", VERTICES_PEDESTAL_COMPLETO, FACES_PEDESTAL_COMPLETO,
                        pos=(8.0, -1.2, 11.5), escala=(0.7, 0.7, 0.7), cor_base=(110, 80, 60))
        self.pedestais = [ped1, ped2, ped3]
        self.objetos.extend(self.pedestais)

        # 2. Obra 1 (Pintura): Moldura 3D clássica na parede norte da Sala Central
        self.moldura_toteninsel = Objeto3D(
            "Moldura_Toteninsel", VERTICES_MOLDURA_PINTURA, FACES_MOLDURA_PINTURA,
            pos=(0.0, 1.6, 12.8), escala=(1.0, 1.0, 1.0), cor_base=COR_MOLDURA_OURO, eh_superficie_arte=True
        )
        self.objetos.append(self.moldura_toteninsel)

        # 3. Obra 2 (Escultura): Busto de Nefertiti na Sala Oeste
        # Carrega o OBJ otimizado (452 vértices / 894 faces) ou fallback
        v_nef, f_nef = carregar_obj(PATH_NEFERTITI)
        if v_nef is None or len(v_nef) == 0:
            v_nef, f_nef = gerar_malha_busto_fallback()
        
        # Posicionada no topo do pedestal da Sala 2 (y_pedestal topo = -1.2 + 1.7*0.9 ≈ 0.33)
        self.busto_nefertiti = Objeto3D(
            "Busto_Nefertiti", v_nef, f_nef,
            pos=(-8.0, 0.35, 8.5), escala=(0.85, 0.85, 0.85), cor_base=(215, 195, 160)
        )
        self.objetos.append(self.busto_nefertiti)

        # 4. Obra 3 (Manuscrito): Vitrine de Madeira Nobre e Redoma 3D na Sala Leste
        # Objeto Composto por Múltiplas Estruturas (Requisito 3.3)
        self.vitrine_papiro = Objeto3D(
            "Vitrine_Papiro", VERTICES_VITRINE_MANUSCRITO, FACES_VITRINE_MANUSCRITO,
            pos=(8.0, -1.2, 8.5), escala=(1.1, 1.0, 1.1), cor_base=COR_MOGNO_VITRINE, eh_superficie_arte=True
        )
        self.objetos.append(self.vitrine_papiro)

        # 5. Objetos Simples sem partes: Três Placas de Identificação em Bronze (Requisito 3.2)
        placa1 = Objeto3D("Placa_Sala1", VERTICES_PLACA, FACES_PLACA, pos=(0.0, -0.25, 12.75), escala=(0.8, 0.8, 1.0), cor_base=COR_PLACA_BRONZE)
        placa2 = Objeto3D("Placa_Sala2", VERTICES_PLACA, FACES_PLACA, pos=(-8.0, -0.65, 7.55), escala=(0.7, 0.7, 1.0), cor_base=COR_PLACA_BRONZE)
        placa3 = Objeto3D("Placa_Sala3", VERTICES_PLACA, FACES_PLACA, pos=(8.0, -0.15, 7.35), escala=(0.7, 0.7, 1.0), cor_base=COR_PLACA_BRONZE)
        self.placas = [placa1, placa2, placa3]
        self.objetos.extend(self.placas)

        # 6. Paredes e Portais Arquitetônicos das Salas
        self.inicializar_arquitetura_paredes()

    def inicializar_arquitetura_paredes(self):
        """Gera as faces 3D das paredes externas e divisórias com portais/arcos."""
        # Paredes delimitadoras:
        # Paredes de Fundo (Norte: z = 13.5), Laterais (x = -13.0 e +13.0), Sul (z = -3.5)
        # Divisórias entre salas em x = -4.5 e x = +4.5 com abertura de passagem (z entre 2.5 e 7.0)
        y_chao, y_teto = -1.2, 4.0
        self.paredes_faces = [
            # Parede Norte Central (atrás de Toteninsel)
            [(-4.5, y_chao, 13.5), (4.5, y_chao, 13.5), (4.5, y_teto, 13.5), (-4.5, y_teto, 13.5)],
            # Parede Norte Sala 2 (Esculturas)
            [(-13.0, y_chao, 13.5), (-4.5, y_chao, 13.5), (-4.5, y_teto, 13.5), (-13.0, y_teto, 13.5)],
            # Parede Norte Sala 3 (Manuscritos)
            [(4.5, y_chao, 13.5), (13.0, y_chao, 13.5), (13.0, y_teto, 13.5), (4.5, y_teto, 13.5)],
            # Paredes Laterais Externas
            [(-13.0, y_chao, -3.5), (-13.0, y_chao, 13.5), (-13.0, y_teto, 13.5), (-13.0, y_teto, -3.5)],
            [(13.0, y_chao, 13.5), (13.0, y_chao, -3.5), (13.0, y_teto, -3.5), (13.0, y_teto, 13.5)],
            # Parede Sul (Frente da Galeria)
            [(13.0, y_chao, -3.5), (-13.0, y_chao, -3.5), (-13.0, y_teto, -3.5), (13.0, y_teto, -3.5)],
            # Divisória Oeste: Trecho Fundo (z: 7.0 a 13.5)
            [(-4.5, y_chao, 7.0), (-4.5, y_chao, 13.5), (-4.5, y_teto, 13.5), (-4.5, y_teto, 7.0)],
            # Divisória Oeste: Trecho Frente (z: -3.5 a 2.5)
            [(-4.5, y_chao, -3.5), (-4.5, y_chao, 2.5), (-4.5, y_teto, 2.5), (-4.5, y_teto, -3.5)],
            # Portal Oeste: Viga Superior do Arco (z: 2.5 a 7.0, y: 2.8 a 4.0)
            [(-4.5, 2.8, 2.5), (-4.5, 2.8, 7.0), (-4.5, y_teto, 7.0), (-4.5, y_teto, 2.5)],
            # Divisória Leste: Trecho Fundo (z: 7.0 a 13.5)
            [(4.5, y_chao, 13.5), (4.5, y_chao, 7.0), (4.5, y_teto, 7.0), (4.5, y_teto, 13.5)],
            # Divisória Leste: Trecho Frente (z: -3.5 a 2.5)
            [(4.5, y_chao, 2.5), (4.5, y_chao, -3.5), (4.5, y_teto, -3.5), (4.5, y_teto, 2.5)],
            # Portal Leste: Viga Superior do Arco (z: 2.5 a 7.0, y: 2.8 a 4.0)
            [(4.5, 2.8, 7.0), (4.5, 2.8, 2.5), (4.5, y_teto, 2.5), (4.5, y_teto, 7.0)],
        ]

    # -------------------------------------------------------------------------
    # REINICIALIZAÇÃO DO MUSEU
    # -------------------------------------------------------------------------
    def reiniciar(self):
        """Reseta máquinas de estados, tempos, objetos e posicionamentos."""
        self.estado_atual = self.ESTADO_PARADO
        self.tempo_animacao = 0.0
        self.obra_foco_idx = 0
        self.submodo_cam = self.MODO_CAM_GERAL
        self.cam_pos_alvo = list(self.cam_pos_geral)
        self.cam_pos_atual = list(self.cam_pos_geral)
        self.cam_yaw_alvo = 0.0
        self.cam_yaw_atual = 0.0
        self.cam_pitch_alvo = 0.0
        self.cam_pitch_atual = 0.0

        for obj in self.objetos:
            obj.resetar()

    # -------------------------------------------------------------------------
    # TESTE DE VISIBILIDADE / ILUMINAÇÃO BINÁRIA (REQUISITO 3.9)
    # Inspirado em Traçado de Raio Simplificado (Ray Casting Cone-Sphere)
    # -------------------------------------------------------------------------
    def testar_iluminacao_binaria(self):
        """
        Calcula o traçado do raio de luz partindo de cada refletor LED no teto.
        Se a distância entre o eixo central do feixe de luz ativo e a obra for
        menor que o raio do cone de luz, a obra é marcada com ILUMINADO = 1 (True);
        caso contrário, ILUMINADO = 0 (False - permanece na penumbra ambiente).
        """
        # Obra ativa recebe o foco do holofote principal
        for i, spot in enumerate(self.spots_led):
            # A iluminação do spot i se ativa prioritariamente na etapa da sua sala
            eh_spot_ativo = (i == self.obra_foco_idx)
            
            # Ponto de origem do raio no projetor e alvo no chão/objeto
            origem_raio = spot["pos"]
            alvo_spot   = spot["alvo"]

            # Distância euclidiana entre a obra correspondente e o eixo do raio
            obra = None
            if i == 0: obra = self.moldura_toteninsel
            elif i == 1: obra = self.busto_nefertiti
            elif i == 2: obra = self.vitrine_papiro

            dist = math.sqrt(
                (obra.pos[0] - alvo_spot[0])**2 +
                (obra.pos[1] - alvo_spot[1])**2 +
                (obra.pos[2] - alvo_spot[2])**2
            )

            # Teste Binário de Interseção Cone-Objeto
            obra.iluminado = (eh_spot_ativo and dist <= spot["raio_cone"])

    # -------------------------------------------------------------------------
    # SISTEMA DE COLISÃO DO VISITANTE (MODO NAVEGAÇÃO LIVRE)
    # -------------------------------------------------------------------------
    def aplicar_colisoes_navegacao(self, nova_pos):
        """
        Garante que o visitante não consiga atravessar as paredes externas,
        paredes divisórias (respeitando as passagens dos portais) e pedestais/vitrines.
        """
        x, y, z = nova_pos
        raio_visitante = 0.45

        # 1. Limites das Paredes Externas
        x = max(-12.4 + raio_visitante, min(12.4 - raio_visitante, x))
        z = max(-2.9  + raio_visitante, min(12.9 - raio_visitante, z))
        y = max(-0.2, min(3.2, y)) # Altura dos olhos do visitante

        # 2. Divisória Oeste (x = -4.5): Permite passagem apenas no vão z in [2.6, 6.9]
        if abs(x - (-4.5)) < raio_visitante:
            if not (2.6 <= z <= 6.9):
                # Se não está no vão da porta, colide com a parede
                if self.cam_pos_atual[0] < -4.5:
                    x = -4.5 - raio_visitante
                else:
                    x = -4.5 + raio_visitante

        # 3. Divisória Leste (x = 4.5): Permite passagem apenas no vão z in [2.6, 6.9]
        if abs(x - 4.5) < raio_visitante:
            if not (2.6 <= z <= 6.9):
                if self.cam_pos_atual[0] > 4.5:
                    x = 4.5 + raio_visitante
                else:
                    x = 4.5 - raio_visitante

        # 4. Caixas Delimitadoras (AABB) de Pedestais e Vitrines
        # Caixa da Escultura Nefertiti (Sala 2: x = -8.0, z = 8.5)
        if abs(x - (-8.0)) < 1.3 and abs(z - 8.5) < 1.3:
            # Empurra para fora da caixa do pedestal
            dx = x - (-8.0)
            dz = z - 8.5
            if abs(dx) > abs(dz):
                x = -8.0 + (1.3 if dx > 0 else -1.3)
            else:
                z = 8.5 + (1.3 if dz > 0 else -1.3)

        # Caixa da Vitrine de Manuscritos (Sala 3: x = 8.0, z = 8.5)
        if abs(x - 8.0) < 1.8 and abs(z - 8.5) < 1.4:
            dx = x - 8.0
            dz = z - 8.5
            if abs(dx) > abs(dz):
                x = 8.0 + (1.8 if dx > 0 else -1.8)
            else:
                z = 8.5 + (1.4 if dz > 0 else -1.4)

        return [x, y, z]

    # -------------------------------------------------------------------------
    # ATUALIZAÇÃO DA LÓGICA, ANIMAÇÕES E CÂMERA (Δt)
    # -------------------------------------------------------------------------
    def atualizar(self, dt):
        # 1. Atualizar Máquina de Estados e Temporizador da Visita Guiada (Requisito 3.6)
        if self.estado_atual == self.ESTADO_EXECUTANDO:
            self.tempo_animacao += dt

            # Avanço temporal sequencial entre as 3 salas temáticas
            etapa_calculada = int(self.tempo_animacao / self.duracao_etapa)
            if etapa_calculada < len(self.info_obras):
                self.obra_foco_idx = etapa_calculada
            else:
                self.estado_atual = self.ESTADO_CONCLUIDO

        # 2. Atualizar Câmera conforme o Modo de Apresentação
        if self.modo_operacao == self.MODO_APRESENTACAO:
            if self.submodo_cam == self.MODO_CAM_FOCO or self.estado_atual == self.ESTADO_EXECUTANDO:
                # Foco dinâmico na obra ativa da visita
                foco_info = self.info_obras[self.obra_foco_idx]
                self.cam_pos_alvo = list(foco_info["pos_foco_cam"])
                self.cam_yaw_alvo = foco_info["yaw_foco"]
                self.cam_pitch_alvo = foco_info["pitch_foco"]
            else:
                # Visão geral panorâmica
                self.cam_pos_alvo = list(self.cam_pos_geral)
                self.cam_yaw_alvo = 0.0
                self.cam_pitch_alvo = 0.0

            # Interpolação suave da câmera (LERP amortecido)
            velocidade_lerp = 3.5 * dt
            for i in range(3):
                self.cam_pos_atual[i] += (self.cam_pos_alvo[i] - self.cam_pos_atual[i]) * velocidade_lerp
            self.cam_yaw_atual += (self.cam_yaw_alvo - self.cam_yaw_atual) * velocidade_lerp
            self.cam_pitch_atual += (self.cam_pitch_alvo - self.cam_pitch_atual) * velocidade_lerp

        elif self.modo_operacao == self.MODO_NAVEGACAO_LIVRE:
            # Na navegação livre, as teclas contínuas W/A/S/D movimentam o visitante
            keys = pygame.key.get_pressed()
            velocidade_andar = 4.2 * dt # Metros por segundo

            frente_x = math.sin(self.cam_yaw_atual)
            frente_z = math.cos(self.cam_yaw_atual)
            lado_x   = math.cos(self.cam_yaw_atual)
            lado_z   = -math.sin(self.cam_yaw_atual)

            dx, dz = 0.0, 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dx += frente_x * velocidade_andar
                dz += frente_z * velocidade_andar
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dx -= frente_x * velocidade_andar
                dz -= frente_z * velocidade_andar
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= lado_x * velocidade_andar
                dz -= lado_z * velocidade_andar
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += lado_x * velocidade_andar
                dz += lado_z * velocidade_andar

            nova_pos = [self.cam_pos_atual[0] + dx, self.cam_pos_atual[1], self.cam_pos_atual[2] + dz]
            self.cam_pos_atual = self.aplicar_colisoes_navegacao(nova_pos)

            # Determina qual obra está mais próxima no modo livre para atualizar informações
            menor_dist = 9999.0
            mais_proxima = self.obra_foco_idx
            for i, spot in enumerate(self.spots_led):
                alvo = spot["alvo"]
                d = math.sqrt((self.cam_pos_atual[0] - alvo[0])**2 + (self.cam_pos_atual[2] - alvo[2])**2)
                if d < menor_dist:
                    menor_dist = d
                    mais_proxima = i
            self.obra_foco_idx = mais_proxima

        # 3. Animações Espaciais dos Modelos (Requisito 3.4 & 3.6):
        # A) Rotação suave da Escultura (Busto de Nefertiti) em torno do eixo Y
        if self.estado_atual == self.ESTADO_EXECUTANDO or self.modo_operacao == self.MODO_NAVEGACAO_LIVRE:
            self.busto_nefertiti.rot[1] += 0.85 * dt

        # B) Leve oscilação de escala / pulsação do cone de luz (Requisito 3.4)
        if self.estado_atual == self.ESTADO_EXECUTANDO:
            fator_pulso = 1.0 + math.sin(self.tempo_animacao * 3.5) * 0.04
            self.spots_led[self.obra_foco_idx]["raio_cone"] = 2.2 * fator_pulso

        # 4. Executa o Teste de Visibilidade / Iluminação Binária
        self.testar_iluminacao_binaria()

    # -------------------------------------------------------------------------
    # RENDERIZAÇÃO DA CENA 3D (PAREDES, PISO, OBJETOS E SPOTLIGHTS)
    # -------------------------------------------------------------------------
    def desenhar_piso_museu(self):
        """Desenha a malha do piso com ladrilhos de mármore escuro em perspectiva."""
        y_piso = -1.2
        # Linhas em Z
        for x in range(-13, 14, 2):
            p1 = projetar_para_camera((x, y_piso, -3.5), self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)
            p2 = projetar_para_camera((x, y_piso, 13.5), self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)
            if p1 and p2:
                pygame.draw.line(self.tela, COR_PISO_GRADE, (p1[0], p1[1]), (p2[0], p2[1]), 1)

        # Linhas em X
        for z in range(-3, 14, 2):
            p1 = projetar_para_camera((-13.0, y_piso, z), self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)
            p2 = projetar_para_camera(( 13.0, y_piso, z), self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)
            if p1 and p2:
                pygame.draw.line(self.tela, COR_PISO_GRADE, (p1[0], p1[1]), (p2[0], p2[1]), 1)

    def desenhar_arquitetura_paredes(self):
        """Renderiza os painéis murais e portais separadores das galerias."""
        for parede in self.paredes_faces:
            pts_proj = [projetar_para_camera(v, self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual) for v in parede]
            if all(pt is not None for pt in pts_proj):
                poligono = [(pt[0], pt[1]) for pt in pts_proj]
                # Preenchimento e aresta arquitetônica
                pygame.draw.polygon(self.tela, COR_PAREDE, poligono)
                pygame.draw.polygon(self.tela, COR_PAREDE_BORDA, poligono, 1)

    def desenhar_objeto_3d(self, obj):
        """
        Aplica transformações geométricas locais (Escala, Rotação, Translação),
        calcula sombreamento difuso por iluminação direcional e desenha as faces.
        """
        # 1. Transformar vértices locais para o mundo
        verts_mundo = [transformar_vertice(v, obj.pos, obj.rot, obj.escala) for v in obj.vertices]
        verts_proj  = [projetar_para_camera(v, self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual) for v in verts_mundo]

        # Fonte de luz associada (Spot LED mais próximo)
        idx_spot = 0
        if obj.pos[0] < -4.0: idx_spot = 1
        elif obj.pos[0] > 4.0: idx_spot = 2
        luz_pos = self.spots_led[idx_spot]["pos"]

        # Fator de brilho geral da iluminação binária
        fator_luz_binaria = 1.0 if obj.iluminado else 0.40

        # Lista de polígonos ordenados por profundidade Z (Algoritmo do Pintor)
        faces_para_desenhar = []

        for face in obj.faces:
            pts_proj_face = [verts_proj[idx] for idx in face]
            if all(pt is not None for pt in pts_proj_face):
                z_medio = sum(pt[2] for pt in pts_proj_face) / len(pts_proj_face)

                # Cálculo de Normal da Face para Sombreamento Difuso de Lambert
                p0 = verts_mundo[face[0]]
                p1 = verts_mundo[face[1]]
                p2 = verts_mundo[face[2]]
                v1 = vet_sub(p1, p0)
                v2 = vet_sub(p2, p0)
                normal = vet_normalizar(vet_produto_vetorial(v1, v2))

                # Vetor da Luz para o centro da face
                centro_face = (
                    (p0[0] + p1[0] + p2[0]) / 3.0,
                    (p0[1] + p1[1] + p2[1]) / 3.0,
                    (p0[2] + p1[2] + p2[2]) / 3.0
                )
                vet_luz = vet_normalizar(vet_sub(luz_pos, centro_face))

                # Produto escalar (cos theta)
                dot = max(0.0, vet_produto_escalar(normal, vet_luz))

                # Cor base com iluminação ambiente (35%) + difusa (65% * dot)
                brilho = (0.35 + 0.65 * dot) * fator_luz_binaria
                cor_face = (
                    int(min(255, obj.cor_base[0] * brilho)),
                    int(min(255, obj.cor_base[1] * brilho)),
                    int(min(255, obj.cor_base[2] * brilho))
                )

                cor_aresta = (
                    min(255, int(cor_face[0] * 1.25)),
                    min(255, int(cor_face[1] * 1.25)),
                    min(255, int(cor_face[2] * 1.25))
                )

                poly_2d = [(pt[0], pt[1]) for pt in pts_proj_face]
                faces_para_desenhar.append((z_medio, poly_2d, cor_face, cor_aresta, obj.eh_vidro))

        # Ordenar faces da mais distante para a mais próxima (Painter's algorithm)
        faces_para_desenhar.sort(key=lambda item: item[0], reverse=True)

        # Desenhar faces na tela
        for _, poly, cor_f, cor_a, eh_vidro in faces_para_desenhar:
            if eh_vidro:
                # Superfície semitransparente de vidro
                surf_vidro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                pygame.draw.polygon(surf_vidro, COR_VIDRO_FACE, poly)
                pygame.draw.polygon(surf_vidro, COR_VIDRO_BORDA, poly, 1)
                self.tela.blit(surf_vidro, (0, 0))
            else:
                pygame.draw.polygon(self.tela, cor_f, poly)
                pygame.draw.polygon(self.tela, cor_a, poly, 1)

    def desenhar_superficies_artisticas_rasterizadas(self):
        """
        Projeta e rasteriza as obras bidimensionais com perspectiva e profundidade:
        - A tela de A Ilha dos Mortos encaixada perfeitamente na moldura 3D da Sala 1.
        - O Papiro de Ani disposto com textura sobre o tampo inclinado da vitrine da Sala 3.
        (Atende ao uso de superfícies rasterizadas e sprites previstos na AP1).
        """
        # 1. Tela de A Ilha dos Mortos (Arnold Böcklin)
        # Quatro vértices correspondentes à tela interna da moldura
        v_tela = [
            (-2.4, -1.3, 12.82), ( 2.4, -1.3, 12.82),
            ( 2.4,  1.3, 12.82), (-2.4,  1.3, 12.82)
        ]
        pts_proj = [projetar_para_camera(v, self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual) for v in v_tela]
        if all(pt is not None for pt in pts_proj):
            min_x = min(pt[0] for pt in pts_proj)
            max_x = max(pt[0] for pt in pts_proj)
            min_y = min(pt[1] for pt in pts_proj)
            max_y = max(pt[1] for pt in pts_proj)
            w = max_x - min_x
            h = max_y - min_y

            if w > 20 and h > 15:
                # Escalar a imagem da obra proporcionalmente ao retângulo em perspectiva
                tela_redim = pygame.transform.smoothscale(self.img_toteninsel, (w, h))
                
                # Modulação de brilho pela iluminação binária
                if not self.moldura_toteninsel.iluminado:
                    sombra = pygame.Surface((w, h), pygame.SRCALPHA)
                    sombra.fill((0, 0, 0, 140))
                    tela_redim.blit(sombra, (0, 0))
                
                self.tela.blit(tela_redim, (min_x, min_y))
                # Borda sutil de encaixe na moldura
                pygame.draw.rect(self.tela, (140, 110, 30), (min_x, min_y, w, h), 2)

        # 2. Papiro de Ani (Livro dos Mortos) no interior da Vitrine
        v_papiro = [
            (8.0 - 1.35, -1.2 + 1.05, 8.5 - 0.75), (8.0 + 1.35, -1.2 + 1.05, 8.5 - 0.75),
            (8.0 + 1.35, -1.2 + 1.28, 8.5 + 0.65), (8.0 - 1.35, -1.2 + 1.28, 8.5 + 0.65)
        ]
        pts_pap = [projetar_para_camera(v, self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual) for v in v_papiro]
        if all(pt is not None for pt in pts_pap):
            min_x = min(pt[0] for pt in pts_pap)
            max_x = max(pt[0] for pt in pts_pap)
            min_y = min(pt[1] for pt in pts_pap)
            max_y = max(pt[1] for pt in pts_pap)
            w = max_x - min_x
            h = max_y - min_y

            if w > 20 and h > 15:
                pap_redim = pygame.transform.smoothscale(self.img_papiro, (w, h))
                if not self.vitrine_papiro.iluminado:
                    sombra = pygame.Surface((w, h), pygame.SRCALPHA)
                    sombra.fill((0, 0, 0, 150))
                    pap_redim.blit(sombra, (0, 0))
                self.tela.blit(pap_redim, (min_x, min_y))

    def desenhar_feixes_spotlights(self):
        """
        Desenha as luminárias de LED no teto e os cones/raios translúcidos
        de iluminação direcionados para as obras.
        """
        for i, spot in enumerate(self.spots_led):
            p_proj = projetar_para_camera(spot["pos"], self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)
            a_proj = projetar_para_camera(spot["alvo"], self.cam_pos_atual, self.cam_yaw_atual, self.cam_pitch_atual)

            if p_proj and a_proj:
                eh_ativo = (i == self.obra_foco_idx)
                cor_luz = spot["cor"] if eh_ativo else (90, 100, 120)

                # Ponto do projetor no teto (círculo emissor)
                pygame.draw.circle(self.tela, cor_luz, (p_proj[0], p_proj[1]), 7 if eh_ativo else 4)
                pygame.draw.circle(self.tela, (255, 255, 255), (p_proj[0], p_proj[1]), 3 if eh_ativo else 2)

                # Desenhar feixe de raio do refletor até o foco
                if eh_ativo:
                    # Linha do raio de luz principal
                    pygame.draw.line(self.tela, COR_LUZ_LED, (p_proj[0], p_proj[1]), (a_proj[0], a_proj[1]), 2)
                    
                    # Linhas periféricas representando o cone de iluminação
                    dx_cone = 45
                    pygame.draw.line(self.tela, (255, 250, 200), (p_proj[0], p_proj[1]), (a_proj[0] - dx_cone, a_proj[1]), 1)
                    pygame.draw.line(self.tela, (255, 250, 200), (p_proj[0], p_proj[1]), (a_proj[0] + dx_cone, a_proj[1]), 1)

    # -------------------------------------------------------------------------
    # INTERFACE SOBREPOSTA HUD, CARTÕES DE PROXIMIDADE E CRÉDITOS
    # -------------------------------------------------------------------------
    def desenhar_hud(self):
        """Interface sobreposta com status, cronômetro, barra de progresso e comandos."""
        # Painel Superior: Título do Museu e Identificação da Galeria
        painel_top = pygame.Surface((LARGURA - 40, 78), pygame.SRCALPHA)
        painel_top.fill(COR_HUD_BG)
        self.tela.blit(painel_top, (20, 12))

        txt_tit = self.fonte_titulo.render("MUSEU VIRTUAL 3D — HISTÓRIA DA ARTE E DA ANTIGUIDADE", True, COR_DESTAQUE_HUD)
        self.tela.blit(txt_tit, (36, 18))

        sala_nome = self.info_obras[self.obra_foco_idx]["sala"]
        txt_sub = f"{sala_nome}  |  Estado: [{self.estado_atual}]  |  Modo: [{self.modo_operacao}]"
        self.tela.blit(self.fonte_hud.render(txt_sub, True, COR_TEXTO_HUD), (36, 45))

        # Barra de Progresso da Visita Guiada (Requisito AP1 3.8)
        tempo_total = len(self.info_obras) * self.duracao_etapa
        progresso = min(1.0, self.tempo_animacao / tempo_total) if tempo_total > 0 else 0.0
        
        largura_barra = 320
        pygame.draw.rect(self.tela, (40, 50, 70), (LARGURA - 360, 48, largura_barra, 12), border_radius=4)
        pygame.draw.rect(self.tela, COR_DESTAQUE_HUD, (LARGURA - 360, 48, int(largura_barra * progresso), 12), border_radius=4)
        txt_prog = f"Progresso Tour: {int(progresso*100)}%"
        self.tela.blit(self.fonte_pequena.render(txt_prog, True, COR_TEXTO_HUD), (LARGURA - 360, 28))

        # Painel Inferior Esquerdo: Controles do Teclado e Mouse
        painel_cmd = pygame.Surface((510, 120), pygame.SRCALPHA)
        painel_cmd.fill(COR_HUD_BG)
        self.tela.blit(painel_cmd, (20, ALTURA - 135))

        self.tela.blit(self.fonte_subtitulo.render("Painel de Comandos e Controles:", True, COR_DESTAQUE_HUD), (32, ALTURA - 130))
        comandos = [
            "[M] Alternar Modo: Apresentação AP1 <-> Navegação Livre (WASD + Mouse)",
            "[ESPAÇO] Iniciar/Pausar/Retomar Visita  |  [R] Reiniciar  |  [C] Câmera",
            "[1, 2, 3] Focar Sala Específica (Pinturas, Esculturas, Manuscritos)",
            "[N] / [B] Próxima / Anterior  |  [K] Créditos da Equipe  |  [ESC] Sair"
        ]
        for idx, cmd in enumerate(comandos):
            self.tela.blit(self.fonte_pequena.render(cmd, True, COR_TEXTO_HUD), (32, ALTURA - 105 + idx * 19))

        # Painel Inferior Direito: Cartão Didático da Obra / Placa de Proximidade
        obra_atual = self.info_obras[self.obra_foco_idx]
        painel_obra = pygame.Surface((580, 175), pygame.SRCALPHA)
        painel_obra.fill(COR_HUD_BG)
        self.tela.blit(painel_obra, (LARGURA - 600, ALTURA - 190))

        # Título da Obra e Artista
        t_obra = self.fonte_subtitulo.render(obra_atual["titulo"], True, COR_DESTAQUE_HUD)
        a_obra = self.fonte_hud.render(f"Autor: {obra_atual['artista']}", True, (255, 235, 170))
        p_obra = self.fonte_pequena.render(f"Período / Data: {obra_atual['periodo']} ({obra_atual['data']})", True, COR_TEXTO_HUD)
        m_obra = self.fonte_pequena.render(f"Material: {obra_atual['material']}  |  {obra_atual['localizacao']}", True, (190, 210, 230))
        d_obra = self.fonte_pequena.render(obra_atual["desc"], True, COR_TEXTO_HUD)

        # Status do Traçado de Raio / Iluminação Binária
        status_luz = "1 - ILUMINADA POR LED" if (
            (self.obra_foco_idx == 0 and self.moldura_toteninsel.iluminado) or
            (self.obra_foco_idx == 1 and self.busto_nefertiti.iluminado) or
            (self.obra_foco_idx == 2 and self.vitrine_papiro.iluminado)
        ) else "0 - PENUMBRA AMBIENTE"
        st_ilum = f"Visibilidade Binária (Spotlight): [{status_luz}]"

        self.tela.blit(t_obra, (LARGURA - 585, ALTURA - 182))
        self.tela.blit(a_obra, (LARGURA - 585, ALTURA - 158))
        self.tela.blit(p_obra, (LARGURA - 585, ALTURA - 138))
        self.tela.blit(m_obra, (LARGURA - 585, ALTURA - 118))
        self.tela.blit(d_obra, (LARGURA - 585, ALTURA - 98))
        self.tela.blit(self.fonte_hud.render(st_ilum, True, COR_DESTAQUE_HUD), (LARGURA - 585, ALTURA - 68))

    def desenhar_tela_creditos(self):
        """Tela sobreposta de Créditos e Referências da Atividade AP1 (Requisito 3.10)."""
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 240))
        self.tela.blit(overlay, (0, 0))

        txt_tit = self.fonte_titulo.render("PROJETO AP1 — COMPUTAÇÃO GRÁFICA E RA/RV", True, COR_DESTAQUE_HUD)
        self.tela.blit(txt_tit, (LARGURA//2 - txt_tit.get_width()//2, 50))

        sub_tit = self.fonte_subtitulo.render("Mundo Virtual Animado: Museu de História da Arte e da Antiguidade", True, (210, 230, 255))
        self.tela.blit(sub_tit, (LARGURA//2 - sub_tit.get_width()//2, 85))

        # Divisão de Responsabilidades dos 4 Integrantes
        integrantes = [
            ("Integrante 1 (Coordenação e Integração)", "Estrutura do código, pipeline gráfico 3D->2D, compatibilidade e testes."),
            ("Integrante 2 (Modelagem e Cena 3D)", "Salas temáticas, malha OBJ de Nefertiti, moldura 3D, vitrine e instâncias de pedestais."),
            ("Integrante 3 (Animação e Estados)", "Máquina de 4 estados, sequenciamento temporal Delta t, rotações e transições."),
            ("Integrante 4 (Câmera, Luz e Interface)", "Modos de câmera (Apresentação e WASD/Mouse), iluminação binária e HUD.")
        ]

        self.tela.blit(self.fonte_subtitulo.render("Equipe de Alunos e Responsabilidades:", True, COR_DESTAQUE_HUD), (120, 130))
        for i, (nome, desc) in enumerate(integrantes):
            txt_n = self.fonte_hud.render(f"• {nome}:", True, (255, 230, 160))
            txt_d = self.fonte_pequena.render(f"   {desc}", True, COR_TEXTO_HUD)
            self.tela.blit(txt_n, (140, 160 + i * 42))
            self.tela.blit(txt_d, (140, 180 + i * 42))

        # Referências das Obras e Materiais Didáticos
        refs = [
            "Variação Temática: Variação 1 — Museu Virtual (Abertura de salas, iluminação binária, visita guiada e rotação).",
            "Obra 1 (Pintura): 'A Ilha dos Mortos' (Arnold Böcklin, 1880) — Domínio Público (Alte Nationalgalerie Berlin).",
            "Obra 2 (Escultura): 'Busto de Nefertiti' (c. 1345 a.C.) — Digitalização 3D Fraunhofer IGD / CultLab3D (CC BY-NC).",
            "Obra 3 (Manuscrito): 'Papiro de Ani - Livro dos Mortos' (c. 1250 a.C.) — British Museum / Wikimedia Commons.",
            "Tecnologias: Python 3 + Pygame (Projeção Perspectiva Pura e Sombreamento Lambertiano sem OpenGL).",
            "Referência Curricular: Aulas 01 a 10 de Computação Gráfica — Prof. Alex Torquato Souza Carneiro."
        ]

        self.tela.blit(self.fonte_subtitulo.render("Referências dos Materiais e Tecnologias:", True, COR_DESTAQUE_HUD), (120, 360))
        for i, ref in enumerate(refs):
            self.tela.blit(self.fonte_pequena.render(f"• {ref}", True, (200, 215, 235)), (140, 395 + i * 26))

        txt_fechar = self.fonte_hud.render("Pressione [K] para fechar esta tela e retornar ao museu.", True, COR_DESTAQUE_HUD)
        self.tela.blit(txt_fechar, (LARGURA//2 - txt_fechar.get_width()//2, ALTURA - 70))

    # -------------------------------------------------------------------------
    # LAÇO PRINCIPAL E GERENCIAMENTO DE EVENTOS
    # -------------------------------------------------------------------------
    def executar(self):
        rodando = True
        while rodando:
            dt = self.relogio.tick(FPS) / 1000.0 # Delta tempo em segundos

            # Processamento de Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        rodando = False

                    # [M] Alternar entre Modo Apresentação AP1 e Modo Navegação Livre
                    elif evento.key == pygame.K_m:
                        if self.modo_operacao == self.MODO_APRESENTACAO:
                            self.modo_operacao = self.MODO_NAVEGACAO_LIVRE
                        else:
                            self.modo_operacao = self.MODO_APRESENTACAO
                            self.submodo_cam = self.MODO_CAM_GERAL

                    # [ESPAÇO] Iniciar / Pausar / Retomar Visita Guiada (Comando Discreto AP1)
                    elif evento.key == pygame.K_SPACE:
                        if self.estado_atual in [self.ESTADO_PARADO, self.ESTADO_PAUSADO]:
                            self.estado_atual = self.ESTADO_EXECUTANDO
                        elif self.estado_atual == self.ESTADO_EXECUTANDO:
                            self.estado_atual = self.ESTADO_PAUSADO
                        elif self.estado_atual == self.ESTADO_CONCLUIDO:
                            self.reiniciar()
                            self.estado_atual = self.ESTADO_EXECUTANDO

                    # [R] Reiniciar Aplicação
                    elif evento.key == pygame.K_r:
                        self.reiniciar()

                    # [C] Alternar Modo de Câmera da Apresentação
                    elif evento.key == pygame.K_c:
                        if self.modo_operacao == self.MODO_APRESENTACAO:
                            if self.submodo_cam == self.MODO_CAM_GERAL:
                                self.submodo_cam = self.MODO_CAM_FOCO
                            else:
                                self.submodo_cam = self.MODO_CAM_GERAL

                    # [1, 2, 3] Seleção Direta das Salas
                    elif evento.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.obra_foco_idx = evento.key - pygame.K_1
                        if self.modo_operacao == self.MODO_APRESENTACAO:
                            self.submodo_cam = self.MODO_CAM_FOCO

                    # [N] Próxima Obra / [B] Obra Anterior
                    elif evento.key == pygame.K_n:
                        self.obra_foco_idx = (self.obra_foco_idx + 1) % len(self.info_obras)
                    elif evento.key == pygame.K_b:
                        self.obra_foco_idx = (self.obra_foco_idx - 1) % len(self.info_obras)

                    # [K] Alternar Tela de Créditos
                    elif evento.key == pygame.K_k:
                        self.exibir_creditos = not self.exibir_creditos

                # Controles de Mouse para Rotação da Visão (Pitch e Yaw)
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1: # Botão esquerdo do mouse
                        self.mouse_arrastando = True
                        self.mouse_ultimo_pos = evento.pos

                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1:
                        self.mouse_arrastando = False

                elif evento.type == pygame.MOUSEMOTION:
                    if self.mouse_arrastando or (self.modo_operacao == self.MODO_NAVEGACAO_LIVRE and pygame.mouse.get_pressed()[0]):
                        dx = evento.pos[0] - self.mouse_ultimo_pos[0]
                        dy = evento.pos[1] - self.mouse_ultimo_pos[1]
                        self.mouse_ultimo_pos = evento.pos

                        # Rotação da visão do observador
                        self.cam_yaw_atual += dx * self.sensibilidade_mouse
                        self.cam_pitch_atual -= dy * self.sensibilidade_mouse
                        # Limite para não inverter a visão vertical
                        self.cam_pitch_atual = max(-1.1, min(1.1, self.cam_pitch_atual))

            # Atualização da Lógica
            self.atualizar(dt)

            # -----------------------------------------------------------------
            # RENDERIZAÇÃO DA CENA EM PYGAME
            # -----------------------------------------------------------------
            self.tela.fill(COR_FUNDO)

            # 1. Piso com Grade e Ladrilhos de Museu
            self.desenhar_piso_museu()

            # 2. Paredes e Portais Arquitetônicos das Galerias
            self.desenhar_arquitetura_paredes()

            # 3. Desenhar Pedestais e Vitrines
            for ped in self.pedestais:
                self.desenhar_objeto_3d(ped)

            self.desenhar_objeto_3d(self.moldura_toteninsel)
            self.desenhar_objeto_3d(self.vitrine_papiro)

            # 4. Desenhar Superfícies Artísticas Rasterizadas (Pintura e Papiro)
            self.desenhar_superficies_artisticas_rasterizadas()

            # 5. Desenhar Busto Escultórico 3D
            self.desenhar_objeto_3d(self.busto_nefertiti)

            # 6. Desenhar Placas de Identificação em Bronze
            for placa in self.placas:
                self.desenhar_objeto_3d(placa)

            # 7. Desenhar Luminárias e Cones de Luz Spot
            self.desenhar_feixes_spotlights()

            # 8. Desenhar Interface Sobreposta (HUD)
            self.desenhar_hud()

            # 9. Desenhar Tela de Créditos (se acionada)
            if self.exibir_creditos:
                self.desenhar_tela_creditos()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# -----------------------------------------------------------------------------
# PONTO DE ENTRADA PRINCIPAL DA APLICAÇÃO
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = MuseuVirtual3D()
    app.executar()