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
