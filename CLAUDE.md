# Knight vs Ogre — resumo do projeto e ponto de partida

> Este arquivo é lido automaticamente pelo Claude Code quando você abre esta pasta. Ele resume tudo que foi
> feito numa conversa anterior (no claude.ai) para que a sessão aqui no seu computador continue de onde parou.
> **Responda em português (pt-BR).** O usuário usa **Windows** e já tem **Python** instalado.

## 1. Em uma frase

Um jogo 2D de combate em **Python + pygame**, com toda a arte em pixel art **gerada por código** (Python + Pillow):
4 classes, ~12 inimigos e 3 chefes, 3 fases temáticas + modo infinito, loja, efeitos e cenário. O plano de
`TASKS_PLAN.md` (T00–T50) foi implementado inteiro (ver `CHANGELOG.md` e `README.md`). Falta a validação por jogo real:
feeling, equilíbrio, sons e estética são do usuário (seção 7).

## 2. Como rodar

```
pip install -r requirements.txt        # pygame
python main.py                         # ou dois cliques em run_game.bat (--endless, --stage 2, --class mage)
build_exe.bat                          # gera dist\KnightVsOgre.exe (PyInstaller, não testado)
python tests/test_logic.py             # testes das regras (não precisam de janela)
python tests/test_scenes.py            # telas, menus, loja (stand-in de pygame em Pillow)
python tests/test_fuzz.py              # 60 s de teclas aleatórias por classe/fase (nada pode quebrar)
python tests/real_pygame_smoke.py      # o jogo com o pygame REAL em modo headless (SDL dummy)
python tests/simulate.py               # roda main.py/view.py reais num "pygame de mentira" e grava GIFs em out/
```

Controles: setas ou A/D andam, **Espaço** pula, **botão esquerdo** ataca (clicar de novo = combo; segurar com a barra cheia = especial), **botão direito** ataque secundário, **1** poção, **2** bomba, **M** som, F11 tela cheia, **Esc** menu. A tabela única é `CONTROLS` em `config.py`.

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
tests/                  test_logic.py (52 testes), test_scenes.py, test_fuzz.py, real_pygame_smoke.py, simulate.py, fake_pygame.py (stand-in em Pillow)
art_tools/              geradores da arte (ver seção 5); build_assets.py regenera tudo em assets/ (knight/ogre/enemy/class/vfx/theme/proj/icons_gen)
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

### 4.3 Sistemas do plano T01–T50 (resumo para quem vai mexer)

- **Tudo é dado**: `FIGHTER_DEFS[kind]` (herói/classe/inimigo/boss: vida, velocidade, sheet, mapa de animações, IA,
  `ai_params`, guarda, boss...), `ATTACKS[id]` (animação, dano, alcance, frames ativos, `next` do combo, `shoot`,
  `area`, `burst`, `cooldown`, `wear`, `guard_break`...), `WEAPONS`, `CLASSES`, `ELITE_MODS`, `STAGES/THEMES`.
  Um ataque/inimigo/classe novo = entradas de dados + uma linha de sheet.
- **Mundo** (`World`): `hero` + `enemies`; `World(stage=None)` = modo infinito (respawn, elenco por abates);
  com `stage` = percurso finito (`_stage`: encontros → `queue` → entram enquanto `alive < max_alive`, arena do boss,
  `stage_clear`, `defeated`). Projéteis (`straight`/`lob` com marcador), `AreaHit`, `timers` (rajadas de especiais).
- **Entrada → telas** (`main.Game`): `sample_inputs` calcula as bordas; pilha de cenas `Title → Select → Play
  (+ Pause/Controls/Defeat/Summary) → Shop → … → End`. `Game.run` / `run_start` = estado que atravessa as fases
  (ouro, poções, arma, armadura, bombas) e o snapshot do início da fase (D9).
- **Arte**: `build_assets.py` regenera tudo; as classes/inimigos são o rig do cavaleiro/ogro com **override
  temporário de paleta** (`enemy_gen.palette`), nunca mudando as saídas já existentes.
- **Eventos** (`world.events` → `audio.SOUND_FOR`): todo evento emitido precisa de som ou estar na lista de mudos do
  teste 50.

## 5. Arte (convenções que o código do jogo assume — não quebre!)

Todos os frames são **64x64, 6 frames por animação, personagem virado para a DIREITA** (o jogo espelha). Um sheet tem
uma linha por animação; **a ordem das linhas e os nomes fazem parte do contrato com o jogo/atlas: só acrescente linhas
no final**. O jogo lê o `fps` de cada animação do `.json`.

| sheet | linhas (na ordem) |
|---|---|
| `knight_spritesheet` | idle(6fps), walk(10), run(12), attack_sword(12, golpe LATERAL), attack_axe(10), attack_bow(10), attack_crossbow(10), hurt(10), death(8), jump_up(12), jump_fall(10), attack_sword_2(12, combo: corte ascendente), attack_sword_3(12, combo: golpe final de cima para baixo), attack_special(12, giro: frame 0 = carga, congelado enquanto segura), throw(12, arremesso de faca; a faca sai no frame 3) |
| `ogre_spritesheet` | idle(6), walk(10), attack(10, machado), hurt(10), death(8) |
| `knight_axe_spritesheet` | **mesmas linhas e nomes do `knight_spritesheet`**, mas o herói empunha o machado (arquivo gerado por `knight_gen.py write_sheet(out, 'axe')`); o jogo usa a linha `attack_axe` |
| `knight_bow_spritesheet`, `knight_xbow_spritesheet` | idem: **mesmas linhas e nomes** do `knight_spritesheet`, o herói carregando arco / besta nas poses de corpo a corpo (`render` aceita `hold='bow'/'xbow'`); o jogo usa `attack_bow` / `attack_crossbow` (flecha/virote nasce no frame 4) |
| `soldier_spritesheet` | idle(6), walk(10), attack(12, golpe lateral da espada, frames 3-4), hurt(10), death(8) — contrato do ogro; gerado por `enemy_gen.py` (cavaleiro com paleta inimiga) |
| `spearman_spritesheet` | contrato do ogro (idle, walk, attack(12, estocada, frames 3-4), hurt, death); lança carregada inclinada (`hold='spear'`); `enemy_gen.py` |
| `archer_spritesheet` | contrato do ogro; `attack` = poses do arco (a flecha sai no frame 4, projétil `lob`); arco carregado nas demais linhas |
| `shieldman_spritesheet` | contrato do ogro + linha `guard`(6, escudo erguido; é o estado parado do jogo) **no final**; escudo na mão livre |
| `orc_`, `goblin_`, `kobold_`, `minotaur_spritesheet` | contrato do ogro (idle, walk, attack, hurt, death), gerados por `enemy_gen.py` a partir do `ogre_gen` (recolor / escala 0,72 / 0,8 / 1,1 / chifres); o minotauro usa a linha `attack` congelada no frame 2 como pose de investida |
| `ogre_captain_`, `minotaur_lord_`, `black_knight_spritesheet` | **chefes: quadros 96x96** (meta do json: `frame_size` 96, `anchor_x` 48 = coluna do quadril, `ground_row` 90 = linha do chão; espelhado = 95−48). Linhas do contrato do ogro (o cavaleiro negro ainda `attack_2`, `attack_3`, `guard` no final); gerados por `enemy_gen.py` com escala 1,5 / 1,45 / 1,3 |
| `ranger_spritesheet` (e as outras classes: `crossbowman_`, `mage_`) — mago: `attack_staff`(12), `_2`, `_3`, `attack_stomp`(12); besteiro: `attack_crossbow_2/_3`(10), `attack_axe_small`(10) | **linhas do `knight_spritesheet`** (idle … throw, o herói carregando a arma da classe) + as da classe: o `attack_special` é **substituído** pelo especial da classe e são anexadas `attack_bow_2`(10), `attack_bow_3`(10), `attack_short`(12). Gerado por `art_tools/class_gen.py` |
| `vfx_spritesheet` | sword_slash(12), axe_slash(10), blood_splash(12), spirit(6), heal(10), coin_glint(12), sword_slash_2(12), sword_slash_3(12), spin_slash(12, aro do especial), charge(10, brasas enquanto segura), block_spark(14, na frente do escudo), stone_spikes(12, espinhos do mago), fire_burst(14, explosão) |

- **Âncora** (quadros de 64): coluna do quadril = 30 no frame normal, **33 quando espelhado** (63−30); linha do chão = 58 dentro do frame
  (no jogo `GROUND_Y = 217`). Posicione sempre por essa coluna, senão o sprite "pula" ao virar.
- Animações de ataque têm o golpe nos **frames 3–4**; o efeito `i` toca junto com o frame `3+i` do ataque.
- No cavaleiro o frame 4 do arco e da besta é o disparo (a flecha/virote só é desenhada nesse frame; o projétil de verdade
  teria de ser criado pelo jogo). **Arco, besta e machado do cavaleiro são usados como armas pickup (T13/T14)** (a animação `run` já é usada ao andar).
- Cenário: `tree` 112x128, `medieval_house` 160x160, `well` 48x64, `street_tile` 64x40 (repetível na horizontal),
  `box` 24x24 (caixote; contorno nas 4 bordas; caixas empilhadas compartilham a linha de contorno, 23 px por nível).
  O último pixel sólido de cada objeto é o chão (a linha de baixo é o contorno).
- Temas de fase (`game/stages.py THEMES`, arte em `art_tools/theme_gen.py`): cada tema tem tile de chão 64x40 repetível, props (mesma convenção: último pixel sólido = chão, linha abaixo = contorno), cores de céu/colinas e decorações de parallax (`castle`). `plain`: tent 82x60, banner 24x66, palisade 68x36, planted_swords 34x36, dead_tree 64x90, cart 80x48, campfire 24x20, grass_tile. `forest`: oak 140x156, fern 34x26, log 78x30, mushrooms 26x20, stone_wall 88x50, bush 50x34, forest_tile; parallax `treeline` + `fog` (gerados no `view.py`). `city`: market_stall 90x70, barrels 42x40, lamppost 22x80 (+ medieval_house, well, street_tile); parallax `skyline` + `wall`.
- Projéteis (`art_tools/proj_gen.py`, PNG soltos `proj_*.png` virados para a direita): arrow (+ `u45/u90/d45/d90` inclinadas), bolt, knife, fireball, rock, bomb. Ícones de HUD 12x12 (`icons_gen.py`): armor, sword, axe, bow, xbow, knife, staff.
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

**Testado automaticamente** (rode tudo antes de commitar; os três primeiros não precisam de janela):
- `tests/test_logic.py` (52 testes, inclui o contrato arte × dados): dano/hurt/invulnerabilidade, vários inimigos, ataques como dados, projéteis e
  áreas, poções, combo, machado/arco/besta, armadura, barra de combo e especial, fichas e elites, cada inimigo, fases
  (encontros, arena, boss, derrota, renascer), curva de dificuldade, classes, secundário, loja/bombas, mapa de áudio.
- `tests/test_scenes.py`: pilha de telas com o stand-in Pillow (título, classe, pausa, comandos, derrota, conclusão,
  loja, fim); `tests/real_pygame_smoke.py`: o jogo com o **pygame de verdade** em modo headless.
- `python art_tools/build_assets.py --check` (assets = geradores) e `check_edges.py` (cortes nos quadros).
- `tests/simulate.py` grava GIFs de gameplay (modo infinito).
- Um bot ingênuo (aperta o ataque sem esquivar) vence a fase 2 sempre, a fase 1 às vezes e perde a fase 3 — serve só
  de régua grosseira.

**NÃO testado — valide jogando**
1. O **feeling** com teclado e mouse reais: velocidades, janelas de combo/especial, alcance, recargas, knockback,
   telegrafia dos inimigos (minotauro, arqueiro) e **equilíbrio** (vida, dano, preços da loja, drops) — tudo em
   `game/config.py` e `game/stages.py`.
2. **Estética** da arte nova vista só em imagens estáticas (poses de combo/especial, as 3 classes novas, os chefes,
   temas, projéteis de 8–16 px, HUD com fonte real).
3. **Sons**: 29 SFX sintetizados (12 originais + 17 da passada de áudio) e a música nunca foram ouvidos pelo usuário.
4. `build_exe.bat` (PyInstaller): ver o CHANGELOG; rode no Windows do usuário antes de distribuir.
5. Modo infinito: elenco por abates e multidão máxima 3 (`ENDLESS_*`) são escolhas minhas.

## 8. Próximos passos sugeridos

- Jogar de ponta a ponta (campanha com cada classe), anotar o que está fácil/difícil/injusto e ajustar `config.py` /
  `stages.py`; ouvir os SFX e a música.
- Ideias que ficaram fora: persistência entre execuções (T51), correr com Shift, música por fase, mais chefes e
  inimigos, pontuação, partículas de poeira, sombra sob os personagens, remapear teclas, joystick.
- Quando for criar arte nova use as skills; quando mudar contratos (linhas dos sheets, âncora, tamanho de quadro)
  atualize a seção 5 e o `meta` do `.json`. Os scripts das skills em `.claude/skills/*/scripts` são cópias das
  ferramentas de `art_tools/`: mantenha-os em sincronia.

## 9. Histórico resumido da conversa original

1. O usuário perguntou se Claude gera imagens/spritesheets → sim, por código (Pillow); não é um modelo de difusão.
2. Spritesheet do cavaleiro medieval: pixel art 64x64, 6 frames: idle, walk, run, ataque de espada, ataque de machado.
3. Acrescentados arco e besta (levantar, puxar/mirar, soltar/disparar). Criada a skill de animação de sprites.
4. Cenário: árvore, casa medieval, poço e rua repetível, na escala do cavaleiro. Criada a skill de cenário.
5. `hurt` e `death` do cavaleiro; novo personagem **ogro** (idle, walk, attack, hurt, death) usando o mesmo esqueleto
   (`sprite_rig.py`); quatro efeitos (rastro de espada, rastro de machado, sangue, espírito); GIFs de demonstração.
6. Jogo demo em pygame (este projeto) + testes + GIFs de gameplay simulado.
7. Este pacote: projeto + skills + resumo, para continuar localmente.
