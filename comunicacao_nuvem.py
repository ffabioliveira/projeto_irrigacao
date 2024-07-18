import json

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        # Prepara os dados a serem enviados para a nuvem
        dados = {
            "ciclo_total": ciclo_total,
            "tempo_acionamento": self.formatar_tempo(tempo_acionamento),
            "intervalo_entre_irrigacoes": self.formatar_intervalo(intervalo),
            "fase_desenvolvimento": fase_desenvolvimento,
            "textura_solo": textura_solo,
            "evapotranspiracao": round(evapotranspiracao, 2),
            "precipitacao": precipitacao,
            "mensagens_status": list(self.comunicacao.mensagens_status.queue)  # Converte a fila para lista
        }
        # Envia os dados formatados para o Node-RED
        self.comunicacao.enviar_mensagem('borda/to/node-red/dados', json.dumps(dados))
        self.comunicacao.mensagens_status.queue.clear()  # Limpa as mensagens de status após envio

    @staticmethod
    def formatar_tempo(tempo_minutos):
        # Converte o tempo em minutos para uma string formatada mm:ss
        minutos = int(tempo_minutos)
        segundos = int((tempo_minutos - minutos) * 60)
        return f"{minutos:02}:{segundos:02}"

    @staticmethod
    def formatar_intervalo(intervalo_horas):
        # Converte o intervalo em horas para uma string formatada hh:mm:ss
        horas = int(intervalo_horas)
        minutos = int((intervalo_horas - horas) * 60)
        segundos = int((intervalo_horas * 3600 - horas * 3600 - minutos * 60))
        return f"{horas:02}:{minutos:02}:{segundos:02}"
