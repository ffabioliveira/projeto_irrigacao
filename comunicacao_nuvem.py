import json
from datetime import datetime

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, volume_por_irrigacao, volume_total_diario, valvula_ligada, proximo_acionamento, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        dados = {
            "ciclo_total": ciclo_total,
            "tempo_acionamento": self.formatar_tempo(tempo_acionamento),
            "intervalo_entre_irrigacoes": self.formatar_intervalo(intervalo),
            "volume_por_irrigacao": volume_por_irrigacao,
            "volume_total_diario": volume_total_diario,
            "status_valvula": "ligada" if valvula_ligada else "desligada",
            "proximo_acionamento": proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S') if proximo_acionamento else "N/A",
            "fase_desenvolvimento": fase_desenvolvimento,
            "textura_solo": textura_solo,
            "evapotranspiracao": evapotranspiracao,
            "precipitacao": precipitacao
        }
        self.comunicacao.enviar_mensagem('topico/nuvem', json.dumps(dados))

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
