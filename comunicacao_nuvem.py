import json

class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao, tipo_dado):
        try:
            dados = {
                'ciclo_total': ciclo_total,
                'tempo_acionamento': tempo_acionamento,
                'intervalo': intervalo,
                'fase_desenvolvimento': fase_desenvolvimento,
                'textura_solo': textura_solo,
                'evapotranspiracao': evapotranspiracao,
                'precipitacao': precipitacao,
                'tipo_dado': tipo_dado
            }
            mensagem = json.dumps(dados)
            self.comunicacao.enviar_mensagem("borda/to/node-red", mensagem)
            print(f"Dados enviados para o Node-RED: {tipo_dado}")
        except Exception as e:
            print(f"Erro ao enviar dados para o Node-RED: {e}")
