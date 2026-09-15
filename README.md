# Museu Virtual de Computação Gráfica

Projeto acadêmico **Mundo Virtual Animado**, desenvolvido em Python 3 e Pygame. O programa simula uma visita a um museu com oito obras distribuídas em três alas: Clássica, Matemática e Tecnológica.

O projeto foi desenvolvido para computadores modestos de laboratório. A renderização usa primitivas 2D, projeção perspectiva matemática e poucos vértices, sem OpenGL, motor 3D ou outras bibliotecas externas.

## Objetivos do projeto

- Demonstrar programação orientada a objetos e separação modular.
- Aplicar projeção matemática 3D para 2D.
- Utilizar câmera com transição suave por interpolação.
- Criar objetos geométricos e animações dependentes de `dt`.
- Oferecer três formas de visita sem controle livre de personagem.
- Integrar audioguia opcional sem interromper o funcionamento quando arquivos não existirem.

## Requisitos

- Python 3.x
- Pygame 2.x
- Sistema operacional Windows, Linux ou macOS
- GPU dedicada não é necessária

A única dependência externa é `pygame`, declarada em [requirements.txt](requirements.txt).

## Instalação e execução

Abra um terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

No Windows, também é possível usar:

```powershell
py -m pip install -r requirements.txt
py main.py
```

O programa inicia diretamente no Menu Principal. Para fechar a janela, use `ESC` no menu ou o botão padrão de fechar da janela.

## Modos de visita

### 1. Roteiro Básico

Apresenta automaticamente as oito obras em ordem cronológica. A obra ativa muda a cada três segundos, a câmera acompanha a apresentação e os objetos continuam sendo animados.

### 2. Curadoria Interativa

Permite selecionar as obras individualmente e alternar entre Plano Geral e Foco Detalhado. A interação é feita somente por comandos discretos de teclado; não existe personagem, movimentação WASD ou navegação livre.

### 3. Tour Imersivo com Audioguia

Apresenta as obras automaticamente com câmera detalhada, iluminação e áudio correspondente. Cada obra permanece ativa durante a duração real do arquivo de áudio. Se o áudio não existir ou não puder ser lido, o intervalo padrão é de quatro segundos.

## Controles

### Menu Principal

| Tecla | Ação |
|---|---|
| `1` | Iniciar Roteiro Básico |
| `2` | Iniciar Curadoria Interativa |
| `3` | Iniciar Tour Imersivo |
| `C` | Abrir Créditos |
| `ESC` | Sair do programa |
| `M` | Permanecer ou retornar ao menu |

### Roteiro Básico

| Tecla | Ação |
|---|---|
| `ESPAÇO` | Pausar ou retomar |
| `R` | Reiniciar o roteiro |
| `M` ou `ESC` | Retornar ao menu |

### Curadoria Interativa

| Tecla | Ação |
|---|---|
| `←` | Obra anterior |
| `→` | Próxima obra |
| `1` | Plano Geral |
| `2` | Foco Detalhado |
| `L` | Ligar ou desligar raio de inspeção |
| `ESPAÇO` | Pausar ou retomar animações |
| `R` | Reiniciar a curadoria |
| `M` ou `ESC` | Retornar ao menu |

### Tour Imersivo

| Tecla | Ação |
|---|---|
| `ESPAÇO` | Pausar ou retomar animação e áudio |
| `R` | Reiniciar o tour |
| `M` ou `ESC` | Retornar ao menu |

## Acervo do museu

O acervo possui exatamente oito objetos principais:

### Ala Clássica

1. Mona Lisa — Leonardo da Vinci
2. Autorretrato — Rembrandt
3. Guernica — Pablo Picasso
4. Noite Estrelada — Vincent van Gogh

As quatro pinturas usam a classe reutilizável `PainelExposicao`. As imagens são carregadas uma vez e possuem fallback procedural quando estão ausentes.

### Ala Matemática

5. Icosaedro Wireframe — vértices 3D, arestas, rotação contínua, pedestal e projeção perspectiva.
6. Espiral Áurea de Fibonacci — espiral gerada matematicamente durante a renderização.

### Ala Tecnológica

7. Servidor Monolítico — corpo geométrico, matriz de LEDs pulsantes e animação baseada em funções trigonométricas.
8. Fita Perfurada de Turing — construída com retângulos e círculos do Pygame.

## Áudios do Tour

Os arquivos ficam em `assets/audio`. As durações medidas com Pygame são:

| Arquivo | Obra | Duração |
|---|---|---:|
| `01_mona_lisa.ogg` | Mona Lisa | 43,248 s |
| `02_rembrandt.ogg` | Autorretrato | 39,171 s |
| `03_guernica.ogg` | Guernica | 39,113 s |
| `04_noite_estrelada.ogg` | Noite Estrelada | 35,050 s |
| `05_icosaedro.ogg` | Icosaedro | 39,120 s |
| `06_espiral_aurea.ogg` | Espiral Áurea | 36,490 s |
| `07_servidor_monolitico.ogg` | Servidor Monolítico | 39,446 s |
| `08_tuning.ogg` | Fita de Turing | 57,882 s |

Duração total aproximada: **5 minutos e 29,52 segundos**.

O sistema usa `pygame.mixer.music` para reprodução. O carregamento da duração é feito separadamente e fica em cache. A ausência de qualquer arquivo não causa crash.

## Imagens opcionais

As imagens ficam em `assets/images` e, no estado atual do projeto, usam exatamente estes nomes:

```text
Mona_Lisa.jpg
Rembrandt.jpg
Guernica - Picasso.jpg
Noite_Estrelada.jpg
```

Caso alguma imagem seja removida, o programa continua executando e desenha uma representação procedural leve. Se o grupo substituir as imagens, deve manter esses nomes ou atualizar a lista em `src/core/engine.py`.

## Arquitetura

```text
main.py
src/
	core/
		engine.py          # loop principal, eventos e orquestração
		state_machine.py   # estados do menu, modos e créditos
	graphics/
		camera.py          # posição, zoom e interpolação da câmera
		renderer.py        # primitivas Pygame e projeção perspectiva
		raycaster.py       # interseção simples com bounding box
	entities/
		base_object.py     # contrato comum das entidades
		artwork.py         # PainelExposicao e fallback de imagens
		math_sculpture.py  # Icosaedro e EspiralAurea
		tech_monolith.py   # ServidorMonolitico e FitaTuring
	audio/
		sound_manager.py   # áudio opcional e duração das faixas
	ui/
		menu.py            # Menu Principal e Créditos
		hud.py             # modo, obra, status e progresso
assets/
	images/              # imagens opcionais das pinturas
	audio/               # narrações opcionais do tour
```

## Conceitos de Computação Gráfica

- **Projeção 3D para 2D:** o `Renderer` aplica fator de perspectiva baseado na profundidade `z`.
- **Translação:** cada entidade possui posição `x` e `y` própria.
- **Rotação:** o icosaedro atualiza seu ângulo continuamente.
- **Escala:** a câmera possui zoom interpolado e os LEDs variam de intensidade e raio.
- **Câmera:** Plano Geral e Foco Detalhado usam transição suave dependente de `dt`.
- **Raycaster:** verifica interseção barata entre um raio 2D e o bounding box da obra ativa.
- **Delta time:** o loop usa `clock.tick(60) / 1000.0`, mantendo as animações independentes da taxa de quadros.

## HUD e estados

Durante os modos de visita, o HUD exibe:

- nome do museu;
- modo atual;
- obra e autor;
- estado da animação;
- barra de progresso;
- atalhos disponíveis.

Os estados usados são `PARADO`, `EXECUTANDO`, `PAUSADO` e `CONCLUIDO`.

## Checklist de testes

Antes da apresentação, confirme:

- [ ] O projeto instala com `python -m pip install -r requirements.txt`.
- [ ] `python main.py` abre o Menu Principal.
- [ ] As opções `1`, `2`, `3` e `C` funcionam.
- [ ] O Roteiro Básico percorre as oito obras.
- [ ] A Curadoria responde a `←`, `→`, `1`, `2`, `L`, `ESPAÇO` e `R`.
- [ ] O Tour troca a obra quando o áudio correspondente termina.
- [ ] `ESPAÇO` pausa e retoma áudio e animação.
- [ ] `M` e `ESC` retornam ao menu nos modos de visita.
- [ ] As imagens e os áudios podem ser removidos sem causar crash.
- [ ] A janela fecha corretamente.

## Divisão sugerida para o grupo

Os integrantes podem dividir a preparação da entrega desta forma:

1. **Apresentação e roteiro:** explicar o objetivo, os três modos e os controles.
2. **Computação gráfica:** demonstrar projeção, câmera, rotação do icosaedro, escala e raycaster.
3. **POO e arquitetura:** explicar `BaseObject`, entidades, máquina de estados e separação de responsabilidades.
4. **Áudio e acervo:** revisar as narrações, imagens, nomes dos arquivos e sincronização por duração.
5. **Testes e documentação:** executar o checklist, conferir computadores do laboratório e preencher os créditos.

Os nomes dos integrantes e os papéis podem ser preenchidos em `src/ui/menu.py`, na tela de Créditos.

## Desempenho e limitações

- A resolução padrão é `1100x700` com limite de 60 FPS.
- As listas de vértices são pequenas e os recursos são carregados uma única vez sempre que possível.
- As imagens redimensionadas são armazenadas em cache.
- Não há OpenGL, shaders, física, banco de dados, rede ou controle livre de personagem.
- O áudio depende do dispositivo de saída do computador. Quando o mixer não inicializa, o tour continua apenas com a animação visual.
- O raycaster é uma aproximação 2D contra bounding boxes; não é ray tracing real.

## Licença e créditos

Projeto acadêmico para a disciplina de Computação Gráfica. Os nomes dos integrantes, referências das imagens e autoria das narrações devem ser preenchidos pelo grupo antes da entrega final.
