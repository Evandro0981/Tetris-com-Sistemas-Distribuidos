'''
     Este arquivo serve para representarmos a aba de prévia das peças.
'''

from configuracao import *
from pygame.image import load
from os import path

class Previa:
     def __init__(self):
          # Esse metodo permite com que obtenhamos o exibir_superficie, ou melhor dizendo, o display da superfície que estamos usando
          self.mostrar_superficie = pygame.display.get_surface()
          
          # Define a superficie da aba de "previa"
          self.superficie = pygame.Surface((LARGURA_BARRA_LATERAL, ALTURA_JOGO * FRACAO_ALTURA_PREVIA - ESPACAMENTO))
          
          '''  O retangulo é uma forma de separarmos o display, sem ele, todas as abas ficariam umas sobrepostas às outras.
               Observe que no "get_rect" informamos a posição desajada que iremos colocar essa aba, no caso, "topright", ou
               canto superior direito.'''
          self.retangulo = self.superficie.get_rect(topright = (LARGURA_JANELA - ESPACAMENTO, ESPACAMENTO))

          #Pecas.
          self.pecas_por_cima = {peca: load(path.join('src','graficos', f'{peca}.png')).convert_alpha() for peca in TETROMINOS.keys()}

          #Posicao das imagens na interface.
          self.fragmento_altura = self.superficie.get_height()/3

     def mostrar_pecas(self, pecas):
          #Mostra as proximas pecas na interface.
          for index, peca in enumerate(pecas):
               imagem_peca = self.pecas_por_cima[peca]
               #Centralizar
               x = self.superficie.get_width()/2 
               y = self.fragmento_altura/2 + index * self.fragmento_altura
               retangulo = imagem_peca.get_rect(center = (x,y))
               self.superficie.blit(imagem_peca, retangulo)

     def executar(self, proximas_pecas):
          #Cor de funda para a interface que mostra as proximas pecas.
          self.superficie.fill(CINZA)

          self.mostrar_pecas(proximas_pecas)

          # O método blit serve para colocarmos uma superficie em cima de outra superficie, nesse caso "superficie" -> "mostrar_superficie"
          self.mostrar_superficie.blit(self.superficie, self.retangulo)
          
          pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.retangulo, 2, 2)
