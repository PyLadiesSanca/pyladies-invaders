# PyLadies Invaders
Jogo desenvolvido para ensinar programação orientada a objetos usando PyGame.

## Descrição
O PyLadies Invaders é um jogo de nave espacial onde o jogador controla uma PyLady que deve atirar em inimigos que estão descendo em direção a ela.

O jogo é inspirado no clássico Space Invaders.

https://github.com/PyLadiesSanca/pyladies-invaders/assets/8601883/9f94fe6c-83e1-4a68-82dc-ee7c69382ef8

## Instruções de instalação
Para executar o código e jogar o PyLadies Invaders é necessário instalar Python 3.10 ou superior.

É recomendado criar um virtualenv para instalar as dependências do projeto.

Estando dentro da pasta raíz do repositório (`pyladies-invaders`), execute os comandos abaixo:

```bash
cd pyladies-invaders
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Instruções de execução
Para executar o jogo, entre na pasta do jogo (`pyladies_invaders`) e execute o comando abaixo com o virtualenv ativado:

```bash
cd pyladies_invaders
python pyladies_invaders.py
```

## Instruções de jogo
- Use as setas direcionais para mover a PyLady para a esquerda e para a direita.
- Use a barra de espaço para atirar nos inimigos.
- O jogo acaba quando os inimigos atingem a PyLady ou quando todos os inimigos são destruídos.
- Caso precise sair do jogo, pressione a tecla `ESC`.
