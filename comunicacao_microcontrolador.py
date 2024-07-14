import json

class ComunicacaoMicrocontrolador:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def ligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")
            print("Mensagem 'ligar_valvula' enviada com sucesso.")
        except Exception as e:
            print(f"Erro ao enviar mensagem 'ligar_valvula': {e}")

    def desligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")
            print("Mensagem 'desligar_valvula' enviada com sucesso.")
        except Exception as e:
            print(f"Erro ao enviar mensagem 'desligar_valvula': {e}")

    def atualizar_dados_ambientais(self, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        try:
            dados = {
                'fase_desenvolvimento': fase_desenvolvimento,
                'textura_solo': textura_solo,
                'evapotranspiracao': evapotranspiracao,
                'precipitacao': precipitacao
            }
            mensagem = json.dumps(dados)
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", mensagem)
            print("Dados ambientais atualizados enviados ao microcontrolador.")
        except Exception as e:
            print(f"Erro ao enviar dados ambientais atualizados: {e}")
