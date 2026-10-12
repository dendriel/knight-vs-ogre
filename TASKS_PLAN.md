# TASKS_PLAN — plano de execução das tarefas do README

> **Status (2026-10-12): executado.** T00–T50 estão implementadas e testadas (T51 ficou fora do escopo, como previsto);
> ver `CHANGELOG.md` para o que cada tarefa entregou e as escolhas feitas. D8–D10 seguiram o padrão recomendado.

Este documento transforma a seção **TODO** do `README.md` em um plano executável: corrige incoerências, ordena as
tarefas por dependência e propõe, para cada uma, o que mudar, como testar, que arte é necessária e quem executa
(Haiku/Sonnet, critério da seção 6.1 do `CLAUDE.md`). É uma **proposta**: os itens marcados **[DECISÃO]** precisam de
uma palavra do usuário (cada um traz um padrão recomendado para destravar o trabalho). **D1–D7 já foram decididas**
(seção 6) e o plano abaixo já as incorpora; restam D8–D10, com padrão recomendado.

Legenda de tamanho: **P** ≤ 1 sessão curta · **M** uma sessão · **G** várias sessões (muita arte ou refatoração).
Legenda de executor: **H** = Haiku (mecânico, segue molde) · **S** = Sonnet (fino, toca contrato/arquitetura).

---

## 1. Incoerências e lacunas encontradas no TODO

| # | Problema | Correção proposta |
|---|---|---|
| I1 | **Fases duplicadas**: "Fases: um percurso…" e "Criar 3 fases…" são o mesmo item; o texto mistura *fase*, *cenário* e *tela*. | Um item só. Vocabulário fixo: **fase** (percurso com tema), **cenário** (arte do tema), **tela** (UI: seleção, conclusão, loja). |
| I2 | **Jogo infinito × fases**: hoje o ogro renasce sem fim e o herói renasce na esquerda (`logic.py:279`, `_respawns`); o mundo é infinito (`slot_props`). Fase com início, fim e boss não combina com isso. | Fase = lista de **encontros** com gatilho por posição, comprimento finito e câmera travada nas pontas. O modo infinito atual **continua** como fase especial `endless` (serve de laboratório e dos testes). Morte do herói numa fase: **tela de derrota** com *Renascer aqui (100 ouro)* ou *Reiniciar a fase* (D1, T37). |
| I3 | **Conflito de entrada no botão de ataque**: hoje *segurar* repete o ataque (`logic.py:160`); o combo pede *clicar de novo*; o especial pede *segurar*. Além disso o **ataque secundário não tem tecla**. | Regras (ver T05/T11/T12): *toque* = golpe/encadeia combo na janela; *segurar sem barra cheia* = repete o golpe 1 (como hoje); *segurar com barra cheia* ≥ 0,25 s = carrega e **solta = especial**; **botão direito = ataque secundário**. |
| I4 | **"Arremessar faca"** é secundário do cavaleiro, mas a loja lista "arremessáveis" (munição) e nada diz se há estoque. | **Decidido (D3):** ataques primário e secundário são **infinitos** (limitados só por *cooldown*); só gastam-se itens comprados/coletados com mecânica de desgaste (poção, durabilidade de arma, armadura). Logo a faca da classe é infinita, e os "arremessáveis" da loja passam a ser **consumíveis à parte** (D8). |
| I5 | **Arma de classe × arma pickup**: o arqueiro "tem arco" e o cavaleiro "pega arco com durabilidade". Não está dito se a arma de classe quebra, nem se um mago pode pegar um machado. | Arma de **classe é indestrutível**; **pickup** tem durabilidade e **substitui só o primário do cavaleiro** (único com sheet completo). Outras classes só recebem pickups quando houver arte. |
| I6 | **Poções**: hoje são consumidas ao pegar e ficam no chão com vida cheia (`logic.py:261`). O TODO quer inventário (até 10, tecla 1). | O comportamento atual **é substituído**: pegar sempre guarda (até 10; com 10 a poção fica no chão); tecla 1 consome. Atualizar "Regras" do README. |
| I7 | **Dano único**: `DAMAGE = 10` vale para todos (`logic.py:218`). Machado "mais forte", boss, flecha e especial exigem dano por ataque; a barra de combo ("X de dano") precisa de unidade. | Dano passa a pertencer ao **ataque** (T03). Barra de combo em pontos de dano reais (`COMBO_BAR_MAX`, ex.: 100 = 10 golpes causados/recebidos). |
| I8 | **Escudo "ou com o especial"**: não há regra de guarda. | Guarda bloqueia golpes **de frente** (sem dano, recuo curto); o inimigo vira para o herói com atraso (`SHIELD_TURN_DELAY`), então dá para passar por trás (os personagens se atravessam). **Especial e machado pesado ignoram guarda.** |
| I9 | **Inimigos × fases × bosses**: "goblin, minotauro, kobold, orc" e "humanos" não têm mapeamento para as 3 fases, e **os bosses não estão definidos**. | Proposta na seção 4 (tabela fase → inimigos → boss). **[DECISÃO D5]** |
| I10 | **Dois tipos de projétil sem nome**: o do herói (reto) e o dos monstros (parábola no céu). "Mira" não faz sentido em visão lateral. | T04 define `straight` (herói; mira = direção que ele encara, acerta o 1º alvo na faixa vertical) e `lob` (inimigo; parábola com **marcador de queda** no chão, dá tempo de desviar). |
| I11 | **"Segunda tela: loja… para a próxima partida"**: "partida" é ambíguo; não diz onde o ouro persiste. | Fluxo: *Seleção → Fase → Conclusão → Loja → Fase seguinte*. Ouro e itens valem na **run** e passam de fase em fase (D6); não há arquivo de save. |
| I12 | **Arte multiplicada**: "todas as animações base para cada arma" × 4 classes × combo × especial explode. | O gerador já recebe `weapon=` por pose (`knight_gen.py`: `dict(weapon='sword', …)`) e já tem `axe`, `bow`, `xbow` (`render`). Variantes por arma = **parametrizar o gerador**, não redesenhar (T13). Itens **(arte)** viram subtarefas de cada feature. |
| I13 | **Combo para classes à distância**: o TODO diz "ataque primário", mas arco/besta/cajado não têm "golpe encadeado". | **Decidido (D4):** vale para todas as classes. Encadeamento vira dado (`ATTACKS[x].next`), então o mesmo sistema (T11) serve às quatro classes; cada classe traz suas 2 animações extras. Para distância: 1º tiro mais lento (mira), 2º e 3º mais rápidos; o 3º é o "tiro forte" (flecha perfurante / virote que atravessa / bola de fogo maior). Armas **pickup** não encadeiam na v1 (sem arte de combo por arma): trocam o combo por mais dano. |
| I14 | **Tela de seleção com 1 classe** não faz sentido; precisa de retrato por classe. | Só entra quando houver ≥ 2 classes (T45); retrato = frame `idle` ampliado 3×, sem arte nova. |
| I15 | **Armas do cavaleiro já existem** (`attack_axe`, `attack_bow`, `attack_crossbow` no sheet — CLAUDE.md §5), mas o README sugere redesenhar tudo. | T13/T14 reaproveitam essas linhas; o trabalho de arte restante é *segurar a arma nas outras animações* e os projéteis. |

---

## 2. Limitações da base atual (o que precisa mudar antes das features)

- `World` tem **um herói e um ogro** (`self.hero`, `self.ogre`, `fighters()` → tupla de 2; `_attacks` só cruza os dois;
  `ai_wait`/`ai_cooldown` são do mundo, não do inimigo).
- Parâmetros espalhados por tipo: `ANIM`, `SLASH`, `REACH` (`logic.py:5-9`), `HALF_WIDTH`, `DAMAGE`, `OGRE_*`.
- Só existe **um** ataque por lutador (estado `attack`); não há id de ataque, combo, arma equipada nem cooldowns.
- **Sem projéteis, sem dano em área, sem inventário/equipamento, sem cenas** (o `main.py` vai direto para o combate).
- Entrada só lê botão esquerdo (`main.py:34`) e `fake_pygame.py` não simula botão direito/teclas numéricas.
- Cenário gerado por `slot_props` com um único tema; parallax e chão fixos no `view.py`.

---

## 3. Visão geral e ordem

```
F0 Fundações ─┬─ T01 dados por lutador ── T02 vários inimigos ── T03 ataques como dados ── T04 projéteis/área
              ├─ T05 entrada + cenas ───── T06 HUD em slots
              │
F1 Cavaleiro ─┼─ T10 poções (inventário)      [T05,T06]
              ├─ T11 combo 3 golpes           [T03]
              ├─ T12 barra de combo + especial [T03,T06,T11]
              ├─ T13 machado pickup + durabilidade [T03,T06]
              ├─ T14 arco/besta pickups       [T04,T13]
              └─ T15 armadura                 [T01,T06]
              │
F2 Inimigos ──┼─ T20 IA modular ─ T26 fichas de ataque + elites ─ T22 soldado ─ T21 lanceiro ─ T23 arqueiro(lob)
              │                                                              [T04]      ─ T24 escudeiro ─ T25 monstros
F3 Fases ─────┼─ T30 sistema de fases [T02] ─ T36 curva de dificuldade/encontros [T26] ─ T37 derrota (renascer/reiniciar)
              │      ─ T31 conclusão [T05] ─ T32 boss/arena [T20] ─ T33/T34/T35 temas
              │
F4 Classes ───┼─ T40 classes [T01,T03] ─ T41 secundário [T04,T05] ─ T42 arqueiro ─ T43 besteiro ─ T44 mago ─ T45 seleção
              │
F5 Economia ──└─ T50 loja + fluxo da run [T31,T10,T13,T15,T37] ─ (consumíveis arremessáveis, D8)
```

**Ordem recomendada** (cada marco deixa o jogo jogável e testado):

1. **F0** inteira (sem mudança visível; é o que destrava todo o resto).
2. **F1** na ordem T10 → T11 → T13 → T15 → T12 → T14 (itens baratos primeiro; especial depois de combo e HUD prontos).
3. **F2** T20 → T26 → T22 → T21 → T23 → T24 (variedade de combate com o que já existe), T25 por último (arte nova).
   A ordem de construção casa com a ordem de **introdução** dos inimigos nas fases (seção 4): soldado e lanceiro e
   arqueiro já fecham a fase 1; escudeiro e goblin/kobold, a fase 2; orc e minotauro, a fase 3.
4. **F3** T30 → T36 → T37 → T31 → T33 → T32 → T34 → T35. Começa pelo sistema + tema com **arte já existente**
   (vila/cidade) para validar o pipeline, depois os temas novos. Ordem de *jogo* continua planície → floresta → cidade.
   Cada tema só fecha quando os inimigos que ele usa existirem (até lá, usa o que já foi construído).
5. **F4** classes (T40 → T41 → T42 → T45 → T43 → T44): o arqueiro vem primeiro porque reaproveita as linhas de arco
   que o cavaleiro já tem; a tela de seleção entra assim que houver 2 classes.
6. **F5** loja por último, porque vende o que as fases anteriores criaram (poções, armas, armadura, facas).

Alternativa (se o foco for variedade de personagem antes de conteúdo de fase): trocar F3 e F4. A única dependência
real entre eles é T41/T50; T30–T35 não dependem de classes.

---

## 4. Conteúdo e curva de dificuldade (D5)

### 4.1 Princípios

- **Dificuldade cresce entre fases e dentro de cada fase.** Toda fase é dividida em três trechos por progresso
  (`p` = x do herói / comprimento): **abertura** (0–35%), **meio** (35–75%) e **pré-boss** (75–100%). Cada trecho é mais
  denso e mais perigoso que o anterior; a fase seguinte *reabre* num patamar um pouco acima do pré-boss da anterior.
- **Vários inimigos ao mesmo tempo** (`MAX_ALIVE` sobe por fase e por trecho). Para continuar justo, só alguns podem
  atacar juntos: **fichas de ataque** (`MAX_ATTACKERS`, T26) — os demais cercam/esperam (e arqueiros atiram de longe).
- **Inimigos mais rápidos e desafiadores**: variantes *elite* por modificadores de ficha (velocidade, vida, espera
  antes do golpe, cooldown, tinta de cor), sem arte nova: **veterano** (+25% vel., −30% espera), **bruto** (+60% vida,
  golpe tira 15), **ágil** (+40% vel., −30% vida). A fração de elites cresce com `p` e com a fase.
- **Composição, não só quantidade**: o pré-boss mistura papéis (escudeiro na frente + arqueiros atrás; lanceiro
  segurando o herói enquanto goblins cercam), forçando uso de pulo/caixas, especial e armas pickup.
- **Tudo em dados** (T36): tabela de encontros por fase e curva em `config.py`; testes verificam monotonicidade.

### 4.2 Roteiro por fase

| Fase | Tema | Elenco (introdução) | `MAX_ALIVE` / `MAX_ATTACKERS` por trecho | Boss |
|---|---|---|---|---|
| 1 | Planície (fácil) | **soldado** e **ogro** 1×1 → **lanceiro** a partir do meio → **arqueiro** (lob) no pré-boss; 1 elite veterano no fim | 2/1 → 3/2 → 3/2 | **Ogro-capitão**: ogro grande, 3× vida, golpe em área; chama 2 soldados na metade da vida |
| 2 | Floresta inglesa (média) | **goblins** (rápidos, frágeis, em bando) e **kobolds** (lob) → **escudeiro** (primeiro) → arqueiros; elites ágeis | 3/2 → 4/2 → 5/3 | **Minotauro**: investida em linha (telegrafada) + machado; rápido |
| 3 | Cidade (difícil) | **escudeiros** + **lanceiros** + **orcs** (ogro recolor) em formação, arqueiros em dupla, **minotauro** como mini-boss no meio; muitos elites | 4/2 → 5/3 → 6/3 | **Cavaleiro Negro**: combo próprio de 3 golpes + guarda + invoca arqueiros |

Exemplo (fase 1, abertura → pré-boss), escrito como dado: `(p=.10, [soldier])`, `(p=.25, [ogre])`,
`(p=.45, [soldier, ogre])`, `(p=.60, [spearman, soldier])`, `(p=.80, [archer, spearman, ogre])`,
`(p=.92, [veteran_soldier, spearman, archer])`, `(p=1.0, boss)`.

### 4.3 Efeitos nos outros sistemas

- Com vários inimigos, **knockback/invulnerabilidade** continuam por lutador; o herói não pode ser "encurralado":
  enquanto `invuln` > 0 ninguém o acerta (já existe) e o encontro respeita `MAX_ATTACKERS`.
- A curva também escala o **loot** (mais ouro nos trechos finais) para a loja (T50) acompanhar a dificuldade.

Props por tema: **planície** — tendas, estandartes, paliçadas, armas fincadas, árvore seca, carroça; **floresta** —
carvalhos densos, samambaias, troncos caídos, cogumelos, muro de pedra, névoa no parallax; **cidade** — casas
(existentes), barracas de mercado, barris, postes, muralha ao fundo, rua de pedra.

---

## 5. Tarefas

Formato: **depende de** · **mudanças** · **testes** · **arte** · **executor / tamanho** · **pronto quando**.
Toda tarefa inclui, no mesmo commit: `CHANGELOG.md` (CLAUDE.md §6.2), README (controles/regras) e, se tocar o contrato
de arte, CLAUDE.md §5 + `meta` do `.json`. Linhas novas de sheet **só no final**.

### F0 — Fundações (sem mudança visível)

**T00 · Limpar o TODO do README** — H/P
Aplicar a tabela da seção 1 (unir fases, vocabulário, itens **(arte)** dentro de cada feature) e apontar para este
arquivo. *Pronto:* README sem itens duplicados/contraditórios.

**T01 · Dados por tipo de lutador** — S/M · depende de: —
- Em `config.py`/`logic.py`: tabela `FIGHTER_DEFS[kind]` com `max_hp, speed, half_width, anim_map, slash_vfx, reach,
  drops, ai`. Remover `ANIM/SLASH/REACH/HALF_WIDTH/DAMAGE` soltos e `OGRE_*` duplicados (manter nomes públicos como
  alias enquanto os testes migram).
- Funnel único de dano: `World.apply_damage(atk, tgt, amount)` (armadura, guarda, combo e estatísticas entram aqui).
- Contadores de estatística: `stats = {kills, damage_dealt, damage_taken, gold_gained}` (já alimenta T12 e T31).
- *Testes:* suíte atual passa **sem mudar asserts**; novo teste de `apply_damage`.
- *Pronto quando:* comportamento idêntico (rodar `test_logic.py` e `simulate.py`, comparar GIF).

**T02 · Vários inimigos** — S/G · depende de: T01
- `World.enemies` (lista); `ogre` vira *property* de compatibilidade (primeiro inimigo vivo) até migrar os testes.
- Estado de IA (`ai_wait`, `ai_cooldown`) para dentro de `Fighter`.
- `_attacks` generalizado: cada atacante contra **todos** os alvos válidos (hero ↔ enemies); respawn do ogro vira um
  *spawner* (`Spawner` simples: alvo de vivos simultâneos + atraso) — comportamento atual = 1 vivo, `RESPAWN_DELAY`.
- Câmera continua seguindo o herói; corpos continuam em `corpses` (limite 40).
- *Testes:* 2–3 ogros simultâneos; ordem determinística (semente); loot por inimigo morto; troca de golpes preservada.
- *Pronto quando:* `test_logic.py` migrado + novo teste "3 ogros".

**T03 · Ataques como dados** — S/G · depende de: T01
- `ATTACKS[id]`: `anim, active_frames, reach, damage, anim_speed, slash_vfx, move_factor, knockback, guard_break,
  cooldown, cost_durability`. `Fighter.attack_id` e `Fighter.weapon`.
- `_hero_control` passa a escolher `attack_id` (hoje implícito); `_attacks` lê do registro.
- Mantém o ataque de espada/machado do ogro como duas entradas — **sem mudar números**.
- *Testes:* ataque do herói/ogro idêntico; dano por ataque; vfx sincronizado (frame 3).
- *Pronto quando:* adicionar um ataque novo = 1 entrada de dados + 1 linha de sheet.

**T04 · Projéteis e dano em área** — S/G · depende de: T01, T03
- `Projectile`: `kind` (`straight` | `lob`), posição/velocidade, dono, dano, vida útil, alvo-faixa vertical, `pierce`.
  `straight`: o herói dispara na direção que encara; acerta o 1º alvo na faixa `VERTICAL_REACH`. `lob`: parábola com
  gravidade, alvo = x do herói no disparo; desenha **marcador de queda** no chão; dano ao cair se o alvo estiver na
  zona.
- `AreaHit`: retângulo/raio com atraso e duração, multi-alvo (espinhos do mago, especiais, boss).
- `view.py`: camada de projéteis entre lutadores e efeitos; sombra do projétil no chão.
- *Arte:* sprites `arrow`, `bolt`, `knife`, `fireball`, `rock_lob` (pequenos, 8–16 px) → `scenery_gen.py` ou novo
  `proj_gen.py`; **H** pode gerar (molde: `potion.png`).
- *Testes:* trajetória determinística; desvio (herói sai da zona); acerto em alvo no ar/caixa; projétil some fora da tela.

**T05 · Entrada ampliada e cenas** — S/M · depende de: —
- `Inputs`: `attack` (nível), `attack_pressed` (borda), `attack_held_t`, `secondary_pressed`, `potion_pressed`
  (tecla 1), `confirm`/`pause`. Borda calculada em `main.py` (como `_jump_held` hoje).
- `Scene` mínima em `main.py`: `PlayScene` (o jogo atual), `PauseScene` (D7: **Esc abre o menu** *Continuar · Ver comandos ·
  Reiniciar fase · Sair*; navegação por ↑/↓ + Enter e por clique; Esc de novo continua; o mundo e o tempo ficam
  congelados), ganchos para `SelectScene`, `SummaryScene`, `DefeatScene`, `ShopScene` (placeholders).
- *Ver comandos*: tela alimentada por **uma única tabela** `CONTROLS` em `config.py` (tecla/botão → ação), que também
  vale de fonte para o README. *Reiniciar fase*: restaura o snapshot do início da fase (D9) e recomeça; enquanto
  não há fases, reinicia o `World`. *Sair*: fecha o jogo; Esc deixa de fechar a janela.
- UI por clique: botão/card genérico com *hover* (usado por T45/T31/T50).
- `tests/fake_pygame.py`: botão direito, teclas numéricas e eventos de clique.
- *Pronto quando:* jogo idêntico em `PlayScene`; teste de borda/segurar no `simulate.py`.

**T06 · HUD em slots** — S/M · depende de: T05
- Reorganizar `view.py` HUD (480×270 é pouco espaço): vida · armadura · arma + durabilidade · poções `n/10` · barra
  de combo · ouro · contadores, em posições nomeadas de `config.py`. Cada slot só aparece se a feature existir.
- *Arte:* ícones 12–16 px (poção já existe; armadura, arma, barra, faca) — **H** (molde `coin.png`).
- *Pronto quando:* HUD atual intacto; slots vazios não aparecem.

### F1 — Cavaleiro: combate mais rico

**T10 · Poções em inventário** — H/P · depende de: T05, T06 (corrige I6)
- `World.potions` (0–10); `_pickups`: poção sempre vai ao inventário; com 10 fica no chão. Tecla **1** → `drink_potion()`
  (usa `World.heal`, só se vida < máx.; evento `('potion', ...)`).
- *Testes:* limite 10; consumo cura 30 e respeita máximo; não consome com vida cheia; sobrevive à morte do herói.
- *Constantes:* `POTION_MAX_STOCK = 10`, `POTION_HEAL` (existente).

**T11 · Combo de 3 golpes** — S/M · depende de: T03 (resolve parte de I3/I13)
- **Sistema único para todas as classes (D4):** cada ataque de dados traz `next` e `chain_speed`; o combo é só uma
  cadeia `ATTACKS[a].next → b → c`. Aqui se implementa e se testa com a espada; arqueiro/besteiro/mago só preenchem
  tabelas (T42–T44). Pickups sem cadeia (ver I13).
- Estados/ataques `sword_1`, `sword_2`, `sword_3`. Clique durante a janela do ataque atual (a partir do frame
  `COMBO_WINDOW_START` até o fim + `COMBO_BUFFER` ~0,15 s) encadeia o próximo; depois do 3º volta ao 1º.
- Balanceamento (proposta): golpe 1 **mais lento** (`KNIGHT_ATTACK_ANIM_SPEED` 2.0 → 1.7) e os encadeados mais rápidos
  (2.4 e 2.6); dano 10/10/15 (o 3º com `knockback` maior). Como `ANIM_SPEED` é por linha do sheet, cada golpe tem sua
  linha e seu efeito (`slash`) **na mesma velocidade** (regra do `config.py`).
- *Arte (contrato):* `knight_spritesheet` ganha `attack_sword_2`, `attack_sword_3` (+ 2 linhas de efeito no
  `vfx_spritesheet`); frames de golpe 3–4. Regenerar rastros (CLAUDE.md §5). **S** (poses/IK).
- *Testes:* encadeia na janela; fora da janela não encadeia; 3 golpes máx.; hurt cancela a cadeia; segurar sem soltar
  repete só o golpe 1.

**T13 · Machado pickup + durabilidade** — S/G · depende de: T03, T06 (não precisa de projéteis)
- `Pickup('weapon', 'axe', durability=100)`; ogro dropa o próprio machado (chance `AXE_DROP_CHANCE`, ex. 0,15).
  `World.weapon` do herói; durabilidade `100 → 0`, gasto por golpe (`AXE_WEAR` ≈ 3%); ao zerar → *quebra*
  (evento + vfx + volta à espada).
- Efeito próprio (I7): machado = dano 20, alcance +8, golpe 1,35× mais lento (`ATTACKS['axe']`); ignora guarda (I8).
- *Arte:* parametrizar `knight_gen.py` com `weapon=` para gerar `knight_axe_spritesheet` (idle, run, ataque, hurt,
  death, jump_up, jump_fall) reaproveitando poses e `attack_axe`; ícone de arma. **S**. Registrar no contrato (§5).
- *Testes:* pegar troca arma; desgaste; quebra volta à espada; morte **sem** renascer pago (reinício) restaura a arma do snapshot; renascer pago mantém a
  arma (D10); HUD mostra durabilidade.

**T15 · Armadura** — H→S/P · depende de: T01 (`apply_damage`), T06
- `hero.armor` (0–`ARMOR_MAX`); `apply_damage` desconta da armadura primeiro; ao zerar → quebra (evento/SFX) e o dano
  volta à vida. Fonte inicial: pickup raro (`ARMOR_DROP_CHANCE`) até a loja existir.
- *Arte:* ícone + barra azul no HUD; variação visual do herói é opcional (adiar).
- *Testes:* ordem de desconto, sobra de dano ao quebrar, `hurt` ainda toca com armadura.

**T12 · Barra de combo + ataque especial do cavaleiro** — S/G · depende de: T03, T06, T11
- `combo_meter` (0–`COMBO_BAR_MAX`): ganha `COMBO_GAIN_DEALT × dano causado` e `COMBO_GAIN_TAKEN × dano recebido`
  (via `apply_damage`, T01). Cheia → HUD pisca.
- Entrada (I3): `attack_held_t ≥ SPECIAL_HOLD_MIN` com barra cheia entra em **carga** (herói parado/lento, brilho); soltar
  dispara `ATTACKS['special']`; soltar antes do mínimo = golpe normal. Barra zera ao disparar.
- Especial do cavaleiro (proposta): **golpe giratório** 360° (`AreaHit`, T04), 2 hits, ignora guarda, invulnerável
  durante a animação.
- *Arte:* `attack_special` (+ efeito `spin_slash`, +carga) — linhas novas no final dos sheets. **S**.
- *Testes:* carga/ganho de barra, soltar cedo, zera ao usar, **zera na morte** (D2: também no renascimento pago), não carrega em `hurt`/`dead`.

**T14 · Arco e besta como pickup** — S/M · depende de: T04, T13
- Reaproveita `attack_bow`/`attack_crossbow` (a flecha só aparece no frame 4 → projétil nasce nesse frame).
  Arco: dano 10, cadência normal; besta: dano 20, recarga lenta (`XBOW_RELOAD`), mais alcance. Durabilidade como o machado.
- *Arte:* projéteis (T04) + `knight_bow/xbow_spritesheet` pela parametrização de T13.
- *Testes:* projétil nasce no frame 4; consome durabilidade por disparo; alcance máximo; recarga.

### F2 — Inimigos

**T20 · IA modular** — S/M · depende de: T02, T03
- Extrair `_ogre_ai` para comportamentos plugáveis por `FIGHTER_DEFS[kind].ai`: `melee` (atual), `spear` (distância de
  parada maior), `ranged_lob` (mantém distância, dispara), `guard` (T24), `boss` (T32). Parâmetros por tipo, mesma
  semente determinística.
- *Pronto quando:* ogro idêntico ao atual com `ai='melee'`.

**T26 · Fichas de ataque e variantes elite** — S/M · depende de: T20 (D5)
- **Fichas de ataque**: `World.attack_tokens` (`MAX_ATTACKERS`); um inimigo só inicia o golpe se obtém uma ficha
  (devolvida ao fim do golpe/hurt/morte). Quem não tem ficha cerca/espera a distância `OGRE_ATTACK_DIST + n·8`, sem
  parar de encarar o herói. Mantém a janela de reação (`WAIT_BEFORE_ATTACK`) mesmo com muitos inimigos.
- **Elites** por modificadores aplicados à ficha do tipo (`ELITE_MODS['veteran'|'brute'|'agile']`: velocidade, vida,
  dano, espera, cooldown) + tinta de cor no `view.py`; sem arte nova. Rótulo no HUD opcional.
- *Testes:* nunca mais de `MAX_ATTACKERS` atacando; ficha liberada ao morrer; elite mais rápido/vida conforme mod;
  com 1 inimigo o comportamento é idêntico ao atual.

**T22 · Cavaleiro inimigo** — H/M · depende de: T20
- Reuso do rig do herói (`knight_gen.py`) com paleta inimiga (`ENEMY_PAL`), espada, mesmas poses → sheet
  `soldier_spritesheet` (mesmas linhas do ogro: idle, walk, attack, hurt, death). Vida 20, dano 10, mais rápido que o
  ogro, espera menor.
- Delegar ao Haiku: *recolor + mapear as linhas* (molde `ogre_gen.py`/`knight_gen.py`); verificação:
  `build_assets.py --check`, `check_edges.py`.

**T21 · Lanceiro** — S/M · depende de: T22
- Camada `spear` em `sprite_rig.py` (arma nova → **S**); alcance `(−12, 62)`, ataque lento (investida curta); fica
  exposto se o herói entra na distância "morta" muito perto (`spear_min_dist`) — dá ao jogador uma resposta.
- *Testes:* acerta a 55 px onde o ogro não acerta; não acerta herói colado (zona morta).

**T23 · Arqueiro inimigo (lob)** — S/M · depende de: T04, T20, T22
- `ranged_lob`: mantém ~`ARCHER_KEEP_DIST`, dispara a cada `ARCHER_COOLDOWN`, flecha em parábola com marcador (I10).
- *Arte:* linha `attack_bow` no sheet do soldado (reaproveita `atk_bow`). *Testes:* desvio, marcador, recuo do arqueiro.

**T24 · Cavaleiro com escudo** — S/M · depende de: T20, T22
- Guarda de frente conforme I8: golpe frontal = `blocked` (sem dano, `('block', kind)` + faísca + recuo curto);
  atacante por trás ou `guard_break` acerta normal; vira com atraso `SHIELD_TURN_DELAY` (~0,5 s).
- *Arte:* camada `shield` + pose `guard` (linha nova) + efeito `block_spark` (vfx, linha nova). **S**.
- *Testes:* bloqueia frontal; por trás acerta; machado/especial atravessa; vira depois do atraso.

**T25 · Monstros fantasia (goblin, kobold, minotauro, orc)** — H (recolors) / S (silhuetas) / G · depende de: T20, T23
- Orc = ogro recolor/escala (**H**); goblin/kobold = pequenos, rápidos, versão `lob` com pedra (**S**: proporções no
  rig); minotauro = cabeça nova + investida (**S**). Cada um: 1 sheet (5 linhas do contrato) + linha em `FIGHTER_DEFS`.
- Fazer **um por vez**, validar GIF antes do próximo.

### F3 — Fases e progressão

**T30 · Sistema de fases** — S/G · depende de: T02 (I1/I2)
- `game/stages.py`: `Stage(id, theme, length, encounters=[(x_trigger, [enemy…], wave_rules)], boss)`; dados, sem
  lógica. `World(stage=…)`: progresso em x, **câmera limitada** a `[0, length]`, herói não passa do início, encontro
  dispara ao cruzar `x_trigger`, fase só termina com todos os encontros limpos + cruzar a linha final.
- Tema vira dado (`THEMES[id]`: props por slot, tile de chão, camadas de parallax, música) — tira o hardcode do
  `view.py`.
- Morte do herói numa fase **não** renasce sozinha: congela o mundo e abre a tela de derrota (T37, D1). O renascimento
  automático e gratuito do jogo atual fica **só** no modo `endless`.
- Modo `endless` = comportamento atual (tema `village`).
- *Testes:* encontro dispara 1×; câmera trava nas pontas; fim de fase só com tudo limpo; morte em fase → estado
  `defeated` (sem respawn automático); `endless` continua renascendo.

**T36 · Encontros e curva de dificuldade** — S/M · depende de: T30, T26 (D5)
- `stages.py`: encontros declarados com `p` (progresso 0–1) + lista de `(tipo, variante)`; `difficulty(stage, p)` →
  `MAX_ALIVE`, `MAX_ATTACKERS`, fração de elites, multiplicador de loot (seção 4). Spawn por gatilho + *reposição*
  (quando vivos < `MAX_ALIVE` e há "orçamento" no trecho, entra o próximo da fila pela borda).
- Tabela de ameaça por tipo (`THREAT[kind]`) para validar encontros: soma por trecho deve **crescer** (teste).
- *Testes:* monotonicidade entre trechos e entre fases; nunca > `MAX_ALIVE`; determinismo com a semente; elites só a
  partir de `p` configurado.

**T37 · Tela de derrota: renascer ou reiniciar** — S/M · depende de: T30, T05 (D1, D9, D10)
- `DefeatScene` (sobre o mundo congelado, com a animação de morte terminada): **"Renascer aqui — 100 ouro"**
  (`REVIVE_COST = 100`; desabilitado e com aviso se `gold < 100`) e **"Reiniciar a fase"**.
- *Renascer:* mesmo x do mapa, vida cheia, `REVIVE_INVULN` = 2 s, barra de combo zerada (D2); inimigos/boss e
  encontros mantêm o estado; ouro −100; `stats.revives += 1`.
- *Reiniciar:* restaura o snapshot do início da fase (D9) e recomeça a fase (passando pela loja quando T50 existir).
- *Testes:* sem ouro suficiente não renasce; renasce no mesmo x; ouro desconta exatamente 100; reiniciar restaura
  ouro/itens do início; encontros reiniciam.

**T31 · Tela de conclusão** — S/M · depende de: T30, T05, T01 (stats)
- `SummaryScene`: monstros mortos, dano causado, ouro adquirido (+ mortes e tempo), botão "Continuar".
- *Testes:* números batem com `world.stats`; ouro da fase ≠ ouro total.

**T33 · Tema 1 — planície** — S/G · depende de: T30
- Arte nova em `scenery_gen.py` (props da seção 4), tile de chão de grama/terra, parallax (céu, colinas, castelo
  distante, fumaça). Props simples (barril/estandarte) → **H**; composição/parallax → **S**.
- Tabela de encontros da fase 1 (seção 4). *Pronto quando:* `build_assets.py --check` e GIF da fase.

**T32 · Boss + arena** — S/G · depende de: T30, T20
- Evento `arena_start` perto do fim: câmera trava (`world.arena = (x0, x1)`), herói não sai, inimigos comuns param de
  surgir; ao morrer o boss: libera a câmera e exibe seta "→". HUD com barra de vida do boss.
- Boss como `FIGHTER_DEFS` com ataques próprios (T03) e `ai='boss'`; **um boss por fase** (seção 4).
- *Arte:* sprite de cada boss (G; **S**) — fazer o boss da fase 1 junto com T33 e os outros com T34/T35.

**T34 · Tema 2 — floresta inglesa** e **T35 · Tema 3 — cidade** — S/G · depende de: T30
- Igual a T33 (props e parallax da seção 4). A cidade reaproveita `medieval_house`, `well`, `street_tile`; a floresta
  reaproveita `tree` em densidade maior + variações novas.

### F4 — Classes

**T40 · Generalizar o herói em classes** — S/M · depende de: T01, T03
- `CLASSES[id]`: `max_hp, speed, jump, sheet, primary, secondary, special, reach/damage`. `World(hero_class=…)`;
  `Fighter.kind` do herói deixa de ser fixo `'knight'`. Cavaleiro = entrada 0 (sem mudança de comportamento).
- *Arte (contrato):* cada classe é um sheet com a **mesma ordem de linhas** do cavaleiro (idle, walk, run, ataque
  primário, ataque secundário, hurt, death, jump_up, jump_fall, [+ especial]).

**T41 · Ataque secundário (botão direito)** — S/M · depende de: T04, T05, T40
- `secondary_pressed` → `ATTACKS[class.secondary]` com `cooldown`. Cavaleiro: **faca arremessada**, infinita e
  limitada só pelo `cooldown` (D3; sem contador no HUD, só indicador de recarga); reaproveita a linha de ataque
  curto (nova linha `throw` no sheet).
- *Testes:* cooldown, projétil `straight` com dano, não dispara em `hurt`/`dead`, funciona com vida em qualquer valor.

**T42 · Arqueiro** — S/G · depende de: T40, T41, T04
- Primário: arco (projétil T04, reaproveita `attack_bow`); secundário: espada curta (`attack_short`); especial: chuva
  de flechas (`AreaHit` + projéteis). Atributos: vida menor, velocidade maior.
- **Combo (D4):** `bow_1` (mira, mais lento) → `bow_2` → `bow_3` (flecha perfurante, `pierce`); as duas linhas novas
  só mudam a pose/cadência (puxar mais curto), então o custo de arte é pequeno.
- Arte: sheet completo do arqueiro (gerador por `weapon='bow'` + paleta). **S**.

**T45 · Tela de seleção de classe** — S/M · depende de: T05, T40, ≥2 classes (após T42)
- `SelectScene`: cards lado a lado (retrato = `idle` ampliado, nome, barras de vida/vel./dano/alcance, primário/
  secundário/especial em texto), clique escolhe → `PlayScene`. Teclas ←/→ + Enter também (acessibilidade).

**T43 · Besteiro** — S/G · depende de: T42 · primário besta (recarga lenta), secundário machado pequeno, especial rajada
de virotes. Combo (D4): `xbow_1` (recarga/mira) → `xbow_2` → `xbow_3` (virote que atravessa inimigos em linha).
**S** (sheet com `weapon='xbow'`).

**T44 · Mago** — S/G · depende de: T42, T04 (AoE) · cajado + bola de fogo (`straight`), secundário **espinhos de
pedra** (`AreaHit` à frente, atraso curto, multi-alvo), especial tempestade de fogo. Combo (D4): `staff_1` → `staff_2` → `staff_3` (bola de fogo
maior, com explosão em área pequena). Exige camada `staff` no rig e sprites de bola de fogo/espinhos (**S**).

### F5 — Economia

**T50 · Loja e fluxo da run** — S/G · depende de: T31, T37, T10, T13, T15 (I11, D1, D6, D9)
- `RunState` (ouro, estoque de poções, armadura, arma, consumíveis) que atravessa as fases (D6) e guarda um
  **snapshot do início da fase** (D9). `ShopScene`: poções, armadura, arma pickup (machado/arco/besta), consumíveis
  arremessáveis (D8, depois). Preço em `SHOP_PRICES` (`config.py`).
- Fluxo: `Seleção → Fase 1 → Conclusão → Loja → Fase 2 → … → Fim`. Derrota → *Reiniciar* (ou "Reiniciar fase" do Esc)
  → restaura o snapshot → **Loja** → mesma fase. Tela final simples ("Fim da demo").
- Enquanto a loja não existe (T37 já entrega o reinício), "Reiniciar" vai direto para a fase.
- *Testes:* compra desconta ouro, limite de estoque, item comprado entra equipado na fase; reinício restaura o
  snapshot; ouro ganho na tentativa perdida não vaza para a nova.

**T51 · Persistência em arquivo** — fora do escopo (D6). Só reabrir se pedirem salvar entre execuções.

---

## 6. Decisões

### 6.1 Decididas

| ID | Decisão | Onde entra |
|---|---|---|
| D1 | Ao morrer numa fase o jogador escolhe: **gastar 100 de ouro para renascer no mesmo ponto** do mapa, ou **reiniciar a fase** (podendo comprar itens na loja de novo para a nova tentativa). Sem ouro suficiente, só "reiniciar". | T37, T50 |
| D2 | A barra de combo **zera na morte**. | T12 |
| D3 | Ataques **primário e secundário são infinitos** (só *cooldown*). Gastam-se apenas itens comprados/coletados com mecânica de desgaste (poções, durabilidade de arma, armadura). | T41, T13–T15 |
| D4 | **Combo vale também para as classes à distância** (3 disparos encadeados; o 1º mais lento). | T11, T42–T44 |
| D5 | Inimigos por fase definidos na seção 4, com **dificuldade crescente entre fases e dentro de cada fase**, vários inimigos simultâneos e variantes mais rápidas/desafiadoras. | seção 4, T26, T36 |
| D6 | O **progresso persiste entre fases** (ouro, poções, arma, armadura) numa `RunState`; não há arquivo de save entre execuções (T51 fica fora do escopo). | T50 |
| D7 | **Esc abre um menu**: Continuar · Ver comandos · Reiniciar fase · Sair. | T05 |

### 6.2 Em aberto (padrão recomendado; seguem a menos que você diga o contrário)

| ID | Pergunta | Padrão recomendado |
|---|---|---|
| D8 | A loja listava "arremessáveis". Com a faca infinita (D3), o que é isso? | **Consumíveis arremessáveis** (ex.: bomba/pote de óleo, com a mecânica de gasto da D3), usados na **tecla 2**, vendidos na loja; entram depois de T50 (usam o projétil `lob` de T04). |
| D9 | Ao **reiniciar a fase** (pela derrota ou pelo menu), o que acontece com ouro/itens ganhos na tentativa? | Volta ao **estado do início da fase** (snapshot da `RunState`); evita "farmar" morrendo. Renascer com ouro **mantém** tudo (o jogador pagou por isso). |
| D10 | O que o **renascimento pago** restaura? | Vida cheia no mesmo x, `REVIVE_INVULN` = 2 s; inimigos e boss mantêm o estado; barra de combo zerada (D2); poções/arma/armadura mantidas. |

## 7. Regras transversais

- **Testes primeiro nas fundações:** F0 deve fechar com `test_logic.py` e `simulate.py` iguais; cada feature adiciona
  testes em `test_logic.py` e usa o `fake_pygame` para o que depender de entrada.
- **Contrato de arte:** só acrescentar linhas no fim dos sheets; atualizar CLAUDE.md §5 e o `meta` do `.json`;
  rodar `build_assets.py --check` e `check_edges.py`; regenerar efeitos de golpe quando mexer nos frames 3–4.
- **Delegação (CLAUDE.md §6.1):** recolor/ícones/props simples/SFX/verificações → Haiku em pasta separada, com
  checagens automáticas antes do Sonnet olhar o PNG/GIF; poses, camadas novas no rig, VFX sincronizado e qualquer
  mudança de contrato → Sonnet. Na dúvida, Sonnet. O veredito de estética e som é do usuário.
- **Áudio:** cada feature nova com evento (`block`, `potion`, `break`, `throw`, `special`) ganha SFX via
  `game-audio-synthesis`; o usuário valida de ouvido.
- **Mudanças só em `config.py`** para balanceamento, sempre registradas no changelog (valor antes → depois).
- **Windows:** nada de caminhos/atalhos específicos; PyInstaller deve continuar achando `assets/` (`base_dir()`); rodar
  `build_exe.bat` ao fim de F3 e F5 (nunca foi testado).

## 8. Mapa README → tarefas

| Item do README | Tarefa |
|---|---|
| Armas como pickups; durabilidade; efeito do machado; animações do herói com cada arma | T13 |
| Arco e besta como pickups | T14 |
| Armadura | T15 |
| Poções no inventário | T10 |
| Combate à distância (arco, besta) | T04 + T14 (herói), T42/T43 (classes) |
| Novas classes; primário/secundário; arte das classes | T40–T44 |
| Combo no primário | T11 |
| Ataque especial e barra de combo | T12 (cavaleiro) + T42–T44 (demais) |
| Seleção de classe | T45 |
| Novos inimigos (fantasia, humanos); ataque à distância dos monstros; arte | T20–T25 (+ T04) |
| Fases; 3 fases temáticas; arte dos cenários | T30, T33–T35 |
| Dificuldade crescente, vários inimigos, elites (D5) | T26, T36 |
| Renascer por 100 de ouro ou reiniciar a fase (D1) | T37, T50 |
| Menu do Esc: continuar, comandos, reiniciar fase, sair (D7) | T05 |
| Boss e arena | T32 |
| Tela de conclusão | T31 |
| Loja | T50 |
