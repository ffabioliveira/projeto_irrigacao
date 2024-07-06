import time
from datetime import datetime, timedelta
from comunicacao_mqtt import ComunicacaoMQTT
from dados_ambientais import DadosAmbientais
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy

class Main:
    def __init__(self, broker, client_id):
        self.comunicacao = ComunicacaoMQTT(broker, client_id)
        self.comunicacao.conectar()

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

                tempo_formatado = dados_ambientais.formatar_tempo(tempo_acionamento)
                intervalo_formatado = dados_ambientais.formatar_intervalo(intervalo)

                print(f"Dia {dia_atual} de {ciclo_total} dia(s) do ciclo da cultura - Data: {data_atual.strftime('%d/%m/%Y')} - Hora atual: {data_atual.strftime('%H:%M:%S')}")
                print(f"Tempo de acionamento recomendado: {tempo_formatado} minutos")
                print(f"Intervalo entre as irrigações recomendado: {intervalo_formatado} horas")

                # Ligar válvula imediatamente
                self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")
                self.atualizar_status_periodicamente(tempo_acionamento * 60, "Acionamento em progresso")

                # Desligar válvula
                self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")

                # Calcular próximo acionamento
                proximo_acionamento = data_atual + timedelta(minutes=tempo_acionamento + intervalo * 60)
                print(f"Próximo acionamento: {proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S')}")

                # Enviar status durante o intervalo
                self.atualizar_status_periodicamente(intervalo * 3600 - tempo_acionamento * 60, "Intervalo entre acionamentos")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Erro durante a execução: {e}")

        self.comunicacao.client.loop_stop()
        self.comunicacao.client.disconnect()
        print("Computador de Borda desconectado.")

    def atualizar_status_periodicamente(self, duracao, mensagem):
        start_time = time.time()
        while time.time() - start_time < duracao:
            print(f"{mensagem} - {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(60)  # Atualiza a cada minuto

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
