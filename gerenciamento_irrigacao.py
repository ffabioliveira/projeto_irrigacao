from datetime import datetime, timedelta
import time

class GerenciamentoIrrigacao:
    def __init__(self, comunicacao_nuvem, comunicacao_microcontrolador):
        self.comunicacao_nuvem = comunicacao_nuvem
        self.comunicacao_microcontrolador = comunicacao_microcontrolador
        self.valvula_ligada = False
        self.proximo_acionamento = None

    def gerenciar_valvula(self, tempo_acionamento, intervalo):
        if not self.valvula_ligada:
            self.comunicacao_microcontrolador.ligar_valvula()
            self.valvula_ligada = True
            self.proximo_acionamento = datetime.now() + timedelta(minutes=tempo_acionamento)
            self.comunicacao_nuvem.enviar_mensagem_status("Válvula ligada")
            time.sleep(tempo_acionamento * 60)
        elif datetime.now() >= self.proximo_acionamento:
            self.comunicacao_microcontrolador.desligar_valvula()
            self.valvula_ligada = False
            proximo_acionamento_str = datetime.now() + timedelta(hours=intervalo)
            self.comunicacao_nuvem.enviar_mensagem_status(f"Próximo acionamento da válvula em: {proximo_acionamento_str.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Próximo acionamento da válvula em: {proximo_acionamento_str.strftime('%d/%m/%Y %H:%M:%S')}")
            time.sleep(intervalo * 3600)
