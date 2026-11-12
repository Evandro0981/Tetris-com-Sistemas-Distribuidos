from configuracao import *
from os import path

class Pontuacao:
     def __init__(self, offset_x=0):
          self.superficie = pygame.Surface((LARGURA_BARRA_LATERAL, ALTURA_JOGO * FRACAO_ALTURA_PONTUACAO - ESPACAMENTO))
          
          # Posiciona a caixa de pontuação abaixo da prévia da respectiva equipe
          pos_x = offset_x + ESPACAMENTO + LARGURA_JOGO + ESPACAMENTO
          pos_y = ESPACAMENTO + (ALTURA_JOGO * FRACAO_ALTURA_PREVIA)
          self.rect = self.superficie.get_rect(topleft = (pos_x, pos_y))
          
          self.mostrar_superficie = pygame.display.get_surface()
          self.fonte = pygame.font.Font(path.join('graficos', 'Russo_One.ttf'), 24)
          self.incrementa_altura = self.superficie.get_height() / 3

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
               self.exibe_texto((x, y), texto)

          self.mostrar_superficie.blit(self.superficie, self.rect)
          pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.rect, 2, 2)