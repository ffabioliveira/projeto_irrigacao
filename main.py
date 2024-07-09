import json
import time
from datetime import datetime, timedelta
from comunicacao_mqtt import ComunicacaoMQTT
from dados_ambientais import DadosAmbientais
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy
from comunicacao_nuvem import ComunicacaoNuvem
from comunicacao_microcontrolador import ComunicacaoMicrocontrolador

class Main:
    def __init__(self, broker, client_id):
        self.comunicacao = ComunicacaoMQTT(broker, client_id)
        self.comunicacao.conectar()
        self.comunicacao_nuvem = ComunicacaoNuvem(self.comunicacao)
        self.comunicacao_microcontrolador = ComunicacaoMicrocontrolador(self.comunicacao)
        self.volume_anterior = 0
        self.volume_atual = 0
        self.valvula_ligada = False  # Adicionado: Sinalizador para controlar o estado da válvula

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

                # Enviar dados para Node-RED
                self.comunicacao_nuvem.enviar_dados_nuvem(dia_atual, ciclo_total, data_atual, tempo_formatado, intervalo_formatado)

                if not self.valvula_ligada:
                    # Ligar válvula pelo tempo de acionamento recomendado
                    self.comunicacao_microcontrolador.ligar_valvula()
                    self.comunicacao_nuvem.enviar_status_valvula("Ligada")
                    time.sleep(tempo_acionamento * 60)
                    self.comunicacao_microcontrolador.desligar_valvula()
                    self.comunicacao_nuvem.enviar_status_valvula("Desligada")

                    # Atualizar volumes de água
                    self.volume_anterior = self.volume_atual
                    self.volume_atual += 10  # Exemplo de incremento de volume de água

                    # Enviar volumes de água para Node-RED
                    self.comunicacao_nuvem.enviar_volumes_agua(self.volume_atual, self.volume_anterior)

                    # Calcular próximo acionamento
                    proximo_acionamento = data_atual + timedelta(minutes=intervalo * 60)
                    self.comunicacao_nuvem.enviar_proximo_acionamento(proximo_acionamento)

                    # Espera até o próximo intervalo
                    time.sleep(intervalo * 3600)
                else:
                    time.sleep(1)
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

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
