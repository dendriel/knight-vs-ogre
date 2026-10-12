# Knight vs Ogre (demo)

## Como rodar (Windows)
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
- Armadura: 10% dos ogros derrubam uma peca (barra azul no HUD, ate 50 pontos). Todo dano desconta primeiro dela; quando acaba, o resto do golpe vai para a vida e a armadura quebra. Nao e consumida se a barra ja esta cheia.
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
- [ ] T12 barra de combo e ataque especial (segurar com a barra cheia, soltar para disparar) **(arte)**
- [ ] T14 arco e besta como pickups (projetil, durabilidade) **(arte)**

### Inimigos
- [ ] T20 IA modular | T26 fichas de ataque e elites (veterano, bruto, agil)
- [ ] T22 cavaleiro inimigo | T21 lanceiro | T23 arqueiro (tiro em parabola com marcador) | T24 cavaleiro com escudo
- [ ] T25 monstros de fantasia (orc, goblin, kobold, minotauro) **(arte)**

### Fases e progressao
- [ ] T30 sistema de fases (percurso finito; o modo infinito vira a fase `endless`)
- [ ] T36 encontros e dificuldade crescente (entre fases e dentro de cada fase; varios inimigos ao mesmo tempo)
- [ ] T37 derrota: renascer por 100 de ouro ou reiniciar a fase
- [ ] T31 tela de conclusao com estatisticas
- [ ] T33 / T34 / T35 temas: planicie, floresta inglesa, cidade **(arte)**
- [ ] T32 boss e arena no fim de cada fase **(arte)**

### Classes
- [ ] T40 classes | T41 ataque secundario (botao direito; faca do cavaleiro) | T42 arqueiro | T45 selecao de classe
- [ ] T43 besteiro | T44 mago **(arte)**

### Economia
- [ ] T50 loja e fluxo da run (Selecao -> Fase -> Conclusao -> Loja -> Fase seguinte); ouro e itens passam de fase em fase
