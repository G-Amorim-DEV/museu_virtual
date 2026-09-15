# Museu Virtual de Computação Gráfica

Projeto acadêmico em **Python 3 + Pygame** que unifica a cena arquitetônica da AP1 com a implementação modular original. Há uma única experiência principal, iniciada por `python main.py`: um museu 3D leve, com saguão, corredores, quatro salas temáticas, 11 obras, visita guiada, curadoria, audioguia e navegação livre.

## Instalação e execução

```bash
python -m pip install -r requirements.txt
python main.py
```

O programa funciona sem GPU dedicada, OpenGL, motor 3D ou assets opcionais. Se uma imagem, áudio ou o OBJ de Nefertiti não estiver disponível, a cena mantém um fallback procedural e continua em execução.

## Arquitetura unificada

`main.py` é o único ponto de entrada e cria `src.core.engine.Engine`. `museu_virtual_ap1.py` permanece como adaptador compatível para a entrega AP1 e instancia o mesmo motor — não existe uma segunda experiência concorrente.

```text
main.py
museu_virtual_ap1.py       adaptador compatível da AP1
src/
  core/engine.py           controlador, cena, modos, câmera e colisões
  core/state_machine.py    estados globais
  museum/collisions.py     planta física, paredes, portas e deslizamento
  audio/sound_manager.py   áudio opcional e cache de durações
  graphics/raycaster.py    inspeção por raio contra bounding box
  graphics/                câmera/renderizador legados reutilizáveis
  entities/                entidades modulares originais reutilizáveis
assets/images/             pinturas opcionais
assets/audio/              oito narrações opcionais
```

### Integração das implementações

| Origem | Funcionalidades preservadas ou integradas |
|---|---|
| Implementação modular (`src/`) | oito obras originais, imagens com fallback, cache e duração real do audioguia, roteiro, curadoria, tour, pausa, reinício, seleção anterior/próxima, HUD, créditos, raycaster e animações por `dt`. |
| AP1 | projeção em perspectiva, cena 3D arquitetônica, salas, piso, teto, paredes, portais, pedestais, vitrine, molduras, spots, placas, navegação WASD/mouse, colisões e proximidade. |
| Redundâncias | os antigos loops independentes e a antiga apresentação 2.5D foram substituídos pelo único controlador `Engine`; os recursos continuam disponíveis na mesma cena. |

## Planta e salas

O visitante inicia no **Saguão Central**, com indicação dos setores e acesso por arcos. A planta possui limites externos, divisórias, corredor transversal e obstáculos físicos para pedestais/vitrines.

- **Galeria Clássica:** paredes de tom tradicional, molduras e spots para quatro pinturas.
- **Galeria de Antiguidade:** iluminação quente, pedestal para Nefertiti, vitrine e Papiro de Ani, além de *A Ilha dos Mortos*.
- **Galeria Matemática:** pedestais científicos para o icosaedro e a espiral.
- **Galeria Tecnologia:** área fria com servidor e fita perfurada.

## Acervo

1. Mona Lisa — Leonardo da Vinci
2. Autorretrato — Rembrandt
3. Guernica — Pablo Picasso
4. Noite Estrelada — Vincent van Gogh
5. Icosaedro Wireframe
6. Espiral Áurea de Fibonacci
7. Servidor Monolítico
8. Fita Perfurada de Turing
9. A Ilha dos Mortos — Arnold Böcklin
10. Busto de Nefertiti
11. Papiro de Ani / Livro dos Mortos

As primeiras oito obras mantêm as faixas de áudio em `assets/audio`. O tour usa a duração medida pelo Pygame quando o arquivo existe e um fallback de quatro segundos quando não existe; as três obras AP1 entram no roteiro com fallback temporal.

## Modos e controles

| Tecla | Ação |
|---|---|
| `1` | Menu: Roteiro Básico; visita: atalho à Galeria Clássica |
| `2` | Menu: Curadoria Interativa; visita: atalho à Antiguidade |
| `3` | Menu: Tour Imersivo; visita: atalho à Matemática |
| `4` | Menu: Navegação Livre; visita: atalho à Tecnologia |
| `M` | Alterna apresentação e navegação livre; no menu inicia exploração |
| `W` `A` `S` `D` | Mover na navegação livre |
| Mouse | Olhar (capturado na navegação livre) |
| `N` / `B` ou setas | Próxima / anterior obra |
| `C` | Alternar plano geral / foco detalhado com transição suave |
| `Espaço` | Pausar ou retomar roteiro/tour/animações/áudio |
| `R` | Reiniciar o modo atual |
| `L` | Alternar raio de inspeção |
| `K` | Créditos |
| `ESC` | Voltar ao menu; no menu, sair |

A máquina de estados contém `MENU`, `EXPLORATION`, `BASIC_SCRIPT`, `CURATION`, `IMMERSIVE_TOUR`, `PAUSED`, `CREDITS` e `COMPLETED`. Pausa guarda o estado anterior para evitar conflitos entre modos.

## Conceitos de Computação Gráfica

- **Projeção perspectiva:** cada ponto do mundo é transladado para a câmera, rotacionado por yaw/pitch e projetado com `x/z` e `y/z`.
- **Câmera:** transições exponenciais dependentes de `dt`; navegação livre com yaw/pitch.
- **Colisões:** uma planta física com caixas 2D para paredes, divisórias, pedestais e vitrines impede passagem indevida e permite deslizar ao longo de obstáculos; os vãos dos portais permanecem atravessáveis.
- **Iluminação procedural:** luz ambiente, spots de teto e destaque dourado para obra ativa/próxima.
- **Animação:** rotação do icosaedro, espiral animada, LEDs pulsantes e iluminação usam `dt`.
- **Raycaster:** o raio horizontal da câmera testa caixas das obras, destaca a primeira peça atingida e identifica a inspeção no HUD.
- **Performance:** imagens são carregadas antecipadamente, escalas de pintura são cacheadas por dimensão quantizada, áudio tem cache de duração e a geometria usa caixas/polígonos simples.

## Validação automatizada

Além da verificação visual, execute:

```bash
python -m unittest discover -s tests -v
python -m compileall .
```

Os testes headless verificam o acervo, os fallbacks, a malha de Nefertiti, paredes e portais, deslizamento de colisão, raio de inspeção, pausa, créditos e transições de modo.

## Assets e referências

As imagens opcionais das quatro pinturas ficam em `assets/images`; os áudios das oito obras originais ficam em `assets/audio`. A imagem de *A Ilha dos Mortos*, o papiro e o OBJ de Nefertiti são opcionais e recebem representação procedural quando ausentes.

Referências preservadas da AP1: *A Ilha dos Mortos* (Arnold Böcklin, 1880; Alte Nationalgalerie Berlin, domínio público); Busto de Nefertiti (digitalização Fraunhofer IGD / CultLab3D, CC BY-NC); Papiro de Ani (British Museum / Wikimedia Commons). A tela de créditos mantém o espaço para os nomes e papéis reais do grupo acadêmico.
