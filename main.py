import json
import time
from datetime import datetime, timedelta
from comunicacao_mqtt import ComunicacaoMQTT
from dados_ambientais import DadosAmbientais
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy

class Main:
    def __init__(self, broker, client_id):
        self.comunicacao = ComunicacaoMQTT(broker, client_id)
        self.comunicacao.conectar()
        self.volume_anterior = 0
        self.volume_atual = 0

    def iniciar(self):
        while not self.comunicacao.client.is_connected():
            time.sleep(1)

        self.comunicacao.aguardar_conexao_microcontrolador()

        ciclo_total = int(input("Informe o ciclo total da cultura em dias: "))
        textura_solo = float(input("Informe a porcentagem de argila no solo (0-100%): "))

        dados_ambientais = DadosAmbientais(ciclo_total, textura_solo)
        simulador_fuzzy = criar_sistema_fuzzy(ciclo_total)

        try:
            while True:
                fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = dados_ambientais.obter_dados_ambientais()
                dia_atual = fase_desenvolvimento
                data_atual = datetime.now()

                if dia_atual > ciclo_total:
                    print("Ciclo da cultura completado.")
                    break

                tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

                tempo_formatado = self.formatar_tempo(tempo_acionamento)
                intervalo_formatado = self.formatar_intervalo(intervalo)

                # Log para verificação
                print(f"Dia {dia_atual} de {ciclo_total} dia(s) do ciclo da cultura - Data: {data_atual.strftime('%d/%m/%Y')}")
                print(f"Tempo de acionamento recomendado: {tempo_formatado} minutos")
                print(f"Intervalo entre as irrigações recomendado: {intervalo_formatado} horas")

                # Publicar dados específicos no broker MQTT em formato JSON
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
                self.comunicacao.enviar_mensagem("borda/to/node-red/valve_status", json.dumps({
                    "topic": "valve_status",
                    "valveStatus": "Ligada"
                }))

                # Ligar válvula imediatamente
                self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")
                self.atualizar_status_periodicamente(tempo_acionamento * 60, "Estado do Sistema", tempo_acionamento)

                # Atualizar volumes de água
                self.volume_anterior = self.volume_atual
                self.volume_atual += 10  # Exemplo de incremento de volume de água

                self.comunicacao.enviar_mensagem("borda/to/node-red/water_volume", json.dumps({
                    "topic": "water_volume",
                    "waterVolume": self.volume_atual
                }))
                self.comunicacao.enviar_mensagem("borda/to/node-red/previous_water_volume", json.dumps({
                    "topic": "previous_water_volume",
                    "previousWaterVolume": self.volume_anterior
                }))

                # Desligar válvula
                self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")
                self.comunicacao.enviar_mensagem("borda/to/node-red/valve_status", json.dumps({
                    "topic": "valve_status",
                    "valveStatus": "Desligada"
                }))

                # Calcular próximo acionamento
                proximo_acionamento = data_atual + timedelta(minutes=tempo_acionamento + intervalo * 60)
                self.comunicacao.enviar_mensagem("borda/to/node-red/next_activation", json.dumps({
                    "topic": "next_activation",
                    "nextActivation": proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S')
                }))

                # Enviar status durante o intervalo
                self.atualizar_status_periodicamente(intervalo * 3600 - tempo_acionamento * 60, "Estado do Sistema", intervalo * 60)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Erro durante a execução: {e}")

        self.comunicacao.client.loop_stop()
        self.comunicacao.client.disconnect()
        print("Computador de Borda desconectado.")

    def formatar_tempo(self, tempo_minutos):
        minutos = int(tempo_minutos)
        segundos = int((tempo_minutos - minutos) * 60)
        return f"{minutos:02d}:{segundos:02d}"

    def formatar_intervalo(self, intervalo_horas):
        horas = int(intervalo_horas)
        minutos = int((intervalo_horas - horas) * 60)
        segundos = int(((intervalo_horas - horas) * 60 - minutos) * 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def atualizar_status_periodicamente(self, duracao, mensagem, tempo_total):
        start_time = time.time()
        while time.time() - start_time < duracao:
            elapsed_time = time.time() - start_time
            remaining_time = tempo_total - (elapsed_time / 60)
            percent_complete = (elapsed_time / (tempo_total * 60)) * 100
            status_mensagem = f"{mensagem} - {percent_complete:.2f}% concluído, tempo restante: {self.formatar_tempo(remaining_time)}"
            print(status_mensagem)
            self.comunicacao.enviar_mensagem("borda/to/node-red/system_status", json.dumps({
                "topic": "system_status",
                "time": datetime.now().strftime('%H:%M:%S'),
                "percentComplete": f"{percent_complete:.2f}%",
                "remainingTime": self.formatar_tempo(remaining_time)
            }))
            time.sleep(60)  # Atualiza a cada minuto

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
