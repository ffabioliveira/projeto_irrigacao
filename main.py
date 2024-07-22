import json
import time
from datetime import datetime, timedelta
from dados_ambientais import DadosAmbientais
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy
from comunicacao_mqtt import ComunicacaoMQTT
from comunicacao_nuvem import ComunicacaoNuvem
from comunicacao_microcontrolador import ComunicacaoMicrocontrolador
from gerenciamento_irrigacao import GerenciamentoIrrigacao

class Main:
    def __init__(self, broker, client_id):
        self.comunicacao = ComunicacaoMQTT(broker, client_id, self)
        self.comunicacao.conectar()
        self.comunicacao_nuvem = ComunicacaoNuvem(self.comunicacao)
        self.comunicacao_microcontrolador = ComunicacaoMicrocontrolador(self.comunicacao)
        self.gerenciamento_irrigacao = GerenciamentoIrrigacao(self.comunicacao_nuvem, self.comunicacao_microcontrolador)
        self.valvula_ligada = False
        self.proximo_acionamento = None
        self.ciclo_total = None
        self.textura_solo = None

    def iniciar(self):
        self.comunicacao.callback_volume = self.comunicacao_microcontrolador.processar_mensagem_volume

        while not self.comunicacao.client.is_connected():
            time.sleep(1)

        self.comunicacao.aguardar_conexao_microcontrolador()

        while self.ciclo_total is None or self.textura_solo is None:
            print("Aguardando entrada do ciclo total e textura do solo pelo Node-RED...")
            time.sleep(5)

        dados_ambientais = DadosAmbientais(self.ciclo_total, self.textura_solo)
        simulador_fuzzy = criar_sistema_fuzzy(self.ciclo_total)

        try:
            dia_atual = 0
            while True:
                nova_dia = self.gerenciar_ciclo_irrigacao(dados_ambientais, simulador_fuzzy, dia_atual)
                if nova_dia != dia_atual:
                    dia_atual = nova_dia
        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")

    def gerenciar_ciclo_irrigacao(self, dados_ambientais, simulador_fuzzy, dia_atual):
        fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = dados_ambientais.obter_dados_ambientais()
        data_atual = datetime.now()

        if fase_desenvolvimento > self.ciclo_total:
            print("Ciclo da cultura completado.")
            return fase_desenvolvimento

        tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
        if fase_desenvolvimento != dia_atual:
            print(f"\nDia {fase_desenvolvimento} de {self.ciclo_total} dia(s) do ciclo da cultura - Data: {data_atual.strftime('%d/%m/%Y')}")
            print(f"Tempo de acionamento recomendado: {self.comunicacao_nuvem.formatar_tempo(tempo_acionamento)}")
            print(f"Intervalo entre as irrigações recomendado: {self.comunicacao_nuvem.formatar_intervalo(intervalo)}")
            print(f"Fase de Desenvolvimento: {fase_desenvolvimento}")
            print(f"Textura do Solo: {textura_solo}%")
            print(f"Evapotranspiração: {evapotranspiracao:.2f} mm")
            print(f"Precipitação: {precipitacao} mm")
            self.comunicacao_nuvem.enviar_dados_nuvem(self.ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

        self.comunicacao_microcontrolador.atualizar_dados_ambientais(fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)
        self.gerenciamento_irrigacao.gerenciar_valvula(tempo_acionamento, intervalo)

        return fase_desenvolvimento

if __name__ == '__main__':
    main = Main('10.0.0.117', 'borda')
    main.iniciar()
