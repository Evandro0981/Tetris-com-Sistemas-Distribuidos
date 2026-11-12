from configuracao import *
from temporizador import Temporizador
from os import path


class Jogo:
    def __init__(self, get_proxima_peca, atualiza_pontos, rede=None, offset_x=0, equipe='EQUIPE_1'):
        self.som_linha = pygame.mixer.Sound(path.join('audio', 'Tetris_clear_line.mp3'))
        self.som_linha.set_volume(0.5)

        self.offset_x = offset_x
        self.equipe = equipe
        self.rede = rede
        self.contador_pecas_fixadas = 0

        self.superficie = pygame.Surface((LARGURA_JOGO, ALTURA_JOGO))
        self.mostrar_superficie = pygame.display.get_surface()

        pos_x = ESPACAMENTO + self.offset_x
        self.retangulo = self.superficie.get_rect(topleft=(pos_x, ESPACAMENTO))
        self.sprites = pygame.sprite.Group()

        self.get_proxima_peca = get_proxima_peca
        self.atualiza_pontos = atualiza_pontos

        self.superficie_linha = self.superficie.copy()
        self.superficie_linha.fill((0, 255, 0))
        self.superficie_linha.set_colorkey((0, 255, 0))
        self.superficie_linha.set_alpha(120)

        self.fonte_fim = pygame.font.Font(None, 48)

        self.dados_campo = [[0 for x in range(COLUNAS)] for y in range(LINHAS)]

        self.velocidade_descida = VELOCIDADE_ATUALIZACAO_INICIAL
        self.descer_peca_rapida = self.velocidade_descida * 0.3
        self.pressionada_tecla_descer = False

        self.level_atual = 1
        self.pontos_atuais = 0
        self.linha_atual = 0
        self.fim_de_jogo = False

        # A PRIMEIRA peça vem da lista sincronizada (antes era um choice() aleatório local)
        self.tetromino = self.criar_peca(self.get_proxima_peca())

        self.temporizadores = {
            'movimento vertical': Temporizador(self.velocidade_descida, True, self.gravidade_ou_descer),
            'movimento horizontal': Temporizador(TEMPO_ESPERA_MOVER),
            'rotacao': Temporizador(TEMPO_ESPERA_ROTACIONAR)
        }
        self.temporizadores['movimento vertical'].ativar()

    # ------------------------------------------------------------------
    # Rede / autoridade
    # ------------------------------------------------------------------
    def em_rede(self):
        return bool(self.rede and self.rede.conectado and self.rede.papel)

    def sou_autoridade(self):
        """Só o jogador de MOVIMENTO da equipe simula gravidade, linhas e pontos.
        Todos os outros clientes apenas aplicam o que ele envia."""
        if not self.em_rede():
            return True
        return self.rede.papel == f'{self.equipe}_MOVIMENTO'

    def enviar(self, dados):
        if self.em_rede():
            dados["equipe"] = self.equipe
            self.rede.enviar(dados)

    def criar_peca(self, forma):
        return Tetromino(forma, self.sprites, self.criar_novo_tetromino,
                         self.dados_campo, self.finalizar_jogo)

    # ------------------------------------------------------------------
    # Gravidade e fixação (somente autoridade)
    # ------------------------------------------------------------------
    def gravidade_ou_descer(self):
        if self.fim_de_jogo or not self.sou_autoridade():
            return

        resultado = self.tetromino.mover_pbaixo()
        if resultado == 'moveu':
            # Envia a posição exata da peça: corrige qualquer deriva nos outros clientes
            self.enviar({"tipo": "ACAO", "tecla": "DESCER", "blocos": self.tetromino.posicoes()})

    def criar_novo_tetromino(self):
        """Chamado (só na autoridade, ou no modo offline) quando a peça fixa."""
        self.checa_linha_completa()
        self.contador_pecas_fixadas += 1

        forma = self.get_proxima_peca()
        self.tetromino = self.criar_peca(forma)

        self.transmitir_grid_sync(forma)

    def transmitir_grid_sync(self, forma):
        if not self.em_rede() or not self.sou_autoridade():
            return

        grid_cores = [[(bloco.cor if bloco else None) for bloco in linha] for linha in self.dados_campo]

        # Uma única mensagem leva TUDO: tabuleiro, pontuação e a próxima peça
        self.enviar({
            "tipo": "GRID_SYNC",
            "id_peca": self.contador_pecas_fixadas,
            "grid": grid_cores,
            "forma": forma,
            "linhas": self.linha_atual,
            "pontos": self.pontos_atuais,
            "level": self.level_atual
        })

    def aplicar_grid_sync(self, msg):
        """Cliente não-autoridade: substitui o estado local pelo da autoridade."""
        for bloco in list(self.sprites):
            bloco.kill()
        self.limpar_campo()

        grid_cores = msg.get("grid") or []
        for y in range(min(LINHAS, len(grid_cores))):
            for x in range(min(COLUNAS, len(grid_cores[y]))):
                cor = grid_cores[y][x]
                if cor:
                    pos = pygame.Vector2(x, y) - DESLOCAMENTO_BLOCO
                    self.dados_campo[y][x] = Bloco(self.sprites, pos, cor)

        self.contador_pecas_fixadas = msg.get("id_peca", self.contador_pecas_fixadas)
        self.linha_atual = msg.get("linhas", self.linha_atual)
        self.pontos_atuais = msg.get("pontos", self.pontos_atuais)
        self.level_atual = msg.get("level", self.level_atual)
        self.atualiza_pontos(self.linha_atual, self.pontos_atuais, self.level_atual)

        # Nova peça = a mesma que a autoridade gerou; também avança a prévia local
        proxima = self.get_proxima_peca()
        self.tetromino = self.criar_peca(msg.get("forma") or proxima)

    def receber_mensagem(self, msg):
        """Mensagens já filtradas pelo Main para a equipe deste tabuleiro."""
        tipo = msg.get("tipo")

        if tipo == "ACAO":
            tecla = msg.get("tecla")
            if tecla == "ESQUERDA":
                self.tetromino.move_horizontal(-1)
            elif tecla == "DIREITA":
                self.tetromino.move_horizontal(1)
            elif tecla == "CIMA":
                self.tetromino.rotacao()
            elif tecla == "DESCER" and not self.sou_autoridade():
                blocos = msg.get("blocos")
                if blocos:
                    self.tetromino.definir_posicoes(blocos)

        elif tipo == "GRID_SYNC":
            if not self.sou_autoridade():
                self.aplicar_grid_sync(msg)

        elif tipo == "FIM_JOGO":
            self.finalizar_jogo(notificar=False)

    # ------------------------------------------------------------------
    # Linhas e pontos
    # ------------------------------------------------------------------
    def limpar_campo(self):
        # Modifica a matriz no lugar, para o Tetromino não ficar com referência velha
        for y in range(LINHAS):
            for x in range(COLUNAS):
                self.dados_campo[y][x] = 0

    def checa_linha_completa(self):
        linhas_para_apagar = [i for i, linha in enumerate(self.dados_campo) if all(linha)]
        if not linhas_para_apagar:
            return

        if self.som_linha.get_num_channels() == 0:
            self.som_linha.play()

        for apagar_linha in linhas_para_apagar:
            for bloco in self.dados_campo[apagar_linha]:
                if bloco:
                    bloco.kill()

            for linha in self.dados_campo:
                for bloco in linha:
                    if bloco and bloco.posicao.y < apagar_linha:
                        bloco.posicao.y += 1

        self.limpar_campo()
        for bloco in self.sprites:
            self.dados_campo[round(bloco.posicao.y)][round(bloco.posicao.x)] = bloco

        self.calcula_pontos(len(linhas_para_apagar))

    def calcula_pontos(self, numero_linhas):
        self.linha_atual += numero_linhas
        self.pontos_atuais += PONTOS_DADOS[numero_linhas] * self.level_atual

        if self.linha_atual / 3 > self.level_atual:
            self.level_atual += 1
            self.velocidade_descida *= 0.90
            self.descer_peca_rapida = self.velocidade_descida * 0.3
            self.temporizadores['movimento vertical'].duracao = self.velocidade_descida

        self.atualiza_pontos(self.linha_atual, self.pontos_atuais, self.level_atual)

    def finalizar_jogo(self, notificar=True):
        if self.fim_de_jogo:
            return
        self.fim_de_jogo = True
        self.temporizadores['movimento vertical'].desativar()
        if notificar and self.sou_autoridade():
            self.enviar({"tipo": "FIM_JOGO"})
            self.enviar({
                'tipo': 'FIM_JOGO_REPORT',
                'pontos': self.pontos_atuais
            })

    # ------------------------------------------------------------------
    # Loop, desenho e input
    # ------------------------------------------------------------------
    def atualizar_temporizador(self):
        for temporizador in self.temporizadores.values():
            temporizador.atualizar()

    def desenhar_grade(self):
        for coluna in range(1, COLUNAS):
            x = coluna * TAMANHO_CELULA
            pygame.draw.line(self.superficie_linha, LINHA_COR, (x, 0), (x, self.superficie.get_height()), 1)

        for linha in range(1, LINHAS):
            y = linha * TAMANHO_CELULA
            pygame.draw.line(self.superficie_linha, LINHA_COR, (0, y), (self.superficie.get_width(), y), 1)

        self.superficie.blit(self.superficie_linha, (0, 0))

    def executar(self):
        if not self.fim_de_jogo:
            self.input()
            self.atualizar_temporizador()
            self.sprites.update()

        self.superficie.fill(CINZA)
        self.sprites.draw(self.superficie)
        self.desenhar_grade()

        if self.fim_de_jogo:
            texto = self.fonte_fim.render('FIM DE JOGO', True, (255, 255, 255))
            self.superficie.blit(texto, texto.get_rect(center=(LARGURA_JOGO // 2, ALTURA_JOGO // 2)))

        pos_x = ESPACAMENTO + self.offset_x
        self.mostrar_superficie.blit(self.superficie, (pos_x, ESPACAMENTO))
        pygame.draw.rect(self.mostrar_superficie, LINHA_COR, self.retangulo, 2, 2)

    def input(self):
        movimento = pygame.key.get_pressed()
        papel = self.rede.papel if self.em_rede() else None

        if papel:
            # Só controla o tabuleiro da própria equipe
            if not papel.startswith(self.equipe):
                return
            pode_mover = 'MOVIMENTO' in papel
            pode_girar = 'ROTACAO' in papel

            press_left = movimento[pygame.K_LEFT] or movimento[pygame.K_a]
            press_right = movimento[pygame.K_RIGHT] or movimento[pygame.K_d]
            press_down = movimento[pygame.K_DOWN] or movimento[pygame.K_s]
            press_up = movimento[pygame.K_UP] or movimento[pygame.K_w]
        else:
            # Modo offline (2 jogadores no mesmo PC): Eq1 usa WASD, Eq2 usa Setas
            pode_mover = True
            pode_girar = True
            if self.equipe == 'EQUIPE_1':
                press_left, press_right, press_down, press_up = movimento[pygame.K_a], movimento[pygame.K_d], movimento[pygame.K_s], movimento[pygame.K_w]
            else:
                press_left, press_right, press_down, press_up = movimento[pygame.K_LEFT], movimento[pygame.K_RIGHT], movimento[pygame.K_DOWN], movimento[pygame.K_UP]

        if pode_mover and not self.temporizadores['movimento horizontal'].ativo:
            if press_left:
                self.tetromino.move_horizontal(-1)
                self.temporizadores['movimento horizontal'].ativar()
                self.enviar({"tipo": "ACAO", "tecla": "ESQUERDA"})

            if press_right:
                self.tetromino.move_horizontal(1)
                self.temporizadores['movimento horizontal'].ativar()
                self.enviar({"tipo": "ACAO", "tecla": "DIREITA"})

        # Aceleração manual (só o jogador de MOVIMENTO, que é quem roda a gravidade)
        if pode_mover:
            if not self.pressionada_tecla_descer and press_down:
                self.pressionada_tecla_descer = True
                self.temporizadores['movimento vertical'].duracao = self.descer_peca_rapida

            if self.pressionada_tecla_descer and not press_down:
                self.pressionada_tecla_descer = False
                self.temporizadores['movimento vertical'].duracao = self.velocidade_descida

        if pode_girar and not self.temporizadores['rotacao'].ativo:
            if press_up:
                self.tetromino.rotacao()
                self.temporizadores['rotacao'].ativar()
                self.enviar({"tipo": "ACAO", "tecla": "CIMA"})


class Tetromino:
    def __init__(self, forma, grupo, criar_novo_tetromino, dados_campo, finalizar_jogo):
        self.forma = forma
        self.posicoes_blocos = TETROMINOS[forma]['forma']
        self.cor = TETROMINOS[forma]['cor']
        self.criar_novo_tetromino = criar_novo_tetromino
        self.dados_campo = dados_campo
        self.finalizar_jogo = finalizar_jogo
        self.blocos = [Bloco(grupo, posicao, self.cor) for posicao in self.posicoes_blocos]

    def posicoes(self):
        return [[round(b.posicao.x), round(b.posicao.y)] for b in self.blocos]

    def definir_posicoes(self, lista):
        for bloco, (x, y) in zip(self.blocos, lista):
            bloco.posicao = pygame.Vector2(x, y)

    def proxima_colisao_horizontal(self, blocos, quantia):
        lista_colisoes = [bloco.colisao_horizontal(int(bloco.posicao.x + quantia), self.dados_campo) for bloco in self.blocos]
        return any(lista_colisoes)

    def proxima_colisao_vertical(self, blocos, quantia):
        lista_colisoes = [bloco.colisao_vertical(int(bloco.posicao.y + quantia), self.dados_campo) for bloco in self.blocos]
        return any(lista_colisoes)

    def move_horizontal(self, quantia):
        if not self.proxima_colisao_horizontal(self.blocos, quantia):
            for bloco in self.blocos:
                bloco.posicao.x += quantia

    def mover_pbaixo(self):
        """Retorna 'moveu', 'fixou' ou 'fim'."""
        if not self.proxima_colisao_vertical(self.blocos, 1):
            for bloco in self.blocos:
                bloco.posicao.y += 1
            return 'moveu'

        for bloco in self.blocos:
            if bloco.posicao.y <= 0:
                self.finalizar_jogo()
                return 'fim'
        for bloco in self.blocos:
            self.dados_campo[int(bloco.posicao.y)][int(bloco.posicao.x)] = bloco
        self.criar_novo_tetromino()
        return 'fixou'

    def rotacao(self):
        if self.forma != 'O':
            pivot_posicao = self.blocos[0].posicao
            nova_posicao_bloco = [bloco.rotacao(pivot_posicao) for bloco in self.blocos]

            for pos in nova_posicao_bloco:
                if pos.x < 0 or pos.x >= COLUNAS or pos.y >= LINHAS:
                    return
                if pos.y >= 0 and self.dados_campo[int(pos.y)][int(pos.x)]:
                    return

            for index, bloco in enumerate(self.blocos):
                bloco.posicao = nova_posicao_bloco[index]


class Bloco(pygame.sprite.Sprite):
    def __init__(self, grupo, posicao, cor):
        super().__init__(grupo)
        self.cor = cor
        self.image = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA))
        self.image.fill(cor)
        self.posicao = pygame.Vector2(posicao) + DESLOCAMENTO_BLOCO
        self.rect = self.image.get_rect(topleft=self.posicao * TAMANHO_CELULA)

    def rotacao(self, pivot_posicao):
        distance = self.posicao - pivot_posicao
        rodar = distance.rotate(90)
        nova_posicao = pivot_posicao + rodar
        # Arredonda: rotate() gera erros de ponto flutuante (ex: 2.9999999) que quebram o int()
        return pygame.Vector2(round(nova_posicao.x), round(nova_posicao.y))

    def colisao_horizontal(self, x, dados_campo):
        if not 0 <= x < COLUNAS:
            return True
        if self.posicao.y >= 0 and dados_campo[int(self.posicao.y)][x]:
            return True

    def colisao_vertical(self, y, dados_campo):
        if y >= LINHAS:
            return True
        if y >= 0 and dados_campo[y][int(self.posicao.x)]:
            return True

    def update(self):
        self.rect.topleft = self.posicao * TAMANHO_CELULA