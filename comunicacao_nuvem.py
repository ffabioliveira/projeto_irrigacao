import json
from datetime import datetime

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, dia_atual, ciclo_total, data_atual, tempo_formatado, intervalo_formatado):
        self.comunicacao.enviar_mensagem("borda/to/node-red/cycle_info", json.dumps({
            "topic": "cycle_info",
            "day": dia_atual,
            "totalDays": ciclo_total,
            "date": data_atual.strftime('%d/%m/%Y')
        }))
        self.comunicacao.enviar_mensagem("borda/to/node-red/activation_time", json.dumps({
            "topic": "activation_time",
            "activationTime": tempo_formatado
        }))
        self.comunicacao.enviar_mensagem("borda/to/node-red/interval_time", json.dumps({
            "topic": "interval_time",
            "intervalTime": intervalo_formatado
        }))

    def enviar_volumes_agua(self, volume_atual, volume_anterior):
        self.comunicacao.enviar_mensagem("borda/to/node-red/water_volume", json.dumps({
            "topic": "water_volume",
            "waterVolume": volume_atual
        }))
        self.comunicacao.enviar_mensagem("borda/to/node-red/previous_water_volume", json.dumps({
            "topic": "previous_water_volume",
            "previousWaterVolume": volume_anterior
        }))

    def enviar_status_valvula(self, status):
        self.comunicacao.enviar_mensagem("borda/to/node-red/valve_status", json.dumps({
            "topic": "valve_status",
            "valveStatus": status
        }))

    def enviar_proximo_acionamento(self, proximo_acionamento):
        self.comunicacao.enviar_mensagem("borda/to/node-red/next_activation", json.dumps({
            "topic": "next_activation",
            "nextActivation": proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S')
        }))
