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
        self.volume_total_diario = 0
        self.volume_por_irrigacao = 0
        self.valvula_ligada = False
        self.proximo_acionamento = None

        # Obter entradas do usuário
        self.ciclo_total = int(input("Informe o ciclo total da cultura em dias: "))
        self.textura_solo = float(input("Informe a porcentagem de argila no solo (0-100%): "))

    def iniciar(self):
        while not self.comunicacao.client.is_connected():
            time.sleep(1)

        self.comunicacao.aguardar_conexao_microcontrolador()

        dados_ambientais = DadosAmbientais(self.ciclo_total, self.textura_solo)
        simulador_fuzzy = criar_sistema_fuzzy(self.ciclo_total)

        try:
            while True:
                fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = dados_ambientais.obter_dados_ambientais()
                dia_atual = fase_desenvolvimento
                data_atual = datetime.now()

                if dia_atual > self.ciclo_total:
                    print("Ciclo da cultura completado.")
                    break

                tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

                # Impressão das informações de irrigação
                print(f"Dia {dia_atual} de {self.ciclo_total} dia(s) do ciclo da cultura - Data: {data_atual.strftime('%d/%m/%Y')}")
                print(f"Tempo de acionamento recomendado: {self.formatar_tempo(tempo_acionamento)} minutos")
                print(f"Intervalo entre as irrigações recomendado: {self.formatar_intervalo(intervalo)} horas")

                # Imprimir dados ambientais atualizados
                print(f"Fase de Desenvolvimento: {fase_desenvolvimento}")
                print(f"Textura do Solo: {textura_solo}%")
                print(f"Evapotranspiração: {evapotranspiracao:.2f} mm")
                print(f"Precipitação: {precipitacao} mm")

                self.comunicacao_microcontrolador.atualizar_dados_ambientais(fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

                # Enviar dados para Node-RED (se necessário)
                self.comunicacao_nuvem.enviar_dados_nuvem(self.ciclo_total, tempo_acionamento, intervalo, self.volume_por_irrigacao, self.volume_total_diario, self.valvula_ligada, self.proximo_acionamento, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

                if not self.valvula_ligada:
                    self.comunicacao_microcontrolador.ligar_valvula()
                    self.valvula_ligada = True
                    self.proximo_acionamento = datetime.now() + timedelta(minutes=tempo_acionamento)
                    self.volume_por_irrigacao = 0  # Zera o volume no início de cada irrigação
                    time.sleep(tempo_acionamento * 60)

                if self.valvula_ligada and datetime.now() >= self.proximo_acionamento:
                    self.comunicacao_microcontrolador.desligar_valvula()
                    self.valvula_ligada = False
                    self.proximo_acionamento = datetime.now() + timedelta(hours=intervalo)
                    self.volume_total_diario += self.volume_por_irrigacao  # Atualiza o volume diário após a irrigação
                    print(f"Próximo acionamento da válvula em: {self.proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S')}")
                    time.sleep(intervalo * 3600)

        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")

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

if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')  # Substitua pelo endereço IP correto do seu broker MQTT
    sistema.iniciar()
