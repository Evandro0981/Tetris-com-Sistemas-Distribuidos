import pygame

TEXTO_COMO_JOGAR = '''
Para o multiplayer:
Um computador deve ser escolhido pra deixar o servidor do jogo rodando.
Cada jogador deve estar na mesma rede desse computador,
e colocar o IP dele na tela inicial do jogo (ex: 10.3.1.17)
4 jogadores devem estar numa partida para o jogo começar.
Terão 2 duplas de jogadores, onde em cada uma:
- Um jogador vai controlar o movimento dos blocos
- Um jogador vai controlar o giro dos blocos

No jogo:
Pressione as setas Direita e Esquerda pra mover os blocos para os lados
Pressione a seta para Cima para girar os blocos
Pressione a seta para Baixo para fazer o bloco cair mais rápido
'''

class TelaInicial:
    def __init__(self, superficie, ao_iniciar):
        self.superficie = superficie
        self.ao_iniciar = ao_iniciar
        self.fonte = pygame.font.Font(None, 28)
        self.fonte_instrucoes = pygame.font.Font(None, 24)
        
        # Estado para alternar entre a tela inicial e a tela de ajuda
        self.mostrar_como_jogar = False
        
        # Prepara as linhas de texto para renderização
        self.linhas_texto = [linha for linha in TEXTO_COMO_JOGAR.strip().split("\n")]
        largura_campo = 240
        altura_campo = 40
        pos_x = (self.superficie.get_width() - largura_campo) // 2

        # Campo de IP do Servidor
        self.ip_servidor = "127.0.0.1"
        self.input_ativo = False
        self.rect_input = pygame.Rect(pos_x, 280, largura_campo, altura_campo)

        # Botão CONECTAR
        self.rect_botao_conectar = pygame.Rect(pos_x, 340, largura_campo, altura_campo)

        # Botão INICIAR
        self.rect_botao_iniciar = pygame.Rect(pos_x, 420, largura_campo, 50)

        # Botão COMO JOGAR
        self.rect_botao_como_jogar = pygame.Rect(pos_x, 490, largura_campo, 50)

        # Botão VOLTAR
        self.rect_botao_voltar = pygame.Rect(pos_x, 760, largura_campo, 50)

    def conectar(self):
        '''
        TODO: Aqui vai ficar a lógica pra conectar o cliente com o servidor
        '''
        print(f"IP inserido: {self.ip_servidor}")

    def tratar_evento(self, evento):
        # Se estiver na tela de Como Jogar
        if self.mostrar_como_jogar:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Clique no botão Voltar
                if self.rect_botao_voltar.collidepoint(evento.pos):
                    self.mostrar_como_jogar = False
            elif evento.type == pygame.KEYDOWN:
                # Tecla ESC também volta para o menu
                if evento.key == pygame.K_ESCAPE:
                    self.mostrar_como_jogar = False
            return
        # Se estiver na tela inicial padrão
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Clique no campo de IP
            if self.rect_input.collidepoint(evento.pos):
                self.input_ativo = True
            else:
                self.input_ativo = False
            # Clique no botão Conectar
            if self.rect_botao_conectar.collidepoint(evento.pos):
                self.conectar()
            # Clique no botão Iniciar
            if self.rect_botao_iniciar.collidepoint(evento.pos):
                self.ao_iniciar()
            # Clique no botão Como Jogar
            if self.rect_botao_como_jogar.collidepoint(evento.pos):
                self.mostrar_como_jogar = True
        elif evento.type == pygame.KEYDOWN and self.input_ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.ip_servidor = self.ip_servidor[:-1]
            elif evento.key == pygame.K_RETURN:
                self.conectar()
            else:
                if len(self.ip_servidor) < 25 and evento.unicode.isprintable():
                    self.ip_servidor += evento.unicode

    def desenhar(self):
        # Desenho da tela de Como Jogar
        if self.mostrar_como_jogar:
            # Título
            fonte_titulo = pygame.font.Font(None, 38)
            titulo = fonte_titulo.render("COMO JOGAR", True, (255, 255, 255))
            rect_titulo = titulo.get_rect(center=(self.superficie.get_width() // 2, 220))
            self.superficie.blit(titulo, rect_titulo)
            # Exibe cada linha do texto centralizada
            # Exibe cada linha do texto alinhada à esquerda
            margem_esquerda = 60  # Distância em pixels da borda esquerda (ajuste como preferir)
            y_texto = 300

            for linha in self.linhas_texto:
                texto_renderizado = self.fonte_instrucoes.render(linha, True, (220, 220, 220))
                self.superficie.blit(texto_renderizado, (margem_esquerda, y_texto))
                y_texto += 35
            # Botão VOLTAR
            pygame.draw.rect(self.superficie, (60, 60, 60), self.rect_botao_voltar)
            pygame.draw.rect(self.superficie, (255, 255, 255), self.rect_botao_voltar, 2)
            texto_voltar = self.fonte.render("VOLTAR", True, (255, 255, 255))
            rect_texto_voltar = texto_voltar.get_rect(center=self.rect_botao_voltar.center)
            self.superficie.blit(texto_voltar, rect_texto_voltar)
            return
        # --- Desenho normal da tela inicial ---
        # Label IP do Servidor
        texto_label = self.fonte.render("IP do Servidor:", True, (255, 255, 255))
        self.superficie.blit(texto_label, (self.rect_input.x, self.rect_input.y - 25))
        # Campo de entrada do IP
        cor_input = (200, 200, 200) if self.input_ativo else (100, 100, 100)
        pygame.draw.rect(self.superficie, cor_input, self.rect_input, 2)
        texto_ip = self.fonte.render(self.ip_servidor, True, (255, 255, 255))
        self.superficie.blit(texto_ip, (self.rect_input.x + 8, self.rect_input.y + 10))
        # Botão CONECTAR
        pygame.draw.rect(self.superficie, (60, 60, 60), self.rect_botao_conectar)
        pygame.draw.rect(self.superficie, (255, 255, 255), self.rect_botao_conectar, 2)
        texto_conectar = self.fonte.render("CONECTAR", True, (255, 255, 255))
        rect_texto_conectar = texto_conectar.get_rect(center=self.rect_botao_conectar.center)
        self.superficie.blit(texto_conectar, rect_texto_conectar)
        # Botão INICIAR
        pygame.draw.rect(self.superficie, (60, 60, 60), self.rect_botao_iniciar)
        pygame.draw.rect(self.superficie, (255, 255, 255), self.rect_botao_iniciar, 2)
        texto_iniciar = self.fonte.render("INICIAR", True, (255, 255, 255))
        rect_texto_iniciar = texto_iniciar.get_rect(center=self.rect_botao_iniciar.center)
        self.superficie.blit(texto_iniciar, rect_texto_iniciar)
        # Botão COMO JOGAR
        pygame.draw.rect(self.superficie, (60, 60, 60), self.rect_botao_como_jogar)
        pygame.draw.rect(self.superficie, (255, 255, 255), self.rect_botao_como_jogar, 2)
        texto_como_jogar = self.fonte.render("COMO JOGAR", True, (255, 255, 255))
        rect_texto_como_jogar = texto_como_jogar.get_rect(center=self.rect_botao_como_jogar.center)
        self.superficie.blit(texto_como_jogar, rect_texto_como_jogar)

