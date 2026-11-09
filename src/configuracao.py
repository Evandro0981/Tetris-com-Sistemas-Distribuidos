import pygame

'''--Tamanho-da-Janela-do-Jogo--
 Essa estrutura serve para definir os componentes da janela do jogo, imagine como se fosse uma matriz.'''
COLUNAS = 10
LINHAS = 20
# Isso define o tamanho de cada célula da "matriz", ou janela do jogo.
TAMANHO_CELULA = 40
# Define a largura da janela do jogo.
LARGURA_JOGO = COLUNAS * TAMANHO_CELULA
# Define a altura da janela do jogo
ALTURA_JOGO = LINHAS * TAMANHO_CELULA 

''' --Barra-lateral--
 Aqui será definido uma janela lateral para o jogo.'''
# Define 200px para a largura da janela lateral.
LARGURA_BARRA_LATERAL = 200
# Essa variável servira para separar 70% da área da barra lateral
FRACAO_ALTURA_PREVIA = 0.7
# Enquanto essa separa os 30% restantes.
FRACAO_ALTURA_PONTUACAO = 1 - FRACAO_ALTURA_PREVIA

'''--Janela-Agrupamento--
Esta sessão serve para agrupar as duas janelas anteriores em uma janelas maior.'''
# Define o espaçamento de 20px, entre as janelas do jogo e da janela maior, que irá agrupar elas.
ESPACAMENTO = 20
# Este cálculo serve para definir a largura da janela de agrupamento.
LARGURA_JANELA = LARGURA_JOGO + LARGURA_BARRA_LATERAL + ESPACAMENTO * 3
# Este cálculo serve para definir a altura da janela de agrupamento.
ALTURA_JANELA = ALTURA_JOGO + ESPACAMENTO * 2

'''--Comportamento-do-Jogo--'''
VELOCIDADE_ATUALIZACAO_INICIAL = 200
TEMPO_ESPERA_MOVER = 200
TEMPO_ESPERA_ROTACIONAR = 200
DESLOCAMENTO_BLOCO = pygame.Vector2(COLUNAS // 2, -1)

# Cores
AMARELO = '#f1e60d'
VERMELHO = '#e51b20'
AZUL = '#204b9b'
VERDE = '#65b32e'
ROXO = '#7b217f'
CIANO = '#6cc6d9'
LARANJA = '#f07e13'
CINZA = '#1C1C1C'
LINHA_COR = '#FFFFFF'

# formas
TETROMINOS = {
     'T': {'forma': [(0,0), (-1,0), (1,0), (0,-1)], 'cor': ROXO},
     'O': {'forma': [(0,0), (0,-1), (1,0), (1,-1)], 'cor': AMARELO},
     'J': {'forma': [(0,0), (0,-1), (0,1), (-1,1)], 'cor': AZUL},
     'L': {'forma': [(0,0), (0,-1), (0,1), (1,1)], 'cor': LARANJA},
     'I': {'forma': [(0,0), (0,-1), (0,-2), (0,1)], 'cor': CIANO},
     'S': {'forma': [(0,0), (-1,0), (0,-1), (1,-1)], 'cor': VERDE},
     'Z': {'forma': [(0,0), (1,0), (0,-1), (-1,-1)], 'cor': VERMELHO},
}

PONTOS_DADOS = {1: 40, 2: 100, 3: 300, 4: 1200}