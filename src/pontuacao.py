'''
     Este arquivo serve para representarmos a aba de pontuação do jogador.
'''

from configuracao import *
from os import path

class Pontuacao:
     def __init__(self):
          # Define a superficie da aba de "pontuacao"
          self.superficie = pygame.Surface((LARGURA_BARRA_LATERAL, ALTURA_JOGO * FRACAO_ALTURA_PONTUACAO - ESPACAMENTO))
          '''  O retangulo é uma forma de separarmos o display, sem ele, todas as abas ficariam umas sobrepostas às outras.
               Observe que no "get_rect" informamos a posição desajada que iremos colocar essa aba, no caso, "bottomright", ou
               canto inferior direito.'''
          self.rect = self.superficie.get_rect(bottomright = (LARGURA_JANELA - ESPACAMENTO, ALTURA_JANELA - ESPACAMENTO))
          # Esse metodo permite com que obtenhamos o exibir_superficie, ou melhor dizendo, o display da superfície que estamos usando
          self.mostrar_superficie = pygame.display.get_surface()

          # Fonte
          self.fonte = pygame.font.Font(path.join('src', 'graficos', 'Russo_One.ttf'), 30)
          
          # Incrementando
          self.incrementa_altura = self.superficie.get_height() / 3

          # Dados
          self.pontos = 0
          self.level = 1
          self.linhas = 0

     def exibe_texto(self, posicao, texto):
          superficie_texto = self.fonte.render(f'{texto[0]}: {texto[1]}', True, 'white')
          area_texto = superficie_texto.get_rect(center = posicao)
          self.superficie.blit(superficie_texto, area_texto)
          
     def executar(self):
          self.superficie.fill(CINZA)
          for index, texto in enumerate([('Pontos', self.pontos), ('Level', self.level), ('Linhas', self.linhas)]):
               x = self.superficie.get_width() / 2
               y = self.incrementa_altura / 2 + index * self.incrementa_altura
               self.exibe_texto((x,y), texto)

          # O método blit serve para colocarmos uma superficie em cima de outra superficie, nesse caso "superficie" -> "mostrar_superficie"
          self.mostrar_superficie.blit(self.superficie, self.rect) 

          pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.rect, 2, 2)      