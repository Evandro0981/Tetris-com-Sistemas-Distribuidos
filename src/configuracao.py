import pygame

'''--Tamanho-da-Janela-do-Jogo--'''
COLUNAS = 10
LINHAS = 20
TAMANHO_CELULA = 40

LARGURA_JOGO = COLUNAS * TAMANHO_CELULA  # 400px
ALTURA_JOGO = LINHAS * TAMANHO_CELULA   # 800px

'''--Barra-lateral--'''
LARGURA_BARRA_LATERAL = 200
FRACAO_ALTURA_PREVIA = 0.7
FRACAO_ALTURA_PONTUACAO = 1 - FRACAO_ALTURA_PREVIA

'''--Janela-Agrupamento (Dois Tabuleiros)--'''
ESPACAMENTO = 20

# Largura de 1 conjunto completo (Jogo + Barra Lateral + Espaço)
LARGURA_TABULEIRO_COMPLETO = LARGURA_JOGO + LARGURA_BARRA_LATERAL + ESPACAMENTO

# Largura total para os 2 tabuleiros lado a lado
LARGURA_JANELA = (LARGURA_TABULEIRO_COMPLETO * 2) + (ESPACAMENTO * 2)
ALTURA_JANELA = ALTURA_JOGO + ESPACAMENTO * 2

'''--Comportamento-do-Jogo--'''
VELOCIDADE_ATUALIZACAO_INICIAL = 400
TEMPO_ESPERA_MOVER = 150
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

# Formas
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