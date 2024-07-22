import json

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        try:
            dados = {
                'ciclo_total': ciclo_total,
                'tempo_acionamento': self.formatar_tempo(tempo_acionamento),
                'intervalo': self.formatar_intervalo(intervalo),
                'fase_desenvolvimento': fase_desenvolvimento,
                'textura_solo': textura_solo,
                'evapotranspiracao': round(float(evapotranspiracao), 2),
                'precipitacao': round(float(precipitacao), 2)
            }
            mensagem = json.dumps(dados, indent=4)
            self.comunicacao.enviar_mensagem("borda/to/node-red", mensagem)
        except Exception as e:
            print(f"Erro ao enviar dados para o Node-RED: {e}")

    def enviar_mensagem_status(self, status_message, volume_total=None):
        try:
            dados = {
                'statusMessage': status_message
            }
            if volume_total is not None:
                dados['volume_total'] = round(float(volume_total), 2)

            mensagem = json.dumps(dados, indent=4)

            self.comunicacao.enviar_mensagem("borda/to/node-red/status_message", mensagem)
        except Exception as e:
            print(f"Erro ao enviar status para o Node-RED: {e}")

    @staticmethod
    def formatar_tempo(tempo):
        minutos = int(tempo)
        segundos = int((tempo - minutos) * 60)
        horas = 0
        return f"{horas:02}:{minutos:02}:{segundos:02}hs"

    @staticmethod
    def formatar_intervalo(intervalo):
        horas = int(intervalo)
        minutos = int((intervalo - horas) * 60)
        segundos = 0
        return f"{horas:02}:{minutos:02}:{segundos:02}hs"
