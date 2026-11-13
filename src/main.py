from configuracao import *
from sys import exit
from random import choice
from os import path

# componentes
from jogo import Jogo
from pontuacao import Pontuacao
from previa import Previa
from tela_inicial import TelaInicial
from rede import ClienteRede
from tela_fim_de_jogo import TelaFimDeJogo
from feedback_texto import FeedbackTexto

OFFSET_EQ1 = 0
OFFSET_EQ2 = LARGURA_TABULEIRO_COMPLETO + ESPACAMENTO
NOMES_FUNCAO = {'MOVIMENTO': 'MOVIMENTO', 'ROTACAO': 'ROTAÇÃO'}

CENTRO_JOGO_EQ1 = (ESPACAMENTO + OFFSET_EQ1 + LARGURA_JOGO // 2, ESPACAMENTO + ALTURA_JOGO // 2)
CENTRO_JOGO_EQ2 = (ESPACAMENTO + OFFSET_EQ2 + LARGURA_JOGO // 2, ESPACAMENTO + ALTURA_JOGO // 2)

class Main:
    def __init__(self):
        pygame.init()

        # Feedback de texto
        self.feedback = FeedbackTexto()

        # musica de fundo
        pygame.mixer.init()
        caminho_musica = path.join('audio', 'Tetris_theme.mp3')
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        # Criando a superfície do jogo
        self.exibir_superficie = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        self.relogio = pygame.time.Clock()
        pygame.display.set_caption('Tetris - 2vs2 Co-op Multiplayer')
        self.fonte_status = pygame.font.Font(None, 26)

        # Conexão de Rede
        self.rede = ClienteRede()

        # Estado do jogo ('menu' ou 'jogando')
        self.estado = 'menu'
        self.tela_inicial = TelaInicial(self.exibir_superficie, self.iniciar_jogo, self.rede)
        self.tela_fim = TelaFimDeJogo(self.exibir_superficie, ao_revanche=self.pedir_revanche, ao_voltar_inicio=self.pedir_voltar_inicio)

        self._revanche_pedida = False

        # Equipe 1 (Esquerda)
        self.jogo1 = None
        self.pontuacao1 = None
        self.previa1 = None
        self.proximas_pecas1 = []

        # Equipe 2 (Direita)
        self.jogo2 = None
        self.pontuacao2 = None
        self.previa2 = None
        self.proximas_pecas2 = []

    def iniciar_jogo(self, pecas_eq1=None, pecas_eq2=None):
        if pecas_eq1 and pecas_eq2:
            self.proximas_pecas1 = list(pecas_eq1)
            self.proximas_pecas2 = list(pecas_eq2)
        else:
            self.proximas_pecas1 = [choice(list(TETROMINOS.keys())) for _ in range(5)]
            self.proximas_pecas2 = [choice(list(TETROMINOS.keys())) for _ in range(5)]

        self.feedback.limpar()

        # Instancia Equipe 1
        self.jogo1 = Jogo(self.get_proximas_pecas_1, self.atualiza_pontos_1, self.rede, offset_x=OFFSET_EQ1, equipe='EQUIPE_1')
        self.pontuacao1 = Pontuacao(offset_x=OFFSET_EQ1)
        self.previa1 = Previa(offset_x=OFFSET_EQ1)

        # Instancia Equipe 2
        self.jogo2 = Jogo(self.get_proximas_pecas_2, self.atualiza_pontos_2, self.rede, offset_x=OFFSET_EQ2, equipe='EQUIPE_2')
        self.pontuacao2 = Pontuacao(offset_x=OFFSET_EQ2)
        self.previa2 = Previa(offset_x=OFFSET_EQ2)

        self.estado = 'jogando'

    def atualiza_pontos_1(self, linhas, pontos, level):
        if self.pontuacao1:
            novas_linhas = linhas - self.pontuacao1.linhas
            if novas_linhas > 0:
                self.disparar_feedback_linhas(1, novas_linhas)
            self.pontuacao1.linhas = linhas
            self.pontuacao1.pontos = pontos
            self.pontuacao1.level = level

    def atualiza_pontos_2(self, linhas, pontos, level):
        if self.pontuacao2:
            novas_linhas = linhas - self.pontuacao2.linhas
            if novas_linhas > 0:
                self.disparar_feedback_linhas(2, novas_linhas)
            self.pontuacao2.linhas = linhas
            self.pontuacao2.pontos = pontos
            self.pontuacao2.level = level


    def _sacar_peca(self, lista):
        peca = lista.pop(0) if lista else choice(list(TETROMINOS.keys()))
        # Offline não há servidor para repor a fila, então repomos aqui
        if not self.rede.conectado:
            lista.append(choice(list(TETROMINOS.keys())))
        return peca

    def get_proximas_pecas_1(self):
        return self._sacar_peca(self.proximas_pecas1)

    def get_proximas_pecas_2(self):
        return self._sacar_peca(self.proximas_pecas2)

    def despachar_mensagem(self, msg):
        tipo = msg.get("tipo")

        if tipo == "RESULTADO_FINAL":
            self.tela_fim.definir_resultado(msg.get("pontos_eq1", 0), msg.get("pontos_eq2", 0))
            self.estado = 'fim_de_jogo'
            self._revanche_pedida = False
            return

        if tipo == "ESPERA_REVANCHE":
            self.tela_fim.definir_espera_revanche(msg.get("confirmados", 0), msg.get("total", 4))
            return

        if tipo == "VOLTAR_INICIO_FORCADO":
            self.voltar_ao_menu()
            return

        if tipo == "INICIAR_JOGO":
            self._revanche_pedida = False
            self.iniciar_jogo(pecas_eq1=msg.get("pecas_eq1"), pecas_eq2=msg.get("pecas_eq2"))
            return

        equipe = msg.get("equipe")

        if tipo == "NOVA_PECA":
            if equipe == "EQUIPE_1":
                self.proximas_pecas1.append(msg.get("peca"))
            elif equipe == "EQUIPE_2":
                self.proximas_pecas2.append(msg.get("peca"))
            return

        # ACAO / GRID_SYNC / FIM_JOGO vão para o tabuleiro da equipe correspondente
        jogo = {"EQUIPE_1": self.jogo1, "EQUIPE_2": self.jogo2}.get(equipe)
        if jogo:
            jogo.receber_mensagem(msg)

    def desenhar_cabecalhos(self):
        papel = self.rede.papel if (self.rede and self.rede.conectado) else None
        minha_equipe = None
        if papel:
            minha_equipe = 'EQUIPE_1' if papel.startswith('EQUIPE_1') else 'EQUIPE_2'

        largura_bloco = LARGURA_JOGO + ESPACAMENTO + LARGURA_BARRA_LATERAL

        # Títulos centralizados no topo de cada tabuleiro
        for equipe, offset in (('EQUIPE_1', OFFSET_EQ1), ('EQUIPE_2', OFFSET_EQ2)):
            numero = equipe[-1]
            if minha_equipe is None:
                texto, cor = f"EQUIPE {numero}", (255, 255, 255)
            elif equipe == minha_equipe:
                numero_minha_equipe = numero
                texto, cor = f"EQUIPE {numero} (SUA)", (0, 255, 255)
            else:
                texto, cor = f"EQUIPE {numero} (ADVERSÁRIA)", (255, 100, 100)

            surf = self.fonte_status.render(texto, True, cor)
            centro_x = ESPACAMENTO + offset + largura_bloco // 2
            self.exibir_superficie.blit(surf, surf.get_rect(center=(centro_x, ESPACAMENTO // 2)))

        # Função do jogador, na margem de baixo (antes ficava em cima, sobreposta aos títulos)
        if papel:
            funcao = NOMES_FUNCAO.get(papel.split('_')[-1], papel)
            texto_funcao = f"SUA FUNÇÃO: {funcao} DA EQUIPE {numero_minha_equipe}"
        else:
            texto_funcao = "MODO LOCAL  |  Equipe 1: WASD  -  Equipe 2: Setas"
        surf_status = self.fonte_status.render(texto_funcao, True, (255, 255, 0))
        self.exibir_superficie.blit(
            surf_status, surf_status.get_rect(center=(LARGURA_JANELA // 2, ALTURA_JANELA - ESPACAMENTO // 2)))

    def executar(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if self.estado == 'menu':
                    self.tela_inicial.tratar_evento(event)
                elif self.estado == 'jogando':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.estado = 'menu'
                elif self.estado == 'fim_de_jogo':
                    self.tela_fim.tratar_evento(event)

            # Esvazia a fila de rede uma vez por quadro e despacha na ordem de chegada
            for msg in self.rede.coletar_mensagens():
                self.despachar_mensagem(msg)

            self.exibir_superficie.fill(CINZA)

            # Detecta fim de jogo local (offline)
            if (self.estado == 'jogando' and not self.rede.conectado
                    and self.jogo1 and self.jogo2
                    and self.jogo1.fim_de_jogo and self.jogo2.fim_de_jogo):
                self.tela_fim.definir_resultado(self.jogo1.pontos_atuais, self.jogo2.pontos_atuais)
                self.estado = 'fim_de_jogo'
                self._revanche_pedida = False
                
            if self.estado == 'menu':
                self.tela_inicial.desenhar()
            elif self.estado == 'jogando':
                self.desenhar_cabecalhos()

                # Desenha Equipe 1 (Esquerda)
                self.jogo1.executar()
                self.pontuacao1.executar()
                self.previa1.executar(self.proximas_pecas1)

                # Desenha Equipe 2 (Direita)
                self.jogo2.executar()
                self.pontuacao2.executar()
                self.previa2.executar(self.proximas_pecas2) 
                # Desenha os feedbacks flutuantes por cima de ambos os tabuleiros
                self.feedback.executar(self.exibir_superficie)
            elif self.estado == 'fim_de_jogo':
                self.tela_fim.desenhar()

            pygame.display.update()
            self.relogio.tick(60)

    def pedir_revanche(self):
        if self._revanche_pedida:
            return
        if not self.rede.conectado:
            # Offline: reinicia direto
            self.iniciar_jogo()
            return
        self._revanche_pedida = True
        self.rede.enviar({"tipo": "PEDIR_REVANCHE", "id": self.rede.id})
        self.tela_fim.marcar_revanche_clicada()


    def pedir_voltar_inicio(self):
        if self.rede.conectado:
            self.rede.enviar({"tipo": "VOLTAR_INICIO", "id": self.rede.id})
        # Offline: volta direto
        self.voltar_ao_menu()


    def voltar_ao_menu(self):
        self.estado = 'menu'
        self._revanche_pedida = False
        self.tela_fim.cancelar_espera_revanche()
        self.jogo1 = None
        self.jogo2 = None
        self.pontuacao1 = None
        self.pontuacao2 = None
        self.previa1 = None
        self.previa2 = None
        self.feedback.limpar()

    def disparar_feedback_linhas(self, equipe_num, numero_linhas):
        mensagens = {
            1: ('LINHA COMPLETA!', AMARELO),
            2: ('LINHA DUPLA!', CIANO),
            3: ('LINHA TRIPLA!', LARANJA),
            4: ('TETRIS!', VERDE)
        }
        texto, cor = mensagens.get(numero_linhas, (f'+{numero_linhas} LINHAS!', AMARELO))
        posicao = CENTRO_JOGO_EQ1 if equipe_num == 1 else CENTRO_JOGO_EQ2
        self.feedback.criar_feedback(texto, posicao=posicao, cor=cor)

if __name__ == '__main__':
    main = Main()
    main.executar()
