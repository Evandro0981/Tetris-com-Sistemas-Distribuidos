import pygame

class Temporizador:
     def __init__(self, duracao, repetitivo = False, func = None):
          self.repetitivo = repetitivo
          self.func = func
          self.duracao = duracao
          
          self.tempo_inicial = 0
          self.ativo = False
          
     def ativar(self):
          self.ativo = True
          self.tempo_inicial = pygame.time.get_ticks()
     
     def desativar(self):
          self.ativo = False
          self.tempo_inicial = 0
     
     def atualizar(self):
          tempo_atual = pygame.time.get_ticks()
          if tempo_atual - self.tempo_inicial >= self.duracao and self.ativo:
               
               if self.func and self.tempo_inicial != 0:
                    self.func()
               
               self.desativar()
               
               if self.repetitivo:
                    self.ativar()
               