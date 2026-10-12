# Knight vs Ogre (demo)

## Como rodar (Windows)
1. Instale o Python 3.10+ (marque "Add Python to PATH").
2. De dois cliques em `run_game.bat` (instala o pygame na primeira vez e abre o jogo).
   Ou no terminal: `pip install -r requirements.txt` e `python main.py`.

Para gerar um `.exe`: `build_exe.bat` (resultado em `dist\KnightVsOgre.exe`).

## Controles
- Setas esquerda/direita ou A / D: andar
- Espaco: pular
- Botao esquerdo do mouse: atacar com a espada (golpe lateral); da para andar enquanto ataca
- F11: tela cheia | Esc: sair

## Regras
- Heroi (esquerda) comeca com 100 de vida e o ogro (direita) com 30; cada golpe que acerta tira 10.
- Caixas: da para pular em cima delas (a escada de 3 niveis deixa o heroi fora do alcance do ogro).
- Ao ser atingido o personagem toca "hurt" e nao pode andar nem atacar. Depois o heroi fica um instante invulneravel (o ogro nao).
- O golpe so acerta nos frames de impacto da animacao (o rastro da arma mostra onde).
- Itens: cada ogro derrotado tem 30% de chance de derrubar uma pocao vermelha (+30 de vida) e 50% de derrubar uma bolsa de 5 a 10 moedas de ouro. So o heroi pega (basta chegar perto); o ouro aparece no HUD abaixo da vida e nao zera quando o heroi morre.
- Ogro morreu: o corpo fica no chao e outro ogro entra pela direita. Heroi morreu: outro heroi nasce na esquerda.
- Contadores de derrotas de cada lado ficam abaixo das barras de vida.
- O cenario e infinito (casas, arvores e pocos sao gerados por "fatias" conforme a camera anda).

## Ajustes de dificuldade
Tudo fica em `game/config.py`: velocidade, tempo de espera do ogro antes de atacar (`OGRE_WAIT_BEFORE_ATTACK`),
descanso entre golpes (`OGRE_COOLDOWN`), alcance dos golpes, dano, tempo de respawn etc.

## Estrutura
- `main.py` laco principal, teclado, janela (escala inteira 3x, 480x270 internos)
- `game/logic.py` regras (sem pygame, testavel) | `game/view.py` desenho e HUD | `game/config.py` numeros
- `assets/` spritesheets (png + json), cenario
- `tests/` testes das regras e simulador (roda o jogo sem janela e grava GIF)

## TODO (ideias e tarefas planejadas)

Registro de ideias, sem ordem de prioridade. As marcadas com **(arte)** exigem novas animacoes/sprites.

### Armas e equipamentos
- [ ] Armas como pickups: o ogro pode derrubar o proprio machado; o heroi pega e passa a usa-lo no lugar da espada.
- [ ] Durabilidade das armas (100% -> 0%): cada ataque gasta uma parte (ex.: ~3% por golpe no machado); ao zerar, a arma quebra.
- [ ] O machado precisa ter um efeito proprio que compense o desgaste (mais dano, mais alcance ou golpe mais lento e forte).
- [ ] **(arte)** Animacoes do heroi com cada arma nova: para cada arma/equipamento, redesenhar o heroi com **todas** as
      animacoes base (idle, walk/run, ataque, hurt, death, jump_up, jump_fall) segurando a arma. Primeiro caso: o machado do ogro.
- [ ] Arco e besta como pickups, tambem com durabilidade.
- [ ] Armadura: obtida pelo jogador; todo dano sofrido desconta da armadura e nao da vida. Quando quebra, o dano volta a descontar da vida.
- [ ] Pocoes de vida no inventario: ate 10, exibidas no HUD e consumidas por tecla de atalho (tecla 1).

### Combate e classes
- [ ] Combate a distancia com arco e flecha (projetil, mira, dano, alcance).
- [ ] Combate a distancia com besta (projetil proprio; diferenciar do arco, ex.: mais dano e recarga mais lenta).
- [ ] Novas classes jogaveis: **arqueiro**, **besteiro** e **mago**, cada uma com atributos diferentes (vida, velocidade, dano, alcance...).
- [ ] Ataque primario e secundario por classe:
  - Cavaleiro: primario = espada; secundario = arremessar uma faca.
  - Arqueiro: primario = arco e flecha; secundario = corte com espada curta.
  - Besteiro: primario = besta; secundario = machado pequeno.
  - Mago: primario = cajado que arremessa bolas de fogo; secundario = bater o cajado no chao e fazer surgir
    espinhos de pedra a frente, atingindo os inimigos na area.
- [ ] **(arte)** Sprites e animacoes de cada classe e de cada ataque (incluindo projeteis, bola de fogo e espinhos de pedra).
- [ ] Tela de selecao de classe no inicio da partida: cards lado a lado, cada um com uma imagem representativa e os
      atributos da classe; a classe e escolhida com um clique.

### Inimigos
- [ ] Novos inimigos de fantasia medieval (goblin, minotauro, kobold, orc...), com versoes de ataque curto (corpo a corpo)
      e de ataque a distancia.
- [ ] O ataque a distancia dos monstros e um tiro/arremesso para cima que faz uma curva no ceu e cai no chao, dando ao
      heroi chance de desviar.
- [ ] **(arte)** Sprites e animacoes de cada novo inimigo (reaproveitar o esqueleto de `ogre_gen.py`).

### Fases e progressao
- [ ] Fases: um percurso da esquerda para a direita, com o cenario variando e diferentes encontros de inimigos.
- [ ] Boss no fim de cada cenario: perto do final a tela trava em modo "arena" ate o boss ser derrotado; depois que a
      tela e liberada, o jogador segue em frente para concluir o cenario.
- [ ] Tela de conclusao do cenario com estatisticas (monstros mortos, dano causado, ouro adquirido).
- [ ] Segunda tela: loja, onde o heroi gasta o ouro em equipamentos para a proxima partida (armas pickup, pocoes,
      arremessaveis e armadura).
