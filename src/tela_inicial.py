import pygame
import math
from os import path
from configuracao import (
    COR_FUNDO, COR_SECUNDARIA_FUNDO, BRANCO, CINZA_BOTAO, CINZA_HOVER, COR_RELEVO,
    DOURADO, VERMELHO, VERDE, AMARELO, LINHA_COR
)

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
    def __init__(self, superficie, ao_iniciar, rede):
        self.superficie = superficie
        self.ao_iniciar = ao_iniciar
        self.rede = rede
        self.status_conexao = ""

        # Fontes do jogo
        caminhos_fonte = [
            path.join('graficos', 'Russo_One.ttf'),
            path.join('src', 'graficos', 'Russo_One.ttf'),
            path.join(path.dirname(__file__), 'graficos', 'Russo_One.ttf'),
            path.join(path.dirname(__file__), '..', 'graficos', 'Russo_One.ttf'),
        ]
        caminho_fonte = next((p for p in caminhos_fonte if path.exists(p)), None)

        if caminho_fonte:
            self.fonte_botoes = pygame.font.Font(caminho_fonte, 20)
            self.fonte_rotulo = pygame.font.Font(caminho_fonte, 16)
            self.fonte_input = pygame.font.Font(caminho_fonte, 20)
            self.fonte_titulo = pygame.font.Font(caminho_fonte, 32)
            self.fonte_status = pygame.font.Font(caminho_fonte, 16)
            self.fonte_subtitulo = pygame.font.Font(caminho_fonte, 12)
        else:
            self.fonte_botoes = pygame.font.Font(None, 26)
            self.fonte_rotulo = pygame.font.Font(None, 22)
            self.fonte_input = pygame.font.Font(None, 26)
            self.fonte_titulo = pygame.font.Font(None, 40)
            self.fonte_status = pygame.font.Font(None, 22)
            self.fonte_subtitulo = pygame.font.Font(None, 16)

        self.fonte = self.fonte_botoes
        self.fonte_instrucoes = pygame.font.Font(None, 24)

        # Carregar Logo
        caminhos_logo = [
            path.join('img', 'logo.png'),
            path.join('src', 'img', 'logo.png'),
            path.join(path.dirname(__file__), 'img', 'logo.png'),
            path.join(path.dirname(__file__), '..', 'img', 'logo.png'),
        ]
        caminho_logo = next((p for p in caminhos_logo if path.exists(p)), None)
        self.logo = None
        if caminho_logo:
            try:
                img_logo = pygame.image.load(caminho_logo)
                largura_logo = 640
                altura_logo = int(largura_logo * img_logo.get_height() / img_logo.get_width())
                self.logo = pygame.transform.smoothscale(img_logo, (largura_logo, altura_logo))
            except Exception as e:
                print(f"Erro ao carregar imagem da logo: {e}")

        self.mostrar_como_jogar = False
        self.linhas_texto = [linha for linha in TEXTO_COMO_JOGAR.strip().split("\n")]

        largura_tela = self.superficie.get_width()
        altura_tela = self.superficie.get_height()
        centro_x = largura_tela // 2

        # Dimensões e posicionamento dos botões (1 VERSUS 1, 2 VERSUS 2, COMO JOGAR)
        largura_botao = 250
        altura_botao = 52
        espaco_botoes = 40
        total_largura_botoes = (largura_botao * 3) + (espaco_botoes * 2)
        x_inicial = (largura_tela - total_largura_botoes) // 2
        y_botoes = 430

        self.rect_botao_1v1 = pygame.Rect(x_inicial, y_botoes, largura_botao, altura_botao)
        self.rect_botao_2v2 = pygame.Rect(x_inicial + largura_botao + espaco_botoes, y_botoes, largura_botao, altura_botao)
        self.rect_botao_como_jogar = pygame.Rect(x_inicial + 2 * (largura_botao + espaco_botoes), y_botoes, largura_botao, altura_botao)

        # Aliases para manter compatibilidade total
        self.rect_botao_iniciar = self.rect_botao_1v1
        self.rect_botao_conectar = self.rect_botao_2v2

        # Subtítulos dos botões
        self.subtitulos = {
            '1v1': "WASD vs Setas no mesmo computador",
            '2v2': "4 computadores se conectam a 1 servidor",
            'como_jogar': "Controles e Instruções pro 2 versus 2"
        }

        # Campo de IP do Servidor (abaixo do botão 2 VERSUS 2 e seu subtítulo)
        largura_input = 250
        altura_input = 48
        self.ip_servidor = "127.0.0.1"
        self.input_ativo = False
        self.y_label_ip = y_botoes + altura_botao + 46
        self.rect_input = pygame.Rect(centro_x - (largura_input // 2), self.y_label_ip + 22, largura_input, altura_input)

        # Elementos da tela COMO JOGAR
        largura_card = 820
        altura_card = 640
        self.rect_card_como_jogar = pygame.Rect(
            (largura_tela - largura_card) // 2,
            (altura_tela - altura_card) // 2,
            largura_card,
            altura_card
        )
        self.rect_botao_voltar = pygame.Rect(centro_x - 110, self.rect_card_como_jogar.bottom - 75, 220, 48)

    def conectar(self):
        sucesso = self.rede.conectar(self.ip_servidor)
        if sucesso:
            self.status_conexao = "Conectado! Aguardando jogadores..."
        else:
            self.status_conexao = "Erro ao conectar. Verifique o IP."

    def tratar_evento(self, evento):
        if self.mostrar_como_jogar:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.rect_botao_voltar.collidepoint(evento.pos) or not self.rect_card_como_jogar.collidepoint(evento.pos):
                    self.mostrar_como_jogar = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.mostrar_como_jogar = False
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_input.collidepoint(evento.pos):
                self.input_ativo = True
            else:
                self.input_ativo = False

            if self.rect_botao_2v2.collidepoint(evento.pos):
                self.conectar()
            elif self.rect_botao_1v1.collidepoint(evento.pos):
                if self.rede.conectado:
                    # Conectado: quem inicia a partida é o servidor, quando houver 4 jogadores
                    self.status_conexao = "Aguardando os 4 jogadores..."
                else:
                    try:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        pass
                    self.ao_iniciar()
            elif self.rect_botao_como_jogar.collidepoint(evento.pos):
                self.mostrar_como_jogar = True

        elif evento.type == pygame.KEYDOWN and self.input_ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.ip_servidor = self.ip_servidor[:-1]
            elif evento.key == pygame.K_RETURN:
                self.conectar()
            else:
                if len(self.ip_servidor) < 25 and evento.unicode.isprintable():
                    self.ip_servidor += evento.unicode

    def desenhar_botao_3d(self, rect, texto, ativo=True):
        pos_mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos_mouse) and ativo
        pressionado = hover and pygame.mouse.get_pressed()[0]

        deslocamento = 3 if pressionado else 0
        profundidade = 5

        cor_fundo = CINZA_HOVER if hover else CINZA_BOTAO
        cor_texto = BRANCO if ativo else (150, 150, 150)

        # 1. Relevo 3D na parte de baixo (#c2bfff)
        rect_relevo = pygame.Rect(rect.x, rect.y + profundidade, rect.width, rect.height)
        pygame.draw.rect(self.superficie, COR_RELEVO, rect_relevo, border_radius=6)

        # 2. Face do botão com borda branca
        rect_face = pygame.Rect(rect.x, rect.y + deslocamento, rect.width, rect.height)
        pygame.draw.rect(self.superficie, cor_fundo, rect_face, border_radius=6)
        pygame.draw.rect(self.superficie, BRANCO, rect_face, width=2, border_radius=6)

        # 3. Texto centralizado
        texto_surf = self.fonte_botoes.render(texto, True, cor_texto)
        self.superficie.blit(texto_surf, texto_surf.get_rect(center=rect_face.center))

        return hover

    def desenhar_input_3d(self):
        pos_mouse = pygame.mouse.get_pos()
        hover = self.rect_input.collidepoint(pos_mouse)

        profundidade = 4

        # 1. Relevo 3D debaixo da borda branca (#c2bfff)
        rect_relevo = pygame.Rect(self.rect_input.x, self.rect_input.y + profundidade, self.rect_input.width, self.rect_input.height)
        pygame.draw.rect(self.superficie, COR_RELEVO, rect_relevo, border_radius=4)

        # 2. Face do campo de input com borda branca
        pygame.draw.rect(self.superficie, CINZA_BOTAO, self.rect_input, border_radius=4)
        pygame.draw.rect(self.superficie, BRANCO, self.rect_input, width=2, border_radius=4)

        # 3. Texto do IP centralizado
        surf_ip = self.fonte_input.render(self.ip_servidor, True, BRANCO)
        rect_ip = surf_ip.get_rect(center=self.rect_input.center)
        self.superficie.blit(surf_ip, rect_ip)

        # Cursor piscando sem deslocar o texto
        if self.input_ativo and (pygame.time.get_ticks() // 500) % 2 == 0:
            surf_cursor = self.fonte_input.render("|", True, BRANCO)
            self.superficie.blit(surf_cursor, (rect_ip.right + 2, rect_ip.y))

        return hover

    def desenhar(self):
        largura_tela = self.superficie.get_width()
        altura_tela = self.superficie.get_height()
        centro_x = largura_tela // 2

        if self.mostrar_como_jogar:
            # Relevo do card
            relevo_card = pygame.Rect(
                self.rect_card_como_jogar.x,
                self.rect_card_como_jogar.y + 6,
                self.rect_card_como_jogar.width,
                self.rect_card_como_jogar.height
            )
            pygame.draw.rect(self.superficie, COR_RELEVO, relevo_card, border_radius=8)
            pygame.draw.rect(self.superficie, CINZA_BOTAO, self.rect_card_como_jogar, border_radius=8)
            pygame.draw.rect(self.superficie, BRANCO, self.rect_card_como_jogar, width=2, border_radius=8)

            # Título
            titulo = self.fonte_titulo.render("COMO JOGAR", True, BRANCO)
            self.superficie.blit(titulo, titulo.get_rect(center=(self.rect_card_como_jogar.centerx, self.rect_card_como_jogar.y + 45)))

            # Linhas de texto
            y_texto = self.rect_card_como_jogar.y + 95
            for linha in self.linhas_texto:
                cor = DOURADO if (linha.startswith("Para") or linha.startswith("No jogo")) else LINHA_COR
                texto_renderizado = self.fonte_instrucoes.render(linha, True, cor)
                self.superficie.blit(texto_renderizado, (self.rect_card_como_jogar.x + 50, y_texto))
                y_texto += 26

            # Botão Voltar
            hover_voltar = self.desenhar_botao_3d(self.rect_botao_voltar, "VOLTAR")

            try:
                if hover_voltar:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass
            return

        # --- Tela Inicial Padrão ---
        # 1. Logo no meio da tela com leve flutuação suave
        if self.logo:
            tempo = pygame.time.get_ticks() / 1000.0
            flutuacao = math.sin(tempo * 2.0) * 5.0
            rect_logo = self.logo.get_rect(center=(centro_x, int(215 + flutuacao)))
            self.superficie.blit(self.logo, rect_logo)
        else:
            titulo = self.fonte_titulo.render("TETRA-LINK", True, BRANCO)
            self.superficie.blit(titulo, titulo.get_rect(center=(centro_x, 215)))

        # 2. Botões horizontais: 1 VERSUS 1 | 2 VERSUS 2 | COMO JOGAR
        hover_1v1 = self.desenhar_botao_3d(self.rect_botao_1v1, "1 VERSUS 1")
        hover_2v2 = self.desenhar_botao_3d(self.rect_botao_2v2, "2 VERSUS 2")
        hover_como_jogar = self.desenhar_botao_3d(self.rect_botao_como_jogar, "COMO JOGAR")

        # Subtítulos dos botões com a fonte Russo_One
        sub_1v1 = self.fonte_subtitulo.render(self.subtitulos['1v1'], True, LINHA_COR)
        self.superficie.blit(sub_1v1, sub_1v1.get_rect(center=(self.rect_botao_1v1.centerx, self.rect_botao_1v1.bottom + 14)))

        sub_2v2 = self.fonte_subtitulo.render(self.subtitulos['2v2'], True, LINHA_COR)
        self.superficie.blit(sub_2v2, sub_2v2.get_rect(center=(self.rect_botao_2v2.centerx, self.rect_botao_2v2.bottom + 14)))

        sub_como = self.fonte_subtitulo.render(self.subtitulos['como_jogar'], True, LINHA_COR)
        self.superficie.blit(sub_como, sub_como.get_rect(center=(self.rect_botao_como_jogar.centerx, self.rect_botao_como_jogar.bottom + 14)))

        # 3. Rótulo "IP DO SERVIDOR:"
        texto_label = self.fonte_rotulo.render("IP DO SERVIDOR:", True, BRANCO)
        rect_label = texto_label.get_rect(center=(self.rect_input.centerx, self.y_label_ip))
        self.superficie.blit(texto_label, rect_label)

        # 4. Campo de Input 3D
        hover_input = self.desenhar_input_3d()

        # 5. Status da Conexão
        if self.status_conexao:
            if "Erro" in self.status_conexao:
                cor_status = VERMELHO
            elif "Conectado" in self.status_conexao:
                cor_status = VERDE
            else:
                cor_status = AMARELO
            texto_status = self.fonte_status.render(self.status_conexao, True, cor_status)
            rect_status = texto_status.get_rect(center=(self.rect_input.centerx, self.rect_input.bottom + 25))
            self.superficie.blit(texto_status, rect_status)

        # 6. Atualização do cursor do mouse
        try:
            if hover_1v1 or hover_2v2 or hover_como_jogar:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif hover_input:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass
