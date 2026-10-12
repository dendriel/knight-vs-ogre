# Changelog

Formato: um bloco por data, mais recente primeiro (todos os commits do mesmo dia ficam juntos); mudanças ainda não
commitadas entram no bloco do dia, ou em **[Não lançado]** se forem de outra data.
Constantes entre crases estão em `game/config.py`. Só aparecem as categorias que têm itens.
Categorias: Jogabilidade · Balanceamento · Arte · Contrato de arte · Áudio · Técnico · Correções · Pendente de validação.

## [2026-10-12]

### Jogabilidade
- T05: **Esc abre o menu** (Continuar · Ver comandos · Reiniciar fase · Sair) em vez de fechar o jogo; navegação por ↑/↓/W/S + Enter ou por mouse; o mundo fica congelado. 'Ver comandos' lê a tabela `CONTROLS` de `config.py`. Reiniciar fase recria o mundo (ouro e itens da tentativa voltam ao zero). O clique que fecha um menu não dispara um golpe.
- T10: poções agora vão para um **inventário** (até 10, `POTION_MAX_STOCK`; com 10 a poção fica no chão) e a tecla **1** bebe uma (+`POTION_HEAL`, só com vida < máxima). Substitui o antigo 'consumir ao pegar'. HUD mostra `n/10` com o ícone da poção; o estoque não zera quando o herói morre.

### Arte
- T04: novos sprites de projétil (`proj_arrow` + variantes inclinadas `u45/u90/d45/d90`, `proj_bolt`, `proj_knife`, `proj_fireball`, `proj_rock`) gerados por `art_tools/proj_gen.py` e desenhados em camada própria (com sombra no chão).
- T06: ícones de HUD 12x12 (`icon_armor`, `icon_sword`, `icon_axe`, `icon_bow`, `icon_xbow`, `icon_knife`, `icon_staff`) gerados por `art_tools/icons_gen.py`.

### Áudio
- T10: pegar poção reaproveita o SFX `coin_pickup`; beber usa o `heal` existente (evento `potion`).

### Técnico
- T00: `README.md` TODO reorganizado por fundação/cavaleiro/inimigos/fases/classes/economia (fases duplicadas unidas, vocabulário fixo fase/cenário/tela, IDs das tarefas do `TASKS_PLAN.md`).
- `README.md`: nova seção **TODO** com as ideias planejadas (armas pickup com durabilidade, arco/besta, classes, inimigos, fases e bosses, loja, poções e armadura).
- `TASKS_PLAN.md`: plano de execução das tarefas do TODO (incoerências corrigidas, dependências, ordem, proposta por tarefa e decisões D1–D7 incorporadas; D8–D10 em aberto com padrão recomendado). `README.md` TODO ganhou dificuldade crescente, derrota (renascer por 100 de ouro ou reiniciar) e menu do Esc.
- `README.md` TODO: 3 fases temáticas (planície, floresta inglesa, cidade), novos inimigos humanos (cavaleiro, arqueiro, lanceiro, cavaleiro com escudo), combo de até 3 golpes no ataque primário e ataque especial com barra de combo.
- T01: `FIGHTER_DEFS[kind]` (vida, velocidade, meia-largura, mapa de animações, efeito de golpe, alcance, IA) substitui as tabelas soltas; `ANIM/SLASH/REACH` continuam como alias. Funil único de dano `World.apply_damage` e `World.stats` (kills, damage_dealt, damage_taken, gold_gained). Teste 22.
- T02: `World.enemies` (lista) substitui o ogro único; estado de IA (`ai_wait`, `ai_cooldown`, `respawn_t`) passa para cada `Fighter`; golpes cruzam o herói com todos os inimigos (um golpe atinge todos ao alcance, um acerto por alvo por golpe, `hit_set`); no modo infinito o 'spawner' mantém `spawn_target` = 1 inimigo (comportamento igual ao anterior). `World.ogre`/`ai_wait`/`ai_cooldown` continuam como propriedades de compatibilidade. Teste 23.
- T03: `ATTACKS[id]` (animação, dano, alcance, frames ativos, frame do rastro, efeito, fator de movimento, knockback, `guard_break`, cooldown, desgaste) e `Fighter.attack_id`; `World.start_attack()`. Ataques do herói (`sword`) e do ogro (`ogre_axe`) idênticos aos anteriores. Um ataque novo = uma entrada + uma linha de sheet. `load_timing` lê todo `*_spritesheet.json` e o lutador usa `defn['sheet']` para animação/desenho. Teste 24.
- T04: `Projectile` (`straight`: voa reto e acerta o 1º alvo na faixa vertical, com `pierce` opcional; `lob`: parábola até onde o alvo estava, com marcador de queda no chão, dá para desviar), `AreaHit` (caixa com atraso/duração, multi-alvo, um acerto por alvo), `World.shoot()`, `World.add_area()`, eventos `shoot`/`impact`. Novas constantes `PROJ_CHEST`, `ARROW_SPEED`, `ARROW_RANGE`, `LOB_FLIGHT`, `LOB_APEX`, `LOB_RADIUS`. `_hit` aceita `at`/`src_x` (dano/knockback de projétil). `build_assets.py` não reescreve PNG com pixels idênticos. Teste 25.
- T05: `Inputs` ganha `attack_pressed/released`, `attack_held_t`, `secondary(_pressed)`, `potion_pressed` (bordas calculadas em `Game.sample_inputs`); pilha de cenas em `main.py` (`PlayScene`, `PauseScene`, `ControlsScene` em `game/scenes.py`; menu em `game/ui.py`); `Game.to_internal` converte o mouse para a tela de 480x270. `fake_pygame` simula botão direito, tecla 1, Enter, cliques e movimento do mouse. Novos `tests/test_scenes.py` e `tests/real_pygame_smoke.py` (jogo com o pygame real em modo headless).
- T06: HUD do herói reorganizado em slots que empilham sob a barra de vida e só existem quando a feature existe (`World.features`: `armor`, `combo`, `weapon`, `potions`); posições fixas em `config.HUD`; novas constantes `COMBO_BAR_MAX` = 100 e `POTION_MAX_STOCK` = 10. Com nenhuma feature o HUD fica igual ao anterior.
- T10: `World.potions`, `World.drink_potion()`; comandos ganham a tecla 1; testes 19–21 migrados e novo teste 26.

### Pendente de validação
- Legibilidade dos projéteis (8–16 px) e do marcador de queda no pygame real; ainda não há ataque do jogo que dispare projéteis (entram em T14/T23/T41).

## [2026-10-11]

### Jogabilidade
- Pulo no **Espaço** (altura ≈ a do cavaleiro, move-se no ar); o ataque passa para o **botão esquerdo do mouse**.
- O cavaleiro anda enquanto ataca (sem virar de lado) e pode pular atacando.
- Personagens não colidem: atravessam-se, e o alcance do golpe (`KNIGHT_REACH`/`OGRE_REACH`, início em −12) cobre alvo sobreposto.
- Caixas de meio cavaleiro de altura: dá para pousar em cima e atravessar no chão. Caixa solta no slot 0 e escada de 1-2-3 caixas no slot 2.
- Alcance vertical (`VERTICAL_REACH` = 30): fora dele ninguém acerta; o ogro espera embaixo sem balançar o machado.
- Cair de uma caixa sem ter pulado toca a animação de queda.

- Pickups: ao morrer, o ogro tem 30% de chance de derrubar uma poção vermelha (+30 de vida, limitada a `HERO_MAX_HP`) e, em sorteio separado, 50% de uma bolsa de ouro com 5–10 moedas. Só o herói coleta (por proximidade); poção com vida cheia fica no chão.
- Itens ficam à frente dos personagens (antes apareciam atrás do corpo do ogro).
- Efeito `heal` (luz verde subindo pelo corpo) ao recuperar vida e `coin_glint` (estrela dourada) ao pegar ouro.
- Contador de ouro no HUD, logo abaixo da vida do herói; o ouro não zera quando o herói morre.

### Balanceamento
- `OGRE_MAX_HP` 100 → 30 (3 golpes); barras de vida usam o máximo de cada lutador.
- `HERO_SPEED` 84 → 120; o herói usa a animação `run` (`RUN_ANIM_SPEED` = 1,65).
- Ataque de espada 1,5x → 2,0x (`KNIGHT_ATTACK_ANIM_SPEED`); o do ogro continua 1,5x (`ATTACK_ANIM_SPEED`).
- Invulnerabilidade do ogro após dano: 1,2 s → 1,0 s (`OGRE_HURT_INVULN_EXTRA` = 0,4; o herói segue com `HURT_INVULN_EXTRA` = 0,6).
- Experimento revertido: ogro sem invulnerabilidade pós-dano (`OGRE_HURT_INVULN = False`) morria rápido demais.
- Pausa do ogro antes de bater (`OGRE_WAIT_BEFORE_ATTACK`) 0,55–0,95 s → 0,35–0,65 s.
- Novas constantes de pickups: `POTION_HEAL` 30, `POTION_DROP_CHANCE` 0,30, `COIN_BAG_DROP_CHANCE` 0,50 (valor escolhido, não pedido), `COIN_BAG_COINS` (5, 10), `PICKUP_RADIUS` 14, `PICKUP_REACH_Y` 24, `PICKUP_MAX` 30.
- Novas constantes: `JUMP_HEIGHT` 44, `JUMP_RISE_TIME` 0,34, `BOX_H` 23, `BOX_W` 24, `ATTACK_MOVE_FACTOR` 1,0.

### Arte
- `attack_sword` trocou o golpe por cima por uma varredura lateral (lâmina na altura do ombro, de trás para a frente); `sword_slash` regenerado com arco raso na altura do peito para acompanhar a nova pose.
- Novas animações do cavaleiro `jump_up` e `jump_fall`.
- Novo sprite de cenário `box` (caixote de madeira 24x24).
- Novas linhas do `vfx_spritesheet`: `heal` (efeito genérico de cura) e `coin_glint`.
- Novos sprites `potion` (12x16), `coin_bag` (16x16) e `coin` (8x8, ícone do HUD).

### Contrato de arte
- `knight_spritesheet`: só a linha `attack_sword` mudou (e `sword_slash` no VFX); linhas 9 (`jump_up`) e 10 (`jump_fall`) anexadas; as demais inalteradas pixel a pixel.
- `vfx_spritesheet`: linhas 4 (`heal`) e 5 (`coin_glint`) anexadas; as 4 anteriores inalteradas pixel a pixel.
- `assets/potion.png`, `coin_bag.png` e `coin.png` novos (sheets inalterados).
- `assets/box.png` novo; caixas empilhadas compartilham a linha de contorno (23 px por nível).

### Correções
- O ogro atacava para um lado enquanto o herói passava por ele para o outro: agora ele se vira durante a preparação do golpe (antes do frame ativo) e trava a direção só no golpe.

### Áudio
- Novos SFX `coin_pickup` (dois blips agudos) e `heal` (arpejo suave ascendente), gerados em `sfx_gen.py`; mapeados nos eventos `pickup`/`heal`.

### Técnico
- Primeiro commit do jogo completo: código, `art_tools/`, `assets/`, testes e as 4 skills do projeto.
- `.gitignore` com Python, `out/`, `build/`, `dist/` e configurações locais do Claude Code.
- `World.heal()` centraliza a cura (efeito + som); teste 21 cobre efeitos, eventos e arquivos de som.
- Testes 18–20 de pickups (chances, coleta só pelo herói, cura limitada, ouro persiste).
- Novos testes de pulo, caixas, escada, alcance vertical, sobreposição, ataque em movimento e direção do ogro (`tests/test_logic.py`).
- `tests/fake_pygame.py` e `tests/simulate.py` passam a simular o botão esquerdo do mouse.
- `CLAUDE.md`: seção 4.1 (pulo, caixas, alcance), critério de delegação ao Haiku (6.1) e regra do changelog (6.2). Este changelog.

### Pendente de validação
- Pickups no pygame real: tamanho/legibilidade dos sprites e posição do contador de ouro no HUD (fonte real). Sons `coin_pickup` e `heal` e os efeitos `heal`/`coin_glint` ainda não vistos/ouvidos em jogo real. A chance de 50% da bolsa foi escolhida por mim.
- Feeling do pulo, do ataque lateral e da velocidade nova com teclado e mouse reais (pygame de verdade).
- Sprites `jump_up`/`jump_fall` vistos só em imagem estática, não em movimento.
