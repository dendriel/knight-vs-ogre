# Knight vs Ogre (demo)

## Como rodar (Windows)
O jogo abre num menu inicial: **Campanha** (3 fases), **Modo infinito** (o combate original), comandos e sair. Para pular o menu: `python main.py --endless` ou `python main.py --stage 2`.

1. Instale o Python 3.10+ (marque "Add Python to PATH").
2. De dois cliques em `run_game.bat` (instala o pygame na primeira vez e abre o jogo).
   Ou no terminal: `pip install -r requirements.txt` e `python main.py`.

Para gerar um `.exe`: `build_exe.bat` (resultado em `dist\KnightVsOgre.exe`).

## Controles
- Setas esquerda/direita ou A / D: andar
- Espaco: pular
- 1: beber uma pocao do inventario
- Botao esquerdo do mouse: atacar com a espada (golpe lateral); da para andar enquanto ataca. Clicar de novo durante o golpe (a partir do impacto) encadeia o combo de 3 golpes (corte, corte ascendente, golpe final mais forte); segurar o botao so repete o primeiro golpe
- M: liga/desliga o som | F11: tela cheia
- Esc: menu (continuar, ver comandos, reiniciar fase, sair); navegue com as setas + Enter ou com o mouse

## Regras
- Heroi (esquerda) comeca com 100 de vida e o ogro (direita) com 30; cada golpe que acerta tira 10.
- Caixas: da para pular em cima delas (a escada de 3 niveis deixa o heroi fora do alcance do ogro).
- Ao ser atingido o personagem toca "hurt" e nao pode andar nem atacar. Depois o heroi fica um instante invulneravel (o ogro nao).
- O golpe so acerta nos frames de impacto da animacao (o rastro da arma mostra onde).
- Itens: cada ogro derrotado tem 30% de chance de derrubar uma pocao vermelha e 50% de derrubar uma bolsa de 5 a 10 moedas de ouro. So o heroi pega (basta chegar perto). A pocao vai para o inventario (ate 10; com 10 ela fica no chao) e a tecla 1 bebe uma (+30 de vida, so se estiver ferido). O ouro e as pocoes aparecem no HUD, nao zeram quando o heroi morre.
- Machado: 15% dos ogros derrubam o proprio machado; ao pegar, o heroi passa a atacar com ele no lugar da espada (dano 20, alcance +8, golpe 1,35x mais lento, anda a 80% da velocidade; ignora defesa). Cada golpe gasta 3% de durabilidade (barra no HUD); em 0% ele quebra e o heroi volta a espada. O heroi que morre perde a arma.
- Arco e besta: 6% / 4% dos ogros derrubam um (pickup raro, mesma durabilidade e HUD do machado). O arco dispara uma flecha a cada golpe (dano 10, alcance 280, 2,5% de desgaste por tiro); a besta, virote de dano 20 e alcance 380, com recarga de 0,8 s e 4% de desgaste. A flecha so acerta alvos na faixa vertical do heroi (em linha reta).
- Armadura: 10% dos ogros derrubam uma peca (barra azul no HUD, ate 50 pontos). Todo dano desconta primeiro dela; quando acaba, o resto do golpe vai para a vida e a armadura quebra. Nao e consumida se a barra ja esta cheia.
- Barra de combo (laranja no HUD): enche com o dano causado (x1,5) e recebido (x1,0). Com a barra cheia, segure o botao de ataque (0,25 s) para carregar e solte para disparar o **giro especial** (2 golpes de 15 em volta, ignora a invulnerabilidade dos alvos e o heroi fica invulneravel durante o giro). Um clique rapido com a barra cheia ainda e um golpe normal. A barra zera ao usar e quando o heroi morre.
- Ogro morreu: o corpo fica no chao e outro ogro entra pela direita. Heroi morreu: outro heroi nasce na esquerda.
- Contadores de derrotas de cada lado ficam abaixo das barras de vida.
- O cenario do modo infinito e infinito (casas, arvores e pocos sao gerados por "fatias" conforme a camera anda). Nas fases o percurso e finito: a camera trava nas pontas, os inimigos entram quando o heroi cruza cada linha de encontro e a fase termina quando todos estao derrotados e o heroi chega ao fim. Morrer numa fase nao renasce sozinho (veja a tela de derrota).

## Ajustes de dificuldade
Tudo fica em `game/config.py`: velocidade, tempo de espera do ogro antes de atacar (`OGRE_WAIT_BEFORE_ATTACK`),
descanso entre golpes (`OGRE_COOLDOWN`), alcance dos golpes, dano, tempo de respawn etc.

## Estrutura
- `main.py` laco principal, teclado, janela (escala inteira 3x, 480x270 internos)
- `game/logic.py` regras (sem pygame, testavel) | `game/view.py` desenho e HUD | `game/config.py` numeros
- `assets/` spritesheets (png + json), cenario
- `game/scenes.py` telas (jogo, pausa, comandos) | `game/ui.py` menu
- `tests/` testes das regras (`test_logic.py`), das telas (`test_scenes.py`), do pygame real sem janela (`real_pygame_smoke.py`) e simulador (grava GIF)

## TODO (ideias e tarefas planejadas)

Vocabulario: **fase** = percurso com tema; **cenario** = arte do tema; **tela** = UI (selecao, conclusao, loja).
A ordem de execucao, as dependencias, as decisoes (D1-D10) e as incoerencias resolvidas estao em `TASKS_PLAN.md`.
Cada item traz o ID da tarefa; `[x]` = feito (ver `CHANGELOG.md`). Itens com **(arte)** exigem sprites novos.

### Fundacoes
- [x] T01 dados por tipo de lutador | T02 varios inimigos | T03 ataques como dados | T04 projeteis e dano em area
- [x] T05 entrada ampliada, cenas e menu do Esc (continuar, ver comandos, reiniciar fase, sair) | [x] T06 HUD em slots

### Cavaleiro
- [x] T10 pocoes no inventario (ate 10, tecla 1; **substitui** o "consumir ao pegar")
- [x] T11 combo de 3 golpes (sistema unico, serve a todas as classes) **(arte)**
- [x] T13 machado como pickup, com durabilidade e efeito proprio (mais dano/alcance, golpe mais lento) **(arte)**
- [x] T15 armadura (o dano desconta dela antes da vida)
- [x] T12 barra de combo e ataque especial (segurar com a barra cheia, soltar para disparar) **(arte)**
- [x] T14 arco e besta como pickups (projetil, durabilidade) **(arte)**

### Inimigos
- [x] T20 IA modular | [x] T26 fichas de ataque e elites (veterano, bruto, agil)
- [x] T22 cavaleiro inimigo | [x] T21 lanceiro | [x] T23 arqueiro (tiro em parabola com marcador) | [x] T24 cavaleiro com escudo
- [x] T25 monstros de fantasia (orc, goblin, kobold, minotauro) **(arte)**

### Fases e progressao
- [x] T30 sistema de fases (percurso finito; o modo infinito vira a fase `endless`)
- [x] T36 encontros e dificuldade crescente (entre fases e dentro de cada fase; varios inimigos ao mesmo tempo)
- [x] T37 derrota: renascer por 100 de ouro ou reiniciar a fase
- [x] T31 tela de conclusao com estatisticas
- [x] T33 / T34 / T35 temas: planicie, floresta inglesa, cidade **(arte)**
- [x] T32 boss e arena no fim de cada fase **(arte)**

### Classes
- [x] T40 classes | T41 ataque secundario (botao direito; faca do cavaleiro) | T42 arqueiro | T45 selecao de classe
- [ ] T43 besteiro | T44 mago **(arte)**

### Economia
- [ ] T50 loja e fluxo da run (Selecao -> Fase -> Conclusao -> Loja -> Fase seguinte); ouro e itens passam de fase em fase
