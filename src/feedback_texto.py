'''
    feedback_texto.py
    Sistema de feedback de texto flutuante para o jogo Tetris multiplayer.
    Exibe textos no centro do tabuleiro de cada equipe que sobem suavemente e desaparecem.
'''

import pygame
from os import path
from configuracao import *


def carregar_fonte(tamanho):
    '''Carrega a fonte do jogo, sem dar erros se for executado numa pasta diferente'''
    caminhos_possiveis = [
        path.join('graficos', 'Russo_One.ttf'),
        path.join('src', 'graficos', 'Russo_One.ttf'),
        path.join(path.dirname(__file__), 'graficos', 'Russo_One.ttf')
    ]
    for caminho in caminhos_possiveis:
        if path.exists(caminho):
            try:
                return pygame.font.Font(caminho, tamanho)
            except Exception:
                pass
    return pygame.font.Font(None, tamanho)


class MensagemFeedback:
    def __init__(self, texto, posicao, cor=AMARELO, tamanho=28, duracao=1200, distancia_subida=50, fonte=None):
        self.texto = texto
        self.cor = cor
        self.duracao = duracao
        self.distancia_subida = distancia_subida
        self.tempo_inicio = pygame.time.get_ticks()
        self.finalizado = False

        self.fonte = fonte if fonte else carregar_fonte(tamanho)
        self.pos_x = posicao[0]
        self.pos_y = posicao[1]

    def atualizar(self):
        tempo_decorrido = pygame.time.get_ticks() - self.tempo_inicio
        if tempo_decorrido >= self.duracao:
            self.finalizado = True

    def desenhar(self, superficie):
        if self.finalizado:
            return

        tempo_decorrido = pygame.time.get_ticks() - self.tempo_inicio
        progresso = min(1.0, max(0.0, tempo_decorrido / self.duracao))

        # Efeito de subida com desaceleração (ease-out)
        fator_subida = 1.0 - (1.0 - progresso) ** 2
        y_atual = self.pos_y - (fator_subida * self.distancia_subida)

        # Fade-out nos últimos 45% do tempo
        if progresso < 0.55:
            alpha = 255
        else:
            alpha = int(255 * (1.0 - (progresso - 0.55) / 0.45))
        alpha = max(0, min(255, alpha))

        if alpha <= 0:
            return

        # Sombra para destacar dos blocos coloridos do tabuleiro
        surf_sombra = self.fonte.render(self.texto, True, (0, 0, 0))
        surf_sombra.set_alpha(int(alpha * 0.75))
        rect_sombra = surf_sombra.get_rect(center=(int(self.pos_x) + 2, int(y_atual) + 2))
        superficie.blit(surf_sombra, rect_sombra)

        # Texto principal
        surf_texto = self.fonte.render(self.texto, True, self.cor)
        surf_texto.set_alpha(alpha)
        rect_texto = surf_texto.get_rect(center=(int(self.pos_x), int(y_atual)))
        superficie.blit(surf_texto, rect_texto)


class FeedbackTexto:
    def __init__(self, tamanho_padrao=28):
        self.tamanho_padrao = tamanho_padrao
        self.fonte = carregar_fonte(tamanho_padrao)
        self.mensagens = []

    def criar_feedback(self, texto, posicao, cor=AMARELO, duracao=1200, distancia_subida=50, tamanho=None):
        fonte_usar = self.fonte if (tamanho is None or tamanho == self.tamanho_padrao) else carregar_fonte(tamanho)
        msg = MensagemFeedback(
            texto=texto,
            posicao=posicao,
            cor=cor,
            duracao=duracao,
            distancia_subida=distancia_subida,
            fonte=fonte_usar
        )
        self.mensagens.append(msg)
        return msg

    def atualizar(self):
        for msg in self.mensagens:
            msg.atualizar()
        self.mensagens = [m for m in self.mensagens if not m.finalizado]

    def desenhar(self, superficie):
        for msg in self.mensagens:
            msg.desenhar(superficie)

    def executar(self, superficie):
        self.atualizar()
        self.desenhar(superficie)

    def limpar(self):
        self.mensagens.clear()