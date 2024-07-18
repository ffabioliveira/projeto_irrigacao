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
        self.valvula_ligada = False
        self.proximo_acionamento = None
        self.configurar_entradas_usuario()

    def configurar_entradas_usuario(self):
        self.ciclo_total = int(input("Informe o ciclo total da cultura em dias: "))
        self.textura_solo = float(input("Informe a porcentagem de argila no solo (0-100%): "))

    def iniciar(self):
        self.comunicacao.callback_volume = self.comunicacao_microcontrolador.processar_mensagem_volume

        while not self.comunicacao.client.is_connected():
            time.sleep(1)

        self.comunicacao.aguardar_conexao_microcontrolador()

        dados_ambientais = DadosAmbientais(self.ciclo_total, self.textura_solo)
        simulador_fuzzy = criar_sistema_fuzzy(self.ciclo_total)

        try:
            while True:
                self.gerenciar_ciclo_irrigacao(dados_ambientais, simulador_fuzzy)
        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")

    def gerenciar_ciclo_irrigacao(self, dados_ambientais, simulador_fuzzy):
        fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = dados_ambientais.obter_dados_ambientais()
        dia_atual = fase_desenvolvimento
        data_atual = datetime.now()

        if dia_atual > self.ciclo_total:
            print("Ciclo da cultura completado.")
            return

        tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
        self.imprimir_informacoes_irrigacao(dia_atual, data_atual, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
        self.comunicacao_microcontrolador.atualizar_dados_ambientais(fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

        self.gerenciar_valvula(tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

    def imprimir_informacoes_irrigacao(self, dia_atual, data_atual, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        print(f"Dia {dia_atual} de {self.ciclo_total} dia(s) do ciclo da cultura - Data: {data_atual.strftime('%d/%m/%Y')}")
        print(f"Tempo de acionamento recomendado: {self.formatar_tempo(tempo_acionamento)} minutos")
        print(f"Intervalo entre as irrigações recomendado: {self.formatar_intervalo(intervalo)} horas")
        print(f"Fase de Desenvolvimento: {fase_desenvolvimento}")
        print(f"Textura do Solo: {textura_solo}%")
        print(f"Evapotranspiração: {evapotranspiracao:.2f} mm")
        print(f"Precipitação: {precipitacao} mm")

    def gerenciar_valvula(self, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        if not self.valvula_ligada:
            self.comunicacao_microcontrolador.ligar_valvula()
            self.valvula_ligada = True
            self.proximo_acionamento = datetime.now() + timedelta(minutes=tempo_acionamento)
            self.comunicacao_nuvem.enviar_dados_nuvem(self.ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
            time.sleep(tempo_acionamento * 60)
        elif datetime.now() >= self.proximo_acionamento:
            self.comunicacao_microcontrolador.desligar_valvula()
            self.valvula_ligada = False
            self.proximo_acionamento = datetime.now() + timedelta(hours=intervalo)
            print(f"Próximo acionamento da válvula em: {self.proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S')}")
            self.comunicacao.mensagens_status.put(self.proximo_acionamento.strftime('%d/%m/%Y %H:%M:%S'))
            self.comunicacao_nuvem.enviar_dados_nuvem(self.ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
            time.sleep(intervalo * 3600)

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
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
