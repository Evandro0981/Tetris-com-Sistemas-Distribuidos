from configuracao import *
from sys import exit

# componentes
from jogo import Jogo
from pontuacao import Pontuacao
from previa import Previa
from tela_inicial import TelaInicial

from random import choice
from os import path

class Main:
     def __init__(self):
          pygame.init()
          
          # musica de fundo
          pygame.mixer.init()
          
          caminho_musica = path.join('src', 'audio', 'Tetris_theme.mp3')
          
          pygame.mixer.music.load(caminho_musica)
          pygame.mixer.music.set_volume(0.3)
          pygame.mixer.music.play(-1)
          
          # Criando a superfície do jogo com o pygame 
          self.exibir_superficie = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
          # Utilizaremos o relógio para várias coisas no jogo, já que ele permitirá que mexamos com o tempo do jogo.
          self.relogio = pygame.time.Clock()
          # Título da janela
          pygame.display.set_caption('Tetris')

          # Estado do jogo ('menu' ou 'jogando')
          self.estado = 'menu'
          self.tela_inicial = TelaInicial(self.exibir_superficie, self.iniciar_jogo)

          # Componentes do jogo
          self.jogo = None
          self.pontuacao = None
          self.previa = None
          self.proximas_pecas = []

     def iniciar_jogo(self):
          # Pecas
          self.proximas_pecas = [choice(list(TETROMINOS.keys())) for peca in range(3)]
          
          # componentes
          self.jogo = Jogo(self.get_proximas_pecas, self.atualiza_pontos) 
          self.pontuacao = Pontuacao()
          self.previa = Previa()
          self.estado = 'jogando'

     def atualiza_pontos(self, linhas, pontos, level):
          if self.pontuacao:
               self.pontuacao.linhas = linhas
               self.pontuacao.pontos = pontos
               self.pontuacao.level = level

     def executar(self):
          while True:
               # Esta sessão serve para finalizar o programa, sem ela a janela do jogo rodaria sem parar.
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         pygame.quit()
                         exit()

                    if self.estado == 'menu':
                         self.tela_inicial.tratar_evento(event)
                    elif self.estado == 'jogando':
                         if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                              self.estado = 'menu'
               
               # Exibição
               self.exibir_superficie.fill(CINZA)
             
               # Componentes conforme o estado atual
               if self.estado == 'menu':
                    self.tela_inicial.desenhar()
               elif self.estado == 'jogando':
                    self.jogo.executar()
                    self.pontuacao.executar()
                    self.previa.executar(self.proximas_pecas)
               
               # Atualizando o jogo
               # Atualiza tudo que vemos dentro do jogo, assim podemos ver a janela do jogo
               pygame.display.update()
               '''clock' é um objeto que permite controlar os quadros (frames) do jogo, por exemplo:
                  Se quisermos que o jogo rode a 60fps apenas faça: self.relogio.tick(60).
                  Caso não haja argumentos, o jogo rodará com a quantidade máxima de quadros por segundo
               '''
               self.relogio.tick()

     def get_proximas_pecas(self):
          proxima_peca = self.proximas_pecas.pop(0)
          self.proximas_pecas.append(choice(list(TETROMINOS.keys())))
          return proxima_peca

if __name__ == '__main__':
     main = Main()
     main.executar()    