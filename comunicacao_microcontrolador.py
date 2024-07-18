import json

class ComunicacaoMicrocontrolador:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao
        self.volume_total = 0.0

    def ligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")
            print("Mensagem 'ligar_valvula' enviada com sucesso.")
            self.comunicacao.mensagens_status.put("Válvula ligada")
        except Exception as e:
            print(f"Erro ao enviar mensagem 'ligar_valvula': {e}")

    def desligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")
            print("Mensagem 'desligar_valvula' enviada com sucesso.")
            self.comunicacao.mensagens_status.put(f"{self.volume_total:.2f} litros")
            self.comunicacao.mensagens_status.put("Válvula desligada")
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

    def processar_mensagem_volume(self, mensagem):
        try:
            dados = json.loads(mensagem)
            if 'volume_total' in dados:
                self.volume_total = float(dados['volume_total'])
                print(f"Volume total atualizado: {self.volume_total} litros")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar mensagem: {mensagem}")
