import pygame

class TelaInicial:
    def __init__(self, superficie, ao_iniciar):
        self.superficie = superficie
        self.ao_iniciar = ao_iniciar
        self.fonte = pygame.font.Font(None, 28)

        # Campo de IP do Servidor
        self.ip_servidor = "127.0.0.1"
        self.input_ativo = False
        largura_campo = 240
        altura_campo = 40
        pos_x = (self.superficie.get_width() - largura_campo) // 2

        self.rect_input = pygame.Rect(pos_x, 280, largura_campo, altura_campo)

        # Botão CONECTAR
        self.rect_botao_conectar = pygame.Rect(pos_x, 340, largura_campo, altura_campo)

        # Botão INICIAR
        self.rect_botao_iniciar = pygame.Rect(pos_x, 420, largura_campo, 50)

    def conectar(self):
        '''
        TODO: Aqui vai ficar a lógica pra conectar o cliente com o servidor
        '''
        print(f"IP inserido: {self.ip_servidor}")

    def tratar_evento(self, evento):
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

        elif evento.type == pygame.KEYDOWN and self.input_ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.ip_servidor = self.ip_servidor[:-1]
            elif evento.key == pygame.K_RETURN:
                self.conectar()
            else:
                # Aceita caracteres digitáveis para o IP (máximo de 25 caracteres)
                if len(self.ip_servidor) < 25 and evento.unicode.isprintable():
                    self.ip_servidor += evento.unicode

    def desenhar(self):
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

