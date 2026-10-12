# Changelog

Formato: um bloco por data, mais recente primeiro (todos os commits do mesmo dia ficam juntos); mudanças ainda não
commitadas entram no bloco do dia, ou em **[Não lançado]** se forem de outra data.
Constantes entre crases estão em `game/config.py`. Só aparecem as categorias que têm itens.
Categorias: Jogabilidade · Balanceamento · Arte · Contrato de arte · Áudio · Técnico · Correções · Pendente de validação.

## [2026-10-12]

### Jogabilidade
- T05: **Esc abre o menu** (Continuar · Ver comandos · Reiniciar fase · Sair) em vez de fechar o jogo; navegação por ↑/↓/W/S + Enter ou por mouse; o mundo fica congelado. 'Ver comandos' lê a tabela `CONTROLS` de `config.py`. Reiniciar fase recria o mundo (ouro e itens da tentativa voltam ao zero). O clique que fecha um menu não dispara um golpe.
- T10: poções agora vão para um **inventário** (até 10, `POTION_MAX_STOCK`; com 10 a poção fica no chão) e a tecla **1** bebe uma (+`POTION_HEAL`, só com vida < máxima). Substitui o antigo 'consumir ao pegar'. HUD mostra `n/10` com o ícone da poção; o estoque não zera quando o herói morre.
- T11: **combo de 3 golpes** no botão esquerdo: clicar de novo durante o golpe (a partir do frame `COMBO_WINDOW_START` = 3 e até `COMBO_BUFFER` = 0,15 s depois do fim) encadeia corte ascendente e golpe final (dano 10/10/15; o 3º alcança 6 px a mais e empurra 24 px). Depois do 3º volta ao 1º; levar dano cancela a cadeia; segurar o botão sem clicar só repete o 1º golpe.
- T13: o ogro derruba seu **machado** (`AXE_DROP_CHANCE` 0,15, sorteio separado) como pickup; o herói que o pega ataca com ele no lugar da espada: dano `AXE_DAMAGE` 20 (espada 10), alcance `AXE_REACH` +8, golpe `AXE_ANIM_SPEED` 1,26 (≈1,35x mais lento que o golpe 1), `AXE_MOVE_FACTOR` 0,8, empurra `AXE_KNOCKBACK` 24 e ignora guarda. Cada golpe gasta `AXE_WEAR` = 3% de durabilidade (barra no HUD); em 0% quebra (evento `break`, tremor) e o herói volta à espada, indestrutível. A arma é do herói: um herói novo nasce com a espada.
- T15: **armadura**: o ogro tem `ARMOR_DROP_CHANCE` = 0,10 de derrubar uma peça (`ARMOR_PICKUP` 50, teto `ARMOR_MAX` 50, não é consumida com a barra cheia). Todo dano desconta da armadura antes da vida; ao zerar, a sobra do golpe vai para a vida e toca `armor_break`. O `hurt` continua tocando. Barra azul no HUD sob a vida.
- T12: **barra de combo** (laranja, pisca quando cheia): +`COMBO_GAIN_DEALT` 1,5 por ponto de dano causado e +`COMBO_GAIN_TAKEN` 1,0 por ponto recebido, cheia em `COMBO_BAR_MAX` = 100. Com ela cheia, segurar o ataque por `SPECIAL_HOLD_MIN` = 0,25 s **carrega** (anda a `CHARGE_MOVE_FACTOR` 0,35) e soltar dispara o **giro especial**: 2 golpes de `SPECIAL_DAMAGE` 15 num raio de `SPECIAL_RADIUS` 56 para os dois lados, ignora invulnerabilidade e guarda, herói invulnerável durante o giro. Clique rápido com a barra cheia continua sendo golpe normal. A barra zera ao usar o especial e quando o herói morre (D2); o especial não recarrega a barra.
- T14: **arco e besta** como pickups raros (`BOW_DROP_CHANCE` 0,06, `XBOW_DROP_CHANCE` 0,04; durabilidade como a do machado). O ataque primário vira um tiro em linha reta que nasce no frame 4 da animação: arco = dano `BOW_DAMAGE` 10, `BOW_RANGE` 280, `BOW_WEAR` 2,5%/tiro; besta = virote de `XBOW_DAMAGE` 20, `XBOW_RANGE` 380, recarga `XBOW_RELOAD` 0,8 s, `XBOW_WEAR` 4%/tiro. O herói anda a 50% / 40% da velocidade enquanto atira.
- T26: **fichas de ataque**: só `MAX_ATTACKERS` = 2 inimigos podem preparar/dar golpe ao mesmo tempo; os demais cercam o herói a uma distância crescente (`STANDOFF_BASE` 14 + `STANDOFF_STEP` 8 por posição na fila) sem parar de encarar. A ficha volta ao fim do golpe, ao levar dano, ao morrer ou quando o herói foge. **Variantes elite** sem arte nova (tinta de cor): *veterano* (+25% velocidade, espera −30%), *bruto* (+60% vida, golpe 15) e *ágil* (+40% velocidade, −30% vida).
- T22: novo inimigo **soldado** (cavaleiro com armadura violeta): `SOLDIER_MAX_HP` 20 (2 golpes), `SOLDIER_SPEED` 62 (ogro 50), espera `SOLDIER_WAIT` 0,25–0,5 s e descanso `SOLDIER_COOLDOWN` 0,7–1,1 s, golpe de espada de 10. HUD mostra o nome do inimigo mais próximo (`label`) e a variante elite.
- T21: novo inimigo **lanceiro** (armadura de couro, tabardo verde): `SPEARMAN_MAX_HP` 25, `SPEARMAN_SPEED` 52, alcance `SPEARMAN_REACH` (18, 62) — acerta a ~55 px onde o ogro não alcança, mas tem **zona morta** de 18 px (herói colado não é atingido); para a `SPEARMAN_ATTACK_DIST` 56, espera 0,4–0,7 s e descansa 1,0–1,5 s; se o herói chega a menos de `SPEARMAN_RETREAT_DIST` 24 durante o descanso ele recua.
- T23: novo inimigo **arqueiro** (couro bege, tabardo laranja): `ARCHER_MAX_HP` 15, fica a ~`ARCHER_KEEP_DIST` 170 px do herói (recua se chegar a menos de `ARCHER_TOO_CLOSE` 110, avança se longe), mira 0,45–0,8 s e solta a flecha no frame 4 em **parábola** (`LOB_FLIGHT` 0,95 s, `LOB_APEX` 70) para onde o herói estava: um marcador vermelho/laranja no chão mostra onde cai (raio `LOB_RADIUS` 12) e dá tempo de desviar. Não usa ficha de ataque.
- T24: novo inimigo **escudeiro** (armadura azul): `SHIELDMAN_MAX_HP` 30. **Bloqueia golpes e flechas de frente** (sem dano, faísca `block_spark`, recua `BLOCK_KNOCKBACK` 8 px, não fica atordoado); só toma dano pelas costas, enquanto ataca/atordoado, ou de golpes com `guard_break` (machado e giro especial). Vira o escudo com atraso `SHIELD_TURN_DELAY` 0,5 s, então dá para passar por trás (os personagens se atravessam).
- T25: **monstros**: *orc* (`ORC_MAX_HP` 40, 56 px/s, machado), *goblin* (10 de vida = 1 golpe, 70 px/s, dano 5, alcance curto, ataca rápido; vem em bando), *kobold* (12 de vida, atira **pedras em parábola** de longe, dano 5) e *minotauro* (50 de vida, machado de 15, **investida telegrafada**: pose com o machado erguido por 0,7 s e depois corre 240 px/s por 0,6 s causando 15; pular por cima desvia; fica 1 s cansado). **Modo infinito**: o elenco cresce com os abates (`ENDLESS_ROSTER`: ogro → soldado (2) → goblin (4) → lanceiro (5) → arqueiro (7) → escudeiro (8) → orc (9) → kobold (10) → minotauro (12)); a partir de 8 abates 25% dos novos podem ser elite; +1 inimigo simultâneo a cada 5 abates (até 3).
- T30: **fases**: percurso finito da esquerda para a direita (`game/stages.py`: `Stage` com tema, comprimento, encontros por progresso `p`); a câmera trava nas pontas, os inimigos entram pela direita quando o herói cruza a linha do encontro (uma vez só), sem reposição automática; a fase termina com todos os encontros disparados, todos derrotados e o herói a `STAGE_FINISH_DIST` 30 px do fim. Morrer **não** renasce sozinho em fase (estado `defeated`; a tela de derrota é a T37). O modo infinito continua igual. A campanha tem 3 fases (tabelas iniciais; a curva de dificuldade vem na T36). HUD mostra nome da fase e barra de progresso com marcas dos encontros.
- T30: o jogo agora abre num **menu inicial** (Campanha · Modo infinito · Ver comandos · Sair); `--endless` / `--stage N` pulam o menu.
- T36: **dificuldade crescente**: cada fase tem 3 trechos por progresso (abertura 0–35%, meio 35–75%, pré-boss 75–100%) com `max_alive` e `max_attackers` próprios (fase 1: 2/1 → 3/2 → 3/2; fase 2: 3/2 → 4/2 → 5/3; fase 3: 4/2 → 5/3 → 6/3). Os encontros entram numa fila e os inimigos aparecem pela borda direita enquanto houver menos de `max_alive` vivos; a fração de elites sorteados cresce com o progresso (fase 1 só a partir de 75%); as bolsas de ouro pagam mais no fim (fase 1 ×1,0→1,4; fase 3 ×1,6→2,2). Encontros da fase 1 conforme a seção 4.2 do plano.
- T37: **tela de derrota** (só em fase): *Renascer aqui — 100 ouro* (`REVIVE_COST`; desabilitado com aviso se faltar ouro) levanta o herói onde caiu com vida cheia, `REVIVE_INVULN` 2 s, barra de combo zerada; inimigos, fila e encontros mantêm o estado e poções/arma/armadura são mantidas (D10). *Reiniciar a fase* volta ao **snapshot do início da fase** (ouro, poções, arma, armadura da entrada; D9), o mesmo vale para *Reiniciar fase* do Esc. *Menu inicial* volta ao título.
- T31: **tela de conclusão** da fase: monstros derrotados, dano causado, dano recebido, ouro adquirido (só desta fase), renascimentos e tempo; *Continuar* leva o estado da run (ouro, poções, arma, armadura — D6) para a fase seguinte; depois da fase 3 aparece "FIM DA DEMO" com volta ao menu inicial.
- T33: **tema Planície** na fase 1: céu claro, colinas verdes, castelo distante com fumaça no parallax, chão de grama e terra; cenário com tendas listradas, estandartes, paliçadas, espadas fincadas, árvore seca, carroça de feno e fogueira.
- T32: **chefe e arena** no fim de cada fase: depois do último encontro, ao entrar na última tela do percurso (a `ARENA_ENTER_MARGIN` 30 px) a tela trava (a câmera desliza até ela; paredes à esquerda e à direita) e o chefe entra pela direita; a barra de vida dele aparece embaixo. Ao morrer ele solta 2 poções + bolsa de `BOSS_LOOT_COINS` 30–50 ouro, a tela é liberada, aparece a seta >>> e a fase só termina quando o herói chega ao fim. Fase 1: **Ogro-Capitão** (`CAPTAIN_MAX_HP` 90, golpe largo de 15 que ignora guarda; chama 2 soldados com metade da vida). Fase 2: **Rei Minotauro** (120 de vida, investida mais rápida e frequente, chama goblins e kobold). Fase 3: **Cavaleiro Negro** (110 de vida, combo próprio de 3 golpes, guarda com escudo, chama 2 arqueiros). Comprimentos das fases: 3600 / 4000 / 4400 px.
- T34: **tema Floresta inglesa** na fase 2: céu verde-acinzentado, linha de árvores no horizonte, névoa em parallax, chão de musgo escuro; carvalhos densos, samambaias, tronco caído, cogumelos, muro de pedra e arbustos com frutas.
- T35: **tema Cidade** na fase 3: céu quente, silhueta de telhados e torres ao fundo, muralha com torres e ameias no parallax, rua de pedra; casas, barracas de feira, barris empilhados, postes de lampião e poço.
- T41: **ataque secundário** no botão direito do mouse: o cavaleiro arremessa uma **faca** em linha reta (`KNIFE_DAMAGE` 8, `KNIFE_SPEED` 340, `KNIFE_RANGE` 300), infinita e limitada só pela recarga `KNIFE_COOLDOWN` 1,0 s (D3; funciona com qualquer vida e com arma pickup na mão); o HUD mostra o ícone com a barra de recarga.
- T42: nova classe **Arqueiro** (por enquanto `python main.py --class ranger`; a seleção chega na T45): `RANGER_MAX_HP` 80, `RANGER_SPEED` 135 (cavaleiro 120), pulo 1,1x. Primário = **arco** com combo de 3 flechas (dano 8 / 8 / 14; a 3ª atravessa os inimigos); secundário (botão direito) = **espada curta** (dano 10, recarga 0,45 s); especial (barra cheia, segurar e soltar) = **chuva de flechas** (`RAIN_COUNT` 10 flechas de dano 8 caindo de 60 a 230 px à frente, com marcador no chão; um golpe sofrido interrompe o resto). Armas pickup não valem para esta classe (sem arte).
- T45: **tela de seleção de classe** depois de Campanha / Modo infinito: cartões lado a lado com o quadro `idle` ampliado, nome, 4 barras (vida, velocidade, dano, alcance) e os 3 ataques; ←/→ + Enter ou clique escolhem; Esc volta. `--class ranger` pula o menu.
- T43: nova classe **Besteiro** (armadura ferrugem): `XBOWMAN_MAX_HP` 110, `CROSSBOWMAN_SPEED` 105 (a mais lenta), pulo 0,9x. Primário = **besta** com combo de 3 virotes (dano 14 / 14 / 22, a 3ª atravessa; mira mais lenta no 1º; só reinicia a cadeia `XBOW_HERO_RELOAD` 0,8 s depois do 1º virote); secundário = **machado pequeno** (dano 12, ignora escudo, recarga 0,6 s); especial = **rajada de virotes** (`VOLLEY_COUNT` 6 virotes perfurantes de dano 10).
- T44: nova classe **Mago** (túnica violeta, chapéu pontudo, cajado): `MAGE_MAX_HP` 70 (a mais frágil), `MAGE_SPEED` 115. Primário = **bolas de fogo** em combo de 3 (dano 12 / 12 / 16; a 3ª explode num raio de `FIREBALL_EXPLOSION` 36 px com dano 10 nos vizinhos); secundário = **espinhos de pedra** (área à frente de 22 a 104 px, dano 14 em todos, atraso 0,12 s, recarga 1,4 s); especial = **tempestade de fogo** (`STORM_COUNT` 12 bolas de fogo caindo num raio de 170 px dos dois lados, dano 10, com explosão no chão).
- T50: **loja** entre as fases (depois da conclusão, antes da seguinte; também ao reiniciar a fase pela derrota ou pelo Esc, com o snapshot do início da fase — se houver ouro para comprar algo): poção 25, armadura 60 (`SHOP_PRICES`), arma pickup só para o cavaleiro (machado 70, arco 80, besta 100) e **bomba** 30 (consumível arremessável, **tecla 2**, `BOMB_DAMAGE` 25 num raio de 40, estoque `BOMB_MAX_STOCK` 5 — D8); o que se compra entra equipado na fase. O fluxo completo é Título → Classe → Fase 1 → Conclusão → Loja → Fase 2 → … → Fim. O modo infinito não tem loja.

### Balanceamento
- T11: `KNIGHT_ATTACK_ANIM_SPEED` 2.0 → 1.7 (golpe 1 mais lento); novos `KNIGHT_COMBO2_ANIM_SPEED` = 2.4 e `KNIGHT_COMBO3_ANIM_SPEED` = 2.6, `COMBO_DAMAGE` = (10, 10, 15), `COMBO_KNOCKBACK` = (14, 14, 24).
- T11: `OGRE_RETALIATE_WAIT` (0,15–0,35) → (0,05–0,18): com o golpe 1 mais lento, apertar sem parar travava o ogro (o revide dele caía fora da janela de invulnerabilidade); agora o revide acontece antes de ela acabar.
- T12: constantes novas `COMBO_GAIN_DEALT` 1,5, `COMBO_GAIN_TAKEN` 1,0, `SPECIAL_DAMAGE` 15, `SPECIAL_RADIUS` 56, `SPECIAL_KNOCKBACK` 26, `SPECIAL_ANIM_SPEED` 1,5 (valores escolhidos, não pedidos).

### Arte
- T04: novos sprites de projétil (`proj_arrow` + variantes inclinadas `u45/u90/d45/d90`, `proj_bolt`, `proj_knife`, `proj_fireball`, `proj_rock`) gerados por `art_tools/proj_gen.py` e desenhados em camada própria (com sombra no chão).
- T06: ícones de HUD 12x12 (`icon_armor`, `icon_sword`, `icon_axe`, `icon_bow`, `icon_xbow`, `icon_knife`, `icon_staff`) gerados por `art_tools/icons_gen.py`.
- T11: novas animações do cavaleiro `attack_sword_2` (corte ascendente) e `attack_sword_3` (golpe final por cima, corpo todo à frente) e efeitos `sword_slash_2` / `sword_slash_3`; `check_edges.py` sem cortes.
- T13: novo `knight_axe_spritesheet` (cavaleiro empunhando o machado em todas as linhas: idle, run, ataque, hurt, death, pulo); ícone `icon_axe` serve de sprite do pickup.
- T12: nova animação `attack_special` (frame 0 = carga, 1–5 giro) e efeitos `spin_slash` (aro de luz) e `charge` (brasas e anel no chão).
- T14: novos `knight_bow_spritesheet` e `knight_xbow_spritesheet` (herói carregando arco / besta em todas as linhas; as linhas de tiro vêm das poses `attack_bow` / `attack_crossbow` já existentes).
- T22: `soldier_spritesheet` gerado por `art_tools/enemy_gen.py` (rig do cavaleiro com paleta inimiga via override temporário das cores do `sprite_rig`; sem tocar na saída do cavaleiro).
- T21: camada `spear` no `sprite_rig.py` (lança de duas mãos, ponta de aço e borla vermelha; `held()` e a mão livre agarram a haste), pose `atk_spear` e `spearman_spritesheet`.
- T23: `archer_spritesheet` (poses de arco como linha de ataque, arco carregado nas outras) gerado por `enemy_gen.py`.
- T24: camada `shield` no `sprite_rig.py` (`shield=True` na pose), `shieldman_spritesheet` com linha `guard` e efeito `block_spark`.
- T25: sheets `orc`, `goblin`, `kobold`, `minotaur` (recolor/escala do rig do ogro, chifres do minotauro) em `enemy_gen.py`; quadros que estourariam a moldura são reduzidos para caber.
- T33: novos props `tent`, `banner`, `palisade`, `planted_swords`, `dead_tree`, `cart`, `campfire` e tile `grass_tile` (`art_tools/theme_gen.py`).
- T32: `ogre_captain`, `minotaur_lord` e `black_knight` (quadros 96x96, escala 1,5 / 1,45 / 1,3 do rig; elmo com espinhos, chifres grandes, armadura negra com escudo).
- T34: novos props `oak`, `fern`, `log`, `mushrooms`, `stone_wall`, `bush` e tile `forest_tile` (`theme_gen.py`); parallax `treeline` e `fog` desenhados pelo `view.py`.
- T35: novos props `market_stall`, `barrels`, `lamppost` (`theme_gen.py`); parallax `skyline` e `wall` no `view.py`.
- T41: nova animação `throw` do cavaleiro (arremesso com a mão livre; a faca sai no frame 3) em todos os sheets do cavaleiro.
- T42: `ranger_spritesheet` (couros verdes, arco em todas as linhas) com `attack_bow_2`, `attack_bow_3`, `attack_short` e `attack_special` (arco para o céu) — `art_tools/class_gen.py`.
- T43: `crossbowman_spritesheet` (besta em todas as linhas) com `attack_crossbow_2`, `attack_crossbow_3`, `attack_axe_small` e `attack_special`.
- T44: camada `staff` no rig (cajado com orbe), chapéu de mago, `mage_spritesheet` (`attack_staff`, `_2`, `_3`, `attack_stomp`, `attack_special`) e efeitos `stone_spikes` e `fire_burst`.
- T50: sprite `proj_bomb` (bomba com pavio).

### Contrato de arte
- T11: `knight_spritesheet` ganha as linhas 11 (`attack_sword_2`) e 12 (`attack_sword_3`), frames de golpe 3–4; `vfx_spritesheet` ganha as linhas 6 (`sword_slash_2`) e 7 (`sword_slash_3`). Linhas anteriores inalteradas pixel a pixel.
- T13: `knight_axe_spritesheet` tem as **mesmas linhas e nomes** do `knight_spritesheet` (o jogo usa `attack_axe`); gerado por `knight_gen.py write_sheet(out, 'axe')`. `sprite_rig.py`: com o corpo deitado (`wback`) a mão livre não é reposicionada pelo machado (evitava corte na morte).
- T12: `knight_spritesheet` (e `knight_axe_spritesheet`) ganham a linha 13 `attack_special`; `vfx_spritesheet` ganha as linhas 8 (`spin_slash`) e 9 (`charge`). Estado `charge` do herói congela no frame 0 de `attack_special`.
- T14: sheets `knight_bow` e `knight_xbow` com as **mesmas linhas e nomes** do `knight_spritesheet`; `sprite_rig.render` ganha `hold=` ('sword' | 'axe' | 'bow' | 'xbow') para carregar outra arma com uma pose de corpo a corpo (`held()`).
- T22: `soldier_spritesheet` = idle(6), walk(10), attack(12), hurt(10), death(8) (contrato do ogro); golpe nos frames 3–4 reaproveita `sword_slash`.
- T21: `spearman_spritesheet` = idle(6), walk(10), attack(12), hurt(10), death(8); `render` aceita `weapon='spear'` / `hold='spear'`.
- T24: `shieldman_spritesheet` = idle(6, não usado), walk(10), attack(12), hurt(10), death(8) + `guard`(6) no final (o jogo mostra `guard` como estado parado); `vfx_spritesheet` ganha a linha 10 (`block_spark`).
- T25: quatro sheets novas no contrato do ogro (idle, walk, attack, hurt, death).
- T32: sheets de chefe com **quadros de 96x96**; o json traz `meta.frame_size`, `anchor_x` (48) e `ground_row` (90) e a View desenha por essas âncoras (os de 64x64 seguem 30 / 58). O cavaleiro negro tem `attack_2`, `attack_3` e `guard` no final.
- T41: `knight_spritesheet` (e `knight_axe/bow/xbow`) ganham a linha 14 `throw`.
- T42: sheet de classe = linhas do `knight_spritesheet` + extras; `attack_special` é substituída pela da classe.
- T44: `vfx_spritesheet` ganha as linhas 11 (`stone_spikes`) e 12 (`fire_burst`); `sprite_rig.held()` aceita `staff`.

### Áudio
- T10: pegar poção reaproveita o SFX `coin_pickup`; beber usa o `heal` existente (evento `potion`).
- T15: eventos `armor_hit`/`armor_break` usam sons provisórios (`hit_knight`/`death_ogre`) até haver SFX próprios.

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
- T11: `ATTACKS[x].next` encadeia os golpes (`sword` → `sword_2` → `sword_3`); `Fighter.combo_next/chain`. Teste 27. O mesmo sistema servirá às classes de distância (T42–T44).
- T13: `WEAPONS` (arma → ataque + sheet), `Fighter.weapon/primary/sheet`, `Pickup('weapon', ..., item)`, `ATTACKS[x].wear`; `slash=None` = o próprio sprite já tem o rastro; `load_timing` aplica as velocidades de `knight` também a `knight_axe`; a View carrega todos os `*_spritesheet.png`. Teste 28.
- T15: `apply_damage` passa a descontar da armadura (`Fighter.armor/armor_max`); `Pickup('armor')`; teste 29.
- T12: estado `charge`; `ATTACKS['special']` com `rehit` (acerta de novo no frame 4), `ignore_invuln` e alcance simétrico; `World.combo`; teste 30.
- T14: `ATTACKS[x].shoot` (dados do projétil, nasce em `slash_frame`), `Fighter.cd` + `ATTACKS[x].cooldown` (recarga), `WEAPONS` com `bow`/`xbow`; teste 31.
- T20: IA modular: `FIGHTER_DEFS[kind]['ai']` escolhe o comportamento (`_ai_melee` = o ogro atual, sem mudança) e `ai_params` sobrescreve `AI_DEFAULT` (distância de ataque, espera, descanso, revide, paciência) por tipo; `Fighter.speed` pronto para as variantes elite. Teste 32.
- T26: `World.max_attackers`, `free_tokens()`, `wait_rank()`, `spawn_enemy(kind, x, elite=)`, `ELITE_MODS`, `Fighter.mods/token`; a View multiplica a tinta (`BLEND_RGB_MULT`, em cache) e o `fake_pygame` ganhou `fill(..., special_flags)`. HUD: a barra de armadura só aparece com armadura > 0. Teste 33.
- T22: `FIGHTER_DEFS['soldier']`, `ATTACKS['soldier_sword']`, `World.focus_enemy()`; `enemy_gen.py` é o gerador de todas as sheets de inimigos (T21/T23/T24/T25). Teste 34.
- T21: IA `spear` (`_ai_spear`) com `retreat_dist` em `AI_DEFAULT`; `ATTACKS['spearman_thrust']`. Teste 35.
- T23: IA `ranged_lob` (`_ai_ranged_lob`), `ATTACKS['archer_shot']` com `shoot` do tipo `lob`. Teste 36.
- T24: `FIGHTER_DEFS[x].guard/turn_delay`, `World._face()` (virada com atraso), bloqueio dentro de `_hit` (evento `block`), IA `guard`. Teste 37.
- T25: IA `charger` (estados `charge`/`dash`), `World.roster`/`_draw_enemy()` (fluxo de sorteio próprio `spawn_rng`), constantes `ENDLESS_*`. Testes 38 e 39.
- T30: `World(stage=...)`, `_stage()`, `_spawn_encounter()`, `Game.start(stage_id)`, `TitleScene`; constantes `STAGE_END_MARGIN`, `STAGE_FINISH_DIST`, `ENCOUNTER_SPACING`; testes de cena passam a iniciar com `Game('endless')`. Teste 40 + cena 6.
- T36: `Stage.difficulty(p)`, `Stage.threat(section)`, `THREAT`, `World.queue/diff`; teste 41 verifica que a ameaça cresce entre trechos e entre fases e que nunca há mais de `max_alive` vivos. Bot ingênuo (aperta sem esquivar): fase 1 vence 1 de 3 seeds, fase 2 vence 3 de 3, fase 3 perde — a fase 3 exige esquiva, poções e especial.
- T37: `World.revive()/can_revive()/export_run()/apply_run()`, `DefeatScene`, `Game.run/run_start/start(stage, run)/to_title()`; `stats['revives']`. Teste 42 + cena 7.
- T31: `SummaryScene`, `EndScene`, `Game.after_summary()` (a loja da T50 entra aqui); cena 8.
- T33: `THEMES` (cores, parallax, chão, tabelas de props por paridade de fatia) e `PROP_PLACE` em `stages.py`; `slot_props(slot, seed, theme)` e a View montam tudo a partir do tema (o tema `village` reproduz o sorteio original); `World.theme_id`. Decoração de parallax `castle`.
- T32: `World.arena/boss/boss_dead`, `_start_arena()`, `_summon()`, IA `boss` (`boss_id`: captain / minotaur_lord / black_knight), `defn['charge']` sobrescreve os parâmetros da investida, `chain_chance` encadeia golpes de inimigos, `_drop_loot(boss=True)`; câmera de fase = base (seguir ou arena) + `cam_off` que desliza. Teste 43.
- T40: classes como dados: `CLASSES` + entradas `FIGHTER_DEFS` com `hero=True` (vida, velocidade, `jump` = multiplicador de altura, `special`, `secondary`, `label`, `voice` para o áudio); `World(hero_class=...)`; o respawn mantém a classe; eventos usam `Fighter.voice`. O cavaleiro é a entrada 0 (comportamento idêntico). Teste 44.
- T41: `FIGHTER_DEFS[x].secondary` + `ATTACKS['knife']` (`shoot`, `cooldown`), `Inputs.secondary_pressed`; teste 45.
- T42: `ATTACKS[x].burst` + `World.timers/_bursts()` (peças atrasadas de um especial), `Projectile.fall`, `Game(hero_class)` e `--class`; teste 46.
- T45: `SelectScene`; `Game.hero_class`; `FIGHTER_DEFS[x].stats/card/label/icon`; cena 6 estendida.
- T43: `ATTACKS` `xb_1..3`, `small_axe`, `bolt_volley` (rajada via `burst` do tipo `shot`); teste 47.
- T44: `Projectile.explode` + `World._explode()`, `ATTACKS[x].area` (caixa atrasada no frame do golpe), burst `rain` com `abs`; teste 48.
- T50: `ShopScene`, `Game.start_with_shop()`, `World.bombs/throw_bomb()`, `Inputs.bomb_pressed`, run state com `bombs`; cenas 8 e 9, teste 49.

### Pendente de validação
- Legibilidade dos projéteis (8–16 px) e do marcador de queda no pygame real; ainda não há ataque do jogo que dispare projéteis (entram em T14/T23/T41).
- Poses do combo vistas só em imagem estática; o feeling da janela do combo e do golpe 1 mais lento precisa de teste real.
- O soldado ainda só aparece em jogo pelo mundo montado em código/fases; entra no modo infinito junto com o elenco completo (fim da T25).
- Curva de dificuldade só medida com um bot simples; o equilíbrio real (vida, pausas dos inimigos, drop de poções) precisa de jogo humano.

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
