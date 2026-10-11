# Changelog

Formato: um bloco por data, mais recente primeiro (todos os commits do mesmo dia ficam juntos); mudanças ainda não
commitadas entram no bloco do dia, ou em **[Não lançado]** se forem de outra data.
Constantes entre crases estão em `game/config.py`. Só aparecem as categorias que têm itens.
Categorias: Jogabilidade · Balanceamento · Arte · Contrato de arte · Áudio · Técnico · Correções · Pendente de validação.

## [2026-10-11]

### Jogabilidade
- Pulo no **Espaço** (altura ≈ a do cavaleiro, move-se no ar); o ataque passa para o **botão esquerdo do mouse**.
- O cavaleiro anda enquanto ataca (sem virar de lado) e pode pular atacando.
- Personagens não colidem: atravessam-se, e o alcance do golpe (`KNIGHT_REACH`/`OGRE_REACH`, início em −12) cobre alvo sobreposto.
- Caixas de meio cavaleiro de altura: dá para pousar em cima e atravessar no chão. Caixa solta no slot 0 e escada de 1-2-3 caixas no slot 2.
- Alcance vertical (`VERTICAL_REACH` = 30): fora dele ninguém acerta; o ogro espera embaixo sem balançar o machado.
- Cair de uma caixa sem ter pulado toca a animação de queda.

### Balanceamento
- `OGRE_MAX_HP` 100 → 30 (3 golpes); barras de vida usam o máximo de cada lutador.
- `HERO_SPEED` 84 → 120; o herói usa a animação `run` (`RUN_ANIM_SPEED` = 1,65).
- Ataque de espada 1,5x → 2,0x (`KNIGHT_ATTACK_ANIM_SPEED`); o do ogro continua 1,5x (`ATTACK_ANIM_SPEED`).
- Invulnerabilidade do ogro após dano: 1,2 s → 1,0 s (`OGRE_HURT_INVULN_EXTRA` = 0,4; o herói segue com `HURT_INVULN_EXTRA` = 0,6).
- Experimento revertido: ogro sem invulnerabilidade pós-dano (`OGRE_HURT_INVULN = False`) morria rápido demais.
- Pausa do ogro antes de bater (`OGRE_WAIT_BEFORE_ATTACK`) 0,55–0,95 s → 0,35–0,65 s.
- Novas constantes: `JUMP_HEIGHT` 44, `JUMP_RISE_TIME` 0,34, `BOX_H` 23, `BOX_W` 24, `ATTACK_MOVE_FACTOR` 1,0.

### Arte
- `attack_sword` trocou o golpe por cima por uma varredura lateral (lâmina na altura do ombro, de trás para a frente); `sword_slash` regenerado com arco raso na altura do peito para acompanhar a nova pose.
- Novas animações do cavaleiro `jump_up` e `jump_fall`.
- Novo sprite de cenário `box` (caixote de madeira 24x24).

### Contrato de arte
- `knight_spritesheet`: só a linha `attack_sword` mudou (e `sword_slash` no VFX); linhas 9 (`jump_up`) e 10 (`jump_fall`) anexadas; as demais inalteradas pixel a pixel.
- `assets/box.png` novo; caixas empilhadas compartilham a linha de contorno (23 px por nível).

### Correções
- O ogro atacava para um lado enquanto o herói passava por ele para o outro: agora ele se vira durante a preparação do golpe (antes do frame ativo) e trava a direção só no golpe.

### Técnico
- Primeiro commit do jogo completo: código, `art_tools/`, `assets/`, testes e as 4 skills do projeto.
- `.gitignore` com Python, `out/`, `build/`, `dist/` e configurações locais do Claude Code.
- Novos testes de pulo, caixas, escada, alcance vertical, sobreposição, ataque em movimento e direção do ogro (`tests/test_logic.py`).
- `tests/fake_pygame.py` e `tests/simulate.py` passam a simular o botão esquerdo do mouse.
- `CLAUDE.md`: seção 4.1 (pulo, caixas, alcance), critério de delegação ao Haiku (6.1) e regra do changelog (6.2). Este changelog.

### Pendente de validação
- Feeling do pulo, do ataque lateral e da velocidade nova com teclado e mouse reais (pygame de verdade).
- Sprites `jump_up`/`jump_fall` vistos só em imagem estática, não em movimento.
