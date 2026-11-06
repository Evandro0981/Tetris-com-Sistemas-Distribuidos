'''
     Este arquivo serve para representarmos o jogo em si, 
     ele é o arquivo principal e que conterá a maior parte da lógica do projeto.
'''

from configuracao import *
from random import choice
from temporizador import Temporizador



class Jogo:
     def __init__(self):
          # Define a superficie da aba do jogo
          self.superficie = pygame.Surface((LARGURA_JOGO, ALTURA_JOGO))
          # Esse metodo permite com que obtenhamos o exibir_superficie, ou melhor dizendo, o display da superfície que estamos usando
          self.mostrar_superficie = pygame.display.get_surface()
          # Estamos definindo um retangulo aqui, para tracejar uma borda para todo o jogo.
          self.retangulo = self.superficie.get_rect(topleft = (ESPACAMENTO, ESPACAMENTO))
          self.sprites = pygame.sprite.Group()
          
          
          # linhas
          self.superficie_linha = self.superficie.copy()
          self.superficie_linha.fill((0, 255, 0))
          self.superficie_linha.set_colorkey((0, 255, 0))
          self.superficie_linha.set_alpha(120)
          
          # tetromino
          self.tetromino = Tetromino(choice(list(TETROMINOS.keys())), self.sprites)
          
          # temporizador
          self.temporizadores = {
               'movimento vertical': Temporizador(VELOCIDADE_ATUALIZACAO_INICIAL, True, self.mover_pbaixo),
               'movimento horizontal': Temporizador(TEMPO_ESPERA_MOVER) 
          }
          self.temporizadores['movimento vertical'].ativar()
          
     def atualizar_temporizador(self):
          for temporizador in self.temporizadores.values():
               temporizador.atualizar()
     
     def mover_pbaixo(self):
          self.tetromino.mover_pbaixo()
     
     def desenhar_grade(self):
          '''  Observe que o metodo pygame.draw.line possui argumentos para representar o inicio e fim de uma linha.
               Logo após o argumento "LINHA_COR" está a posição inicial, que precisa ser representado por uma tupla,
               como exemplo, no desenho das linhas verticais, na tupla da posição inicial, nosso "x" é o tamanho da célula * a coluna atual,
               isso se deve pois, a cada iteração do loop a coluna será incrementada e o cálculo levará à posições mais distantes.
               Já nosso y é a posição 0 da superficie do jogo, pois ele representa aonde iniciará o tracejamento da linha, nesse caso,
               iniciará no topo da nossa superficie, por isso definimos como 0.
               
               A posição final, que é a segunda tupla, tem o mesmo raciocinio, primeiro definimos o "x" que é o espaçamento entre
               cada linha e depois pegado a altura da superficie (no caso das linhas verticais) 
               para definir até onde vai o tracejamento.
          '''
          # desenha as linhas verticais
          for coluna in range(1, COLUNAS):
               x = coluna * TAMANHO_CELULA
               pygame.draw.line(self.superficie_linha, LINHA_COR, (x, 0), (x, self.superficie.get_height()), 1)

          # desenha as linhas horizontais
          for linha in range(1, LINHAS):
               y = linha * TAMANHO_CELULA
               pygame.draw.line(self.superficie_linha, LINHA_COR, (0, y), (self.superficie.get_width(), y), 1)
          
          self.superficie.blit(self.superficie_linha, (0,0))
          
     def executar(self):
          # atualizar
          self.input()
          self.atualizar_temporizador()
          self.sprites.update()
          
          self.superficie.fill(CINZA)
          self.sprites.draw(self.superficie)
           
          self.desenhar_grade()
          # O método blit serve para colocarmos uma superficie em cima de outra superficie, nesse caso "superficie" -> "mostrar_superficie"
          self.mostrar_superficie.blit(self.superficie, (ESPACAMENTO, ESPACAMENTO))
          pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.retangulo, 2, 2)    

     def input(self):
          '''
               Move a peca referente a acao feita pelo jogador(esquerda, direita) 
          '''
          movimento = pygame.key.get_pressed()

          if not self.temporizadores['movimento horizontal'].ativo:  
               if movimento[pygame.K_LEFT]:
                    self.tetromino.move_horizontal(-1)
                    self.temporizadores['movimento horizontal'].ativar()
               if movimento[pygame.K_RIGHT]:
                    self.tetromino.move_horizontal(1)
                    self.temporizadores['movimento horizontal'].ativar()
                   

class Tetromino:
     def __init__(self, forma, grupo):
          
          # Base
          self.posicoes_blocos = TETROMINOS[forma]['forma']
          self.cor = TETROMINOS[forma]['cor']

          # criando blocos
          self.blocos = [Bloco(grupo, posicao, self.cor) for posicao in self.posicoes_blocos]

     #Colisões
     def proxima_colisao_horizontal(self, blocos, quantia):
          lista_colisoes =[bloco.colisao_horizontal(int(bloco.posicao.x + quantia)) for bloco in self.blocos]
          return True if any(lista_colisoes) else False

     def proxima_colisao_vertical(self, blocos, quantia):
          lista_colisoes =[bloco.colisao_vertical(int(bloco.posicao.y + quantia)) for bloco in self.blocos]
          return True if any(lista_colisoes) else False


     def move_horizontal(self, quantia):
          if not self.proxima_colisao_horizontal(self.blocos, quantia):
               for bloco in self.blocos:
                    bloco.posicao.x += quantia

     def mover_pbaixo(self):
          if not self.proxima_colisao_vertical(self.blocos, 1):
               for bloco in self.blocos:
                    bloco.posicao.y += 1
          
          
'''  Classe Bloco servira para gerarmos os blocos do tetris
     A herança com Sprite do pygame serve para conseguirmos mostrar uma superficie e posiciona-la de forma mais simples.'''
class Bloco(pygame.sprite.Sprite):
     
     '''  Alguns nomes precisam estar em ingles por exigência do próprio pygame, mais especificamente o método
          "group.draw()", que exige atributos "image" e "rect", então na classe Bloco eles se manterão em ingles.'''
     def __init__(self, grupo, posicao, cor):
          # geral
          super().__init__(grupo)
          self.image = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA))
          self.image.fill(cor)
          
          # posicao
          self.posicao = pygame.Vector2(posicao) + DESLOCAMENTO_BLOCO
          
          self.rect = self.image.get_rect(topleft = self.posicao * TAMANHO_CELULA)

     def colisao_horizontal(self, x):
          '''
               Não deixa que a peça caia para fora da matriz. '''
          if not 0 <= x < COLUNAS:
               return True
          
     def colisao_vertical(self, y):
          '''
               Não deixa que a peça caia para fora da matriz. '''
          if y >= LINHAS:
               return True
     
     def update(self):
          #self.rect = self.image.get_rect(topleft = self.posicao * TAMANHO_CELULA)
          self.rect.topleft = self.posicao * TAMANHO_CELULA     
          