import json
from datetime import datetime

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        dados = {
            "ciclo_total": ciclo_total,
            "tempo_acionamento": self.formatar_tempo(tempo_acionamento),
            "intervalo_entre_irrigacoes": self.formatar_intervalo(intervalo),
            "fase_desenvolvimento": fase_desenvolvimento,
            "textura_solo": textura_solo,
            "evapotranspiracao": round(evapotranspiracao, 2),
            "precipitacao": precipitacao,
            "mensagens_status": self.comunicacao.mensagens_status  # Adiciona as mensagens de status
        }
        self.comunicacao.enviar_mensagem('borda/to/node-red/dados', json.dumps(dados))
        self.comunicacao.enviar_mensagens_status()  # Envia as mensagens de status acumuladas

    @staticmethod
    def formatar_tempo(tempo_minutos):
        minutos = int(tempo_minutos)
        segundos = int((tempo_minutos - minutos) * 60)
        return f"{minutos:02}:{segundos:02}"

    @staticmethod
    def formatar_intervalo(intervalo_horas):
        horas = int(intervalo_horas)
        minutos = int((intervalo_horas - horas) * 60)
        segundos = int((intervalo_horas * 3600 - horas * 3600 - minutos * 60))
        return f"{horas:02}:{minutos:02}:{segundos:02}"
