from configuracao import *
from pygame.image import load
from os import path

class Previa:
     def __init__(self, offset_x=0):
          self.mostrar_superficie = pygame.display.get_surface()
          self.superficie = pygame.Surface((LARGURA_BARRA_LATERAL, ALTURA_JOGO * FRACAO_ALTURA_PREVIA - ESPACAMENTO))
          
          # Posiciona a caixa de prévia ao lado do tabuleiro da respectiva equipe
          pos_x = offset_x + ESPACAMENTO + LARGURA_JOGO + ESPACAMENTO
          self.retangulo = self.superficie.get_rect(topleft = (pos_x, ESPACAMENTO))

          self.pecas_por_cima = {peca: load(path.join('graficos', f'{peca}.png')).convert_alpha() for peca in TETROMINOS.keys()}
          self.fragmento_altura = self.superficie.get_height() / 3

     def mostrar_pecas(self, pecas):
          for index, peca in enumerate(pecas):
               imagem_peca = self.pecas_por_cima[peca]
               x = self.superficie.get_width() / 2 
               y = self.fragmento_altura / 2 + index * self.fragmento_altura
               retangulo = imagem_peca.get_rect(center = (x, y))
               self.superficie.blit(imagem_peca, retangulo)

     def executar(self, proximas_pecas):
          self.superficie.fill(COR_FUNDO)
          self.mostrar_pecas(proximas_pecas)
          self.mostrar_superficie.blit(self.superficie, self.retangulo)
          pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.retangulo, 2, 2)