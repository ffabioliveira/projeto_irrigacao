import time
from datetime import datetime
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
                data_atual = datetime.now()
                dia_atual = (data_atual - dados_ambientais.data_inicio).days + 1

                if dia_atual > ciclo_total:
                    print("Ciclo da cultura completado.")
                    break

                fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = dados_ambientais.obter_dados_ambientais(dia_atual)
                tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

                tempo_formatado = dados_ambientais.formatar_tempo(tempo_acionamento)
                intervalo_formatado = dados_ambientais.formatar_intervalo(intervalo)

                print(f"Dia {dia_atual} do ciclo da cultura")
                print(f"Tempo de acionamento recomendado: {tempo_formatado} minutos")
                print(f"Intervalo entre as irrigações recomendado: {intervalo_formatado} horas")

                self.comunicacao.enviar_mensagem("borda/to/microcontrolador", f"Ciclo:{ciclo_total};Tempo:{tempo_acionamento:.2f};Intervalo:{intervalo:.2f}")

                time.sleep(86400)  # Aguardar um dia (24 horas)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Erro durante a execução: {e}")

        self.comunicacao.client.loop_stop()
        self.comunicacao.client.disconnect()
        print("Computador de Borda desconectado.")

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
