import socket
import threading
import json


class ClienteRede:
    def __init__(self):
        self.cliente = None
        self.papel = None
        self.id = None
        self.mensagens = []
        self.conectado = False
        self.buffer = ""
        self.trava_mensagens = threading.Lock()
        self.trava_envio = threading.Lock()

    def conectar(self, ip, porta=5555):
        if self.conectado:
            return True
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cliente.connect((ip, porta))
            # Sem o atraso do algoritmo de Nagle: ações chegam na hora
            self.cliente.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.conectado = True

            thread = threading.Thread(target=self.ouvir_servidor, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"Erro de conexão: {e}")
            return False

    def ouvir_servidor(self):
        while self.conectado:
            try:
                dados = self.cliente.recv(8192).decode('utf-8')
                if not dados:
                    self.conectado = False
                    break

                self.buffer += dados
                while '\n' in self.buffer:
                    linha, self.buffer = self.buffer.split('\n', 1)
                    linha = linha.strip()
                    if not linha:
                        continue
                    try:
                        msg = json.loads(linha)
                    except json.JSONDecodeError as err:
                        print(f"Aviso de parsing JSON (ignorado): {err}")
                        continue

                    if msg.get("tipo") == "INICIAR_JOGO":
                        self.papel = msg.get("papel")
                        self.id = msg.get("id")

                    with self.trava_mensagens:
                        self.mensagens.append(msg)
            except Exception as e:
                print(f"Erro na recepção: {e}")
                self.conectado = False
                break

    def coletar_mensagens(self):
        """Entrega todas as mensagens pendentes de uma vez, na ordem de chegada."""
        with self.trava_mensagens:
            pendentes, self.mensagens = self.mensagens, []
        return pendentes

    def enviar(self, dados):
        if self.conectado:
            try:
                mensagem = json.dumps(dados) + '\n'
                with self.trava_envio:
                    self.cliente.sendall(mensagem.encode('utf-8'))
            except Exception as e:
                print(f"Erro ao enviar: {e}")