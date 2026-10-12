# Knight vs Ogre — resumo do projeto e ponto de partida

> Este arquivo é lido automaticamente pelo Claude Code quando você abre esta pasta. Ele resume tudo que foi
> feito numa conversa anterior (no claude.ai) para que a sessão aqui no seu computador continue de onde parou.
> **Responda em português (pt-BR).** O usuário usa **Windows** e já tem **Python** instalado.

## 1. Em uma frase

Um jogo 2D de combate (cavaleiro vs. ogro) em **Python + pygame**, com toda a arte em pixel art **gerada por código**
(Python + Pillow): personagens animados, efeitos especiais e cenário. O jogo roda e as regras estão testadas, mas
**ainda não foi executado com o pygame de verdade** (veja a seção 7).

## 2. Como rodar

```
pip install -r requirements.txt        # pygame
python main.py                         # ou dois cliques em run_game.bat
build_exe.bat                          # gera dist\KnightVsOgre.exe (PyInstaller, não testado)
python tests/test_logic.py             # testes das regras (não precisam de janela)
python tests/simulate.py               # roda main.py/view.py reais num "pygame de mentira" e grava GIFs em out/
```

Controles: setas ou A/D andam, **Espaço** pula, **botão esquerdo do mouse** ataca (segurar repete), **M** liga/desliga o som, F11 tela cheia, Esc sai.

> **pygame-ce:** o `pygame` clássico não instalou no Python do usuário; o jogo roda com `pip install pygame-ce` (mesmo `import pygame`).

## 3. Estrutura da pasta

```
main.py                 laço principal, teclado, janela (resolução interna 480x270, escala inteira 3x)
game/config.py          TODOS os números ajustáveis (dano, velocidades, tempos da IA, respawn, câmera...)
game/logic.py           regras do jogo, SEM pygame (World, Fighter, IA do ogro, dano, respawn, cenário infinito)
game/view.py            desenho: parallax, chão, cenário, personagens, efeitos, HUD
game/audio.py           toca os SFX a partir de `world.events` (falha em silêncio sem dispositivo de áudio)
assets/                 spritesheets (png + json) e cenário (png) usados pelo jogo
assets/sfx/             efeitos sonoros .wav (gerados por código, ver skill game-audio-synthesis)
assets/music/           trilha .wav em loop (`music_gen.py` da mesma skill regenera)
tests/                  test_logic.py, simulate.py, fake_pygame.py (stand-in em Pillow para rodar sem janela)
art_tools/              geradores da arte (ver seção 5); build_assets.py regenera tudo em assets/
.claude/skills/         4 skills do projeto (carregadas automaticamente pelo Claude Code, ver seção 6)
install_skills.py       OPCIONAL: instala as skills também como skills pessoais (~/.claude/skills)
requirements.txt        pygame            requirements-art.txt   Pillow (só para as ferramentas de arte)
```

## 4. O jogo

**Pedido original do usuário (resumo):** abre direto no combate; cavaleiro à esquerda (controlado), ogro à direita
(IA); vida de 0 a 100 para os dois, cada golpe tira 10; ao levar dano toca `hurt` e o personagem não anda nem ataca
durante a animação; HUD estilo jogo de luta (vida do herói à esquerda, do ogro à direita); ogro anda até o herói e
ataca depois de uma pequena pausa; ao morrer o ogro o corpo fica no chão e entra outro pela direita; ao morrer o herói
nasce outro na esquerda; contadores de derrotas de cada lado; cenário infinito com a câmera seguindo o herói (herói no
centro).

**Como foi implementado**
- `World.update(dt, inputs)` é o coração. Estados do `Fighter`: `idle, walk, attack, hurt, dead`. Só `idle/walk` podem
  agir (`can_act`). Animações vêm de `ANIM[kind][state]` (cavaleiro ataca com `attack_sword`).
- **Dano por hitbox**: o golpe só conta nos frames `ACTIVE_FRAMES = (3, 4)` da animação de ataque e **uma vez por golpe**
  (`hit_done`). Alcance em `KNIGHT_REACH` / `OGRE_REACH` (intervalo à frente do quadril). Os golpes dos dois lados são
  aplicados juntos (troca de golpes é possível).
- **Efeitos**: rastro (`sword_slash`/`axe_slash`) nasce quando o atacante chega ao frame 3; `blood_splash` no dano;
  `spirit` na morte, com atraso `SPIRIT_DELAY`. Todos usam a mesma âncora/espelhamento do personagem.
- **IA do ogro** (`_ogre_ai`): anda até `OGRE_ATTACK_DIST`; já em alcance espera `OGRE_WAIT_BEFORE_ATTACK` (0,55–0,95 s,
  sorteado — é a janela do jogador) e ataca; depois descansa `OGRE_COOLDOWN`. Se o herói recua pouco
  (`OGRE_PATIENCE_DIST`) ele mantém o plano em vez de recomeçar a espera. Ao sair de um `hurt` ele revida mais rápido
  (`OGRE_RETALIATE_WAIT`).
- **Decisões minhas (não pedidas) que merecem revisão do usuário**: depois do `hurt` o personagem fica invulnerável por
  `HURT_INVULN_EXTRA = 0.6 s` (sem isso, segurar Espaço travava o ogro em stun-lock eterno — descoberto num teste);
  knockback de 14 px; o herói não atravessa o ogro vivo (`MIN_SEPARATION`); herói recém-nascido é invulnerável 1 s;
  tremor de tela curto ao acertar; dica de controles nos primeiros 8 s.
- **Respawn**: morte → `RESPAWN_DELAY` (1,6 s) → o corpo vira cadáver (`world.corpses`, máx. 40) e nasce outro. Novo
  ogro entra pela borda direita da tela; novo herói na esquerda; a câmera mantém a posição e desliza até recentralizar
  o herói (`cam_off`, decaimento exponencial `CAMERA_EASE`).
- **Cenário infinito**: o mundo é dividido em "fatias" de `SLOT_W = 176` px; `slot_props(slot)` decide de forma
  determinística (seed) se a fatia tem casa, árvore, poço ou nada; só as fatias visíveis são desenhadas. Chão em tiles
  de 64 px alinhados ao mundo, mais nuvens e duas colinas com parallax (geradas no `view.py`, sem arquivos).
- **Janela**: tela interna 480x270 ampliada por **escala inteira** (pixels quadrados e nítidos); redimensionável; F11
  alterna tela cheia; no Windows chama `SetProcessDPIAware`.

## 5. Arte (convenções que o código do jogo assume — não quebre!)

Todos os frames são **64x64, 6 frames por animação, personagem virado para a DIREITA** (o jogo espelha). Um sheet tem
uma linha por animação; **a ordem das linhas e os nomes fazem parte do contrato com o jogo/atlas: só acrescente linhas
no final**. O jogo lê o `fps` de cada animação do `.json`.

| sheet | linhas (na ordem) |
|---|---|
| `knight_spritesheet` | idle(6fps), walk(10), run(12), attack_sword(12, golpe LATERAL), attack_axe(10), attack_bow(10), attack_crossbow(10), hurt(10), death(8), jump_up(12), jump_fall(10), attack_sword_2(12, combo: corte ascendente), attack_sword_3(12, combo: golpe final de cima para baixo) |
| `ogre_spritesheet` | idle(6), walk(10), attack(10, machado), hurt(10), death(8) |
| `knight_axe_spritesheet` | **mesmas linhas e nomes do `knight_spritesheet`**, mas o herói empunha o machado (arquivo gerado por `knight_gen.py write_sheet(out, 'axe')`); o jogo usa a linha `attack_axe` |
| `vfx_spritesheet` | sword_slash(12), axe_slash(10), blood_splash(12), spirit(6), heal(10), coin_glint(12), sword_slash_2(12), sword_slash_3(12) |

- **Âncora**: coluna do quadril = 30 no frame normal, **33 quando espelhado** (63−30); linha do chão = 58 dentro do frame
  (no jogo `GROUND_Y = 217`). Posicione sempre por essa coluna, senão o sprite "pula" ao virar.
- Animações de ataque têm o golpe nos **frames 3–4**; o efeito `i` toca junto com o frame `3+i` do ataque.
- No cavaleiro o frame 4 do arco e da besta é o disparo (a flecha/virote só é desenhada nesse frame; o projétil de verdade
  teria de ser criado pelo jogo). **Arco, besta e machado do cavaleiro existem nos sheets mas o jogo ainda não usa** (a animação `run` já é usada ao andar).
- Cenário: `tree` 112x128, `medieval_house` 160x160, `well` 48x64, `street_tile` 64x40 (repetível na horizontal),
  `box` 24x24 (caixote; contorno nas 4 bordas; caixas empilhadas compartilham a linha de contorno, 23 px por nível).
  O último pixel sólido de cada objeto é o chão (a linha de baixo é o contorno).
- Estilo: contorno 1 px `(18,18,30)`, só pixels opacos (transparência de efeitos é simulada com dithering), luz vinda do
  topo-esquerda, paleta compartilhada entre personagens e cenário.

**Ferramentas de arte** (`art_tools/`, precisam de `pip install -r requirements-art.txt`):
- `python build_assets.py` regenera todos os sheets/atlas/cenário em `assets/`; `--check` só confere se `assets/` ainda
  bate com os geradores (pixel a pixel); `--gifs` também grava GIFs de demonstração em `out/`.
- `sprite_rig.py` = esqueleto compartilhado (IK de dois ossos, camadas com contorno, armas); `knight_gen.py` e
  `ogre_gen.py` = os personagens (poses como listas por frame); `vfx_gen.py` = efeitos; `scenery_gen.py` = cenário;
  `demo_gif.py` = cenas compostas (batalha, morte do herói, grade com todas as animações).
- Depois de mexer em poses rode o verificador de cortes:
  `python ../.claude/skills/pixel-sprite-animation/scripts/check_edges.py ../assets/knight_spritesheet.png`.
- **Se mudar os frames de ataque, regenere os efeitos de golpe**: foram ajustados a essas poses exatas.

### 4.1 Pulo, caixas e alcance (regras adicionadas depois)

- **Pulo**: Espaço (um pulo por toque). `Fighter.y` = altura dos pés, `vy`, `grounded`. Altura `JUMP_HEIGHT` (44 px ≈ altura do
  cavaleiro), tempo de subida `JUMP_RISE_TIME`; gravidade derivada. Move-se no ar. Animação derivada do estado físico:
  `jump_up` (vy>0) e `jump_fall` (vy<=0, inclusive ao cair de uma caixa sem ter pulado). O ogro nunca sai do chão.
- **Ataque**: botão esquerdo do mouse. O herói **anda enquanto ataca** (sem virar de lado). Ataque de espada em
  `KNIGHT_ATTACK_ANIM_SPEED = 2.0`; o herói usa a animação `run` ao andar (`HERO_SPEED = 120`).
- **Sem colisão entre personagens**: atravessam-se. `KNIGHT_REACH/OGRE_REACH` começam em −12 para que um alvo sobreposto
  ainda seja acertado; o ogro não "pisca" de lado quando o herói está em cima dele (zona morta de 2 px).
- **Caixas** (`slot_boxes(slot)` em `logic.py`, desenhadas em `view.py`): plataformas só de pouso (one-way). Andar no chão
  atravessa a caixa; pular e cair em cima pousa; pode pular de dentro/na frente. Cada nível = `BOX_H` (23 px, metade do
  cavaleiro). Slot 0 tem 1 caixa e o slot 2 uma escada 1-2-3 perto do início; o resto é sorteado de forma determinística.
- **Alcance vertical**: um golpe só acerta se a diferença de altura dos pés ≤ `VERTICAL_REACH` (30 px; vale para os dois
  lados). Herói em 1 caixa (23) é atingido do chão; em 2 ou 3 caixas o ogro fica embaixo sem conseguir acertar (e o
  herói também não acerta de lá). O ogro não balança o machado no vazio.
- **Ogro**: `OGRE_MAX_HP = 30` (3 golpes). Mantém a invulnerabilidade pós-dano (`OGRE_HURT_INVULN = True`, hurt +
  `OGRE_HURT_INVULN_EXTRA = 0.4` → 1,0 s no total; o herói usa `HURT_INVULN_EXTRA = 0.6`); com `False` ele morria rápido demais (o usuário pediu para voltar).

### 4.2 Pickups e ouro

- Ao morrer, o ogro sorteia (em `World.loot_rng`, fluxo separado da IA) uma poção (`POTION_DROP_CHANCE` 0,30; cura
  `POTION_HEAL` 30) e uma bolsa de ouro (`COIN_BAG_DROP_CHANCE` 0,50; `COIN_BAG_COINS` 5–10). Os sorteios são independentes.
- Só o herói coleta (`World._pickups`): alcance horizontal `PICKUP_RADIUS`, vertical `PICKUP_REACH_Y`. Poção com vida
  cheia **não** é consumida (fica no chão). O ouro (`World.gold`) é do jogador e **não zera** quando o herói morre.
- Itens não somem com o tempo; no máximo `PICKUP_MAX` no mundo (os mais antigos somem). Evento `('pickup', kind)`
  emitido ao coletar. **Efeitos**: ouro toca `coin_glint` no herói + SFX `coin_pickup`; qualquer cura passa por
  `World.heal(f, amount)` (efeito `heal` verde no personagem + evento `('heal', kind)` + SFX `heal`), então novos itens de
  vida só chamam esse método. **Camadas** (view.py): cenário → caixas → corpos → lutadores → pickups → efeitos → HUD
  (itens ficam à frente dos personagens). Sprites: `potion` 12x16, `coin_bag` 16x16, `coin` 8x8 (ícone do HUD).

## 6. Skills

As skills estão em `.claude/skills/` **dentro do projeto**, então o Claude Code as carrega sozinho quando você inicia
o `claude` nesta pasta (nada a instalar):

- `pixel-sprite-animation` — criar/estender spritesheets de personagens e inimigos com o esqueleto (poses, hurt/death,
  novo personagem, QA de cortes). **Esta versão é mais nova** que a salva na conta do claude.ai (a da conta é a versão
  inicial, só com o cavaleiro).
- `pixel-scenery-assets` — props e tiles de cenário (árvore, casa, poço, rua que se repete, etc.).
- `pixel-vfx-effects` — efeitos (rastros de golpe, sangue, espírito, faíscas) e o GIF de demonstração composto.
- `game-audio-synthesis` — SFX e música sintetizados em Python puro (`sfx_gen.py` regenera `assets/sfx/`:
  `python .claude/skills/game-audio-synthesis/scripts/sfx_gen.py`). Claude não ouve o resultado: o usuário valida de ouvido.

Para tê-las em **todas** as pastas: `python install_skills.py` (copia para `~/.claude/skills`, com backup se já existir).
Se o Claude não parecer conhecer as skills, reinicie a sessão iniciando o `claude` de dentro desta pasta (e peça a ele para listar as skills disponíveis).

### 6.1 Delegar geração de assets ao Haiku? (critério de decisão)

Objetivo: gastar menos tokens. Subagente com `model: "haiku"` (ferramenta Agent) segue as skills normalmente, mas começa
"frio": o prompt precisa ser autossuficiente (o que gerar, quais skills/arquivos ler, convenções da seção 5).
**Antes de cada tarefa de assets, avalie qual caso ela é e diga ao usuário a escolha:**

| Tarefa | Quem executa |
|---|---|
| Recolor/variação de paleta, novo inimigo clonando `ogre_gen.py`, prop de cenário simples, regenerar SFX, rodar `build_assets.py --check` / `check_edges.py` / `tests/test_logic.py` | **Haiku** (mecânica, segue molde existente) |
| Poses/animações novas (IK, frames de golpe 3–4), mudança de linhas do sheet ou da âncora, VFX sincronizado com ataques, qualquer coisa que toque o contrato da seção 5 | **Sonnet** (trabalho fino; erros do Haiku custam mais em retrabalho do que a economia) |

Fluxo econômico quando delegar: (1) Haiku gera numa pasta de saída/worktree separada, sem sujar `assets/`;
(2) verificações automáticas baratas primeiro (`--check`, `check_edges.py`, testes); (3) Sonnet só olha o PNG/GIF final e
aprova ou pede ajuste; (4) integra em `assets/` só depois de aprovado. Limite: Claude não ouve áudio nem julga estética
com precisão — o veredito final de visual/som é do usuário. Na dúvida entre os dois casos, use Sonnet.

### 6.2 Changelog

Mantenha `CHANGELOG.md` atualizado **na mesma sessão** de cada mudança (e inclua-o no commit). Formato: um bloco por
data, mais recente primeiro; **todos os commits do mesmo dia ficam no mesmo bloco** (sem subtítulo); o que ainda não foi
commitado entra no bloco do dia. Categorias: Jogabilidade, Balanceamento (cite a
constante de `config.py` e o valor antes → depois), Arte, Contrato de arte (linhas dos sheets, âncora, frames de golpe),
Áudio, Técnico, Correções, Pendente de validação. Só inclua as categorias que têm itens.

## 7. O que foi e o que NÃO foi testado (leia antes de mexer)

**Testado**: `tests/test_logic.py` (início/câmera, −10 de vida por golpe, `hurt` bloqueando mover/atacar, invulnerabilidade,
3 golpes matam o ogro, contadores, cadáver permanece, respawns nas bordas certas, pausa da IA, luta longa simulada, herói
parado morre). `tests/simulate.py` executa o **`main.py`, `view.py` e `logic.py` reais** com `fake_pygame.py` (um stand-in
em Pillow) e gravou os GIFs de gameplay que o usuário viu. Os geradores de arte reproduzem os PNGs do jogo pixel a pixel.

**NÃO testado — verifique na primeira execução real**
1. Rodar com o **pygame de verdade** no Windows: qualquer diferença entre ele e o stand-in aparece aqui (fonte do HUD —
   `pygame.font.Font(None, 16)` e o acento de "HERÓI", tamanho/DPI da janela, F11, desempenho do `transform.scale`).
2. O **feeling** do combate com teclado real: velocidades, janela da IA, alcance dos golpes, tamanho do knockback —
   tudo em `game/config.py`.
3. `build_exe.bat` (PyInstaller) nunca foi executado.
4. **Sons (10 SFX) criados mas ainda não ouvidos pelo usuário** — volumes/timbres a ajustar. Música (`medieval_theme.wav`, 35 s, loop) também ainda não ouvida; volumes em `config.py` (`MUSIC_VOLUME`).
5. Velocidades: ataques 1,5x e andar 1,2x mais rápidos (multiplicadores em `config.py`: `ATTACK_ANIM_SPEED`, `WALK_ANIM_SPEED`).

## 8. Próximos passos sugeridos (o usuário disse que seguirá o desenvolvimento por aqui)

- Primeiro: rodar `python main.py`, jogar uns minutos e ajustar `config.py` (dificuldade) e quaisquer bugs de pygame real.
- Usar o que já existe nos sheets: correr (Shift), ataque de machado, arco e besta do herói (precisa de projétil).
- Mais inimigos (reaproveitar `ogre_gen.py` com outra paleta/arma), tela de início/pause/game over, som (SFX gerados por
  código ou arquivos), pontuação, partículas de poeira nos passos, sombra sob os personagens.
- Quando for criar arte nova, use as skills acima; quando mudar contratos (linhas dos sheets, âncora), atualize esta
  seção 5 e o `meta` do `.json`.

## 9. Histórico resumido da conversa original

1. O usuário perguntou se Claude gera imagens/spritesheets → sim, por código (Pillow); não é um modelo de difusão.
2. Spritesheet do cavaleiro medieval: pixel art 64x64, 6 frames: idle, walk, run, ataque de espada, ataque de machado.
3. Acrescentados arco e besta (levantar, puxar/mirar, soltar/disparar). Criada a skill de animação de sprites.
4. Cenário: árvore, casa medieval, poço e rua repetível, na escala do cavaleiro. Criada a skill de cenário.
5. `hurt` e `death` do cavaleiro; novo personagem **ogro** (idle, walk, attack, hurt, death) usando o mesmo esqueleto
   (`sprite_rig.py`); quatro efeitos (rastro de espada, rastro de machado, sangue, espírito); GIFs de demonstração.
6. Jogo demo em pygame (este projeto) + testes + GIFs de gameplay simulado.
7. Este pacote: projeto + skills + resumo, para continuar localmente.
