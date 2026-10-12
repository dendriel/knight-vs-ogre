# Knight vs Ogre (demo)

## Como rodar (Windows)
1. Instale o Python 3.10+ (marque "Add Python to PATH").
2. De dois cliques em `run_game.bat` (instala o pygame na primeira vez e abre o jogo).
   Ou no terminal: `pip install -r requirements.txt` e `python main.py`.

O jogo abre num menu inicial: **Campanha** (3 fases com chefe), **Modo infinito** (o combate original), comandos e sair;
depois escolha a classe (setas + Enter ou clique). Para pular o menu: `python main.py --endless`, `--stage 2` (ou
`--stage stage2`) e `--class ranger` (knight, ranger, crossbowman, mage).

Para gerar um `.exe`: `build_exe.bat` (resultado em `dist\KnightVsOgre.exe`).

## Controles
A lista que o jogo mostra em "Ver comandos" vem de `CONTROLS` em `game/config.py`.
- Setas esquerda/direita ou A / D: andar | Espaco: pular
- Botao esquerdo do mouse: ataque primario da classe (da para andar enquanto ataca). Clicar de novo durante o golpe
  (a partir do impacto) encadeia o combo de 3 golpes; segurar o botao so repete o primeiro golpe.
- Botao direito do mouse: ataque secundario da classe (infinito, so tem recarga)
- Segurar o botao esquerdo com a barra de combo cheia: carrega; soltar dispara o especial da classe
- 1: beber uma pocao | 2: arremessar uma bomba (comprada na loja)
- E: pegar arma / armadura do chao (potions e ouro sao automaticos); E de novo, sem nada por perto, solta a arma
- M: liga/desliga o som | F11: tela cheia | Esc: menu (continuar, comandos, reiniciar fase, sair)

## Classes
| Classe | Vida | Vel. | Primario (combo de 3) | Secundario | Especial |
|---|---|---|---|---|---|
| Cavaleiro | 100 | 120 | espada (10/10/15) | faca arremessada (3 cargas, 5 s cada) | giro (2 x 15 em volta) |
| Arqueiro | 80 | 135 | arco (8/8/14, a 3a atravessa) | espada curta | chuva de flechas |
| Besteiro | 110 | 105 | besta (14/14/22, a 3a atravessa; recarga) | machado pequeno | rajada de 6 virotes |
| Mago | 70 | 115 | bolas de fogo (12/12/16, a 3a explode) | espinhos de pedra (area) | tempestade de fogo |

Armas pickup (machado, arco, besta) servem a qualquer classe (tecla E). Depois do ultimo golpe de um combo ha um descanso de 0,5 s. Os especiais duram 3x mais e batem 2x mais forte.

## Regras
- Cada golpe tira vida conforme o ataque (espada 10, machado 20, flechas 8-14...). Ao ser atingido o personagem toca
  "hurt", nao pode andar nem atacar e fica um instante invulneravel.
- O golpe so acerta nos frames de impacto da animacao e dentro da faixa vertical do atacante (caixas de 2 ou 3 niveis
  deixam o heroi fora do alcance dos corpo a corpo).
- Itens soltos pelos inimigos: pocao (vai para o inventario, ate 3; tecla 1 cura 30), bolsa de ouro, armadura (barra
  azul, 50 pontos: desconta o dano antes da vida), machado / arco / besta (durabilidade, voltam a espada quando
  quebram). O heroi que morre perde a arma e a armadura; ouro e pocoes ficam.
- Barra de combo (laranja): enche com o dano causado (x0,5) e recebido (x0,33): o especial demora 3x mais para ficar disponivel; zera ao usar o especial e quando o
  heroi morre.
- **Inimigos**: ogro, soldado, lanceiro (alcance longo, zona morta colado), arqueiro (flecha em parabola com marcador no
  chao), escudeiro (bloqueia de frente; 3 golpes quebram a defesa por 2,5 s; a besta quebra com 1 tiro; machado e especial ignoram o escudo), orc, goblin (bando), kobold (pedras em
  parabola), minotauro (investida telegrafada: pule por cima). So alguns atacam ao mesmo tempo (fichas); ha variantes
  elite (veterano, bruto, agil) com tinta de cor.
- **Fases**: percurso finito com 3 temas (planicie, floresta, cidade). A dificuldade cresce entre as fases e dentro de
  cada uma (abertura, meio, pre-boss). No fim o boss fecha a tela (Ogro-Capitao, Rei Minotauro, Cavaleiro Negro); depois
  de derrota-lo siga a seta ate o fim. Conclusao mostra as estatisticas e abre a **loja** (pocao, armadura, armas,
  bombas) antes da fase seguinte.
- **Derrota** em fase: renascer no mesmo ponto por 100 de ouro, ou reiniciar a fase (volta ao estado do inicio da
  fase, passando pela loja). No modo infinito o heroi renasce sozinho e o ogro/elenco cresce com os abates.

## Ajustes de dificuldade
Tudo fica em `game/config.py` (velocidades, dano, pausas dos inimigos, recargas, precos...); as fases e a curva de
dificuldade ficam em `game/stages.py`.

## Estrutura
- `main.py` laco principal, entrada, pilha de telas, janela (escala inteira 3x, 480x270 internos)
- `game/logic.py` regras (sem pygame, testavel) | `game/stages.py` fases, temas, curva | `game/config.py` numeros
- `game/view.py` desenho, HUD e parallax | `game/scenes.py` telas | `game/ui.py` menu | `game/audio.py` sons
- `assets/` spritesheets (png + json), cenario, projeteis, icones, sons | `art_tools/` geradores da arte
- `tests/` `test_logic.py` (regras), `test_scenes.py` (telas), `test_fuzz.py` (teclas aleatorias), `real_pygame_smoke.py`
  (pygame real, sem janela), `simulate.py` (grava GIFs)

## Status do plano (`TASKS_PLAN.md`)
Todas as tarefas T00-T50 foram implementadas (ver `CHANGELOG.md`), exceto T51 (persistencia em arquivo, fora do
escopo) e a validacao por jogo real (feeling, sons, estetica), que e do usuario.

- [x] T00-T06 fundacoes (dados por lutador, varios inimigos, ataques como dados, projeteis, cenas/menu, HUD)
- [x] T10-T15 cavaleiro (pocoes, combo, machado, armadura, barra de combo e especial, arco e besta)
- [x] T20-T26 inimigos (IA modular, fichas e elites, soldado, lanceiro, arqueiro, escudeiro, monstros)
- [x] T30-T37 fases (sistema, dificuldade, derrota, conclusao, temas, boss e arena)
- [x] T40-T45 classes (arqueiro, besteiro, mago, secundario, selecao)
- [x] T50 loja e fluxo da run
