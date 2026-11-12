import pygame
from configuracao import CINZA, DOURADO, BRANCO, CINZA_BOTAO, CINZA_HOVER


class TelaFimDeJogo:
    def __init__(self, superficie, ao_revanche, ao_voltar_inicio):
        self.superficie = superficie
        self.ao_revanche = ao_revanche
        self.ao_voltar_inicio = ao_voltar_inicio

        self.fonte_titulo = pygame.font.Font(None, 64)
        self.fonte_vencedor = pygame.font.Font(None, 44)
        self.fonte_equipe = pygame.font.Font(None, 32)
        self.fonte_pontos = pygame.font.Font(None, 56)
        self.fonte = pygame.font.Font(None, 28)

        self.pontos = {'Equipe 1': 0, 'Equipe 2': 0}
        self.vencedor = None

        # Estado de espera da revanche
        self.aguardando_revanche = False
        # Trava o botão de revanche de um jogador específico
        self.ja_cliquei_revanche = False
        self.texto_espera = ""

        largura = self.superficie.get_width()
        largura_botao = 240
        pos_x = (largura - largura_botao) // 2
        self.rect_botao_revanche = pygame.Rect(pos_x, 560, largura_botao, 50)
        self.rect_botao_voltar = pygame.Rect(pos_x, 630, largura_botao, 50)

        largura_cartao, altura_cartao, espaco = 260, 200, 40
        x_inicial = (largura - (largura_cartao * 2 + espaco)) // 2
        self.rects_cartoes = {
            'Equipe 1': pygame.Rect(x_inicial, 270, largura_cartao, altura_cartao),
            'Equipe 2': pygame.Rect(x_inicial + largura_cartao + espaco, 270, largura_cartao, altura_cartao),
        }

    # ------------------------------------------------------------------
    # Chamado pelo Main quando chega RESULTADO_FINAL do servidor
    # ------------------------------------------------------------------
    def definir_resultado(self, pontos_equipe_1, pontos_equipe_2):
        self.pontos = {'Equipe 1': pontos_equipe_1, 'Equipe 2': pontos_equipe_2}
        if pontos_equipe_1 > pontos_equipe_2:
            self.vencedor = 'Equipe 1'
        elif pontos_equipe_2 > pontos_equipe_1:
            self.vencedor = 'Equipe 2'
        else:
            self.vencedor = None
        self.aguardando_revanche = False
        # Trava o botão de revanche de um jogador específico
        self.ja_cliquei_revanche = False
        self.texto_espera = ""

    # ------------------------------------------------------------------
    # Chamado pelo Main quando o servidor avisa que alguém clicou revanche
    # ------------------------------------------------------------------
    def definir_espera_revanche(self, quantidade_confirmados, total):
        # self.aguardando_revanche = True
        self.texto_espera = f"Aguardando jogadores... ({quantidade_confirmados}/{total})"

    def marcar_revanche_clicada(self):
        """Chamado só no cliente que clicou: trava o botão dele."""
        self.ja_cliquei_revanche = True

    def cancelar_espera_revanche(self):
        self.aguardando_revanche = False
        self.texto_espera = ""

    # ------------------------------------------------------------------
    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not self.ja_cliquei_revanche and self.rect_botao_revanche.collidepoint(evento.pos):
                self.ao_revanche()
            elif self.rect_botao_voltar.collidepoint(evento.pos):
                self.ao_voltar_inicio()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN and not self.ja_cliquei_revanche:
                self.ao_revanche()
            elif evento.key == pygame.K_ESCAPE:
                self.ao_voltar_inicio()

    def desenhar_texto_centralizado(self, texto, fonte, cor, centro):
        s = fonte.render(texto, True, cor)
        self.superficie.blit(s, s.get_rect(center=centro))

    def desenhar_botao(self, rect, texto, ativo=True):
        if not ativo:
            cor = (30, 30, 30)
            cor_texto = (120, 120, 120)
        else:
            cor = CINZA_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else CINZA_BOTAO
            cor_texto = BRANCO
        pygame.draw.rect(self.superficie, cor, rect)
        pygame.draw.rect(self.superficie, BRANCO, rect, 2)
        self.desenhar_texto_centralizado(texto, self.fonte, cor_texto, rect.center)

    def desenhar(self):
        centro_x = self.superficie.get_width() // 2

        self.desenhar_texto_centralizado('FIM DE JOGO', self.fonte_titulo, BRANCO, (centro_x, 150))
        if self.vencedor:
            self.desenhar_texto_centralizado(f'{self.vencedor} venceu!', self.fonte_vencedor, DOURADO, (centro_x, 215))
        else:
            self.desenhar_texto_centralizado('Empate!', self.fonte_vencedor, DOURADO, (centro_x, 215))

        for nome, rect in self.rects_cartoes.items():
            eh_vencedor = (nome == self.vencedor)
            pygame.draw.rect(self.superficie, CINZA, rect)
            pygame.draw.rect(self.superficie, DOURADO if eh_vencedor else BRANCO,
                             rect, 4 if eh_vencedor else 2, 2)
            self.desenhar_texto_centralizado(nome, self.fonte_equipe, BRANCO, (rect.centerx, rect.y + 45))
            self.desenhar_texto_centralizado(str(self.pontos[nome]), self.fonte_pontos,
                                             DOURADO if eh_vencedor else BRANCO, (rect.centerx, rect.y + 105))
            self.desenhar_texto_centralizado('pontos', self.fonte, (220, 220, 220), (rect.centerx, rect.y + 150))

        # Botão de revanche desabilitado SÓ se EU já cliquei
        self.desenhar_botao(self.rect_botao_revanche, 'REVANCHE',
                            ativo=not self.ja_cliquei_revanche)
        self.desenhar_botao(self.rect_botao_voltar, 'VOLTAR AO INÍCIO', ativo=True)

        # Contador visível para TODOS enquanto a espera estiver em andamento
        if self.texto_espera:
            s = self.fonte.render(self.texto_espera, True, (255, 255, 0))
            self.superficie.blit(s, s.get_rect(center=(centro_x, 720)))