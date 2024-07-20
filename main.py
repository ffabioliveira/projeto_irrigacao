import json
import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
from dados_ambientais import DadosAmbientais
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy

class ComunicacaoMQTT:
    def __init__(self, broker, client_id):
        self.client = mqtt.Client(client_id)
        self.broker = broker
        self.microcontrolador_conectado = False
        self.callback_volume = None

    def conectar(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker)
        self.client.loop_start()

    def enviar_mensagem(self, topico, mensagem):
        self.client.publish(topico, mensagem)

    def inscrever(self, topico, callback):
        self.client.subscribe(topico)
        self.client.message_callback_add(topico, callback)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Computador de Borda conectado ao broker!")
            client.subscribe("microcontrolador/to/borda")
        else:
            print(f"Falha na conexão do Computador de Borda. Código de retorno: {rc}")

    def on_message(self, client, userdata, message):
        mensagem_recebida = message.payload.decode()
        print(f"Mensagem recebida: {mensagem_recebida}")
        if 'volume_total' in mensagem_recebida:
            if self.callback_volume:
                self.callback_volume(mensagem_recebida)
        elif mensagem_recebida == "Microcontrolador conectado!":
            self.microcontrolador_conectado = True
            print("Microcontrolador conectado!")
            self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": "Microcontrolador conectado!"}))
        elif mensagem_recebida.startswith("Status:"):
            status_message = mensagem_recebida.split(": ", 1)[1]
            if status_message not in ["Válvula ligada", "Válvula desligada"]:
                self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": status_message}))
        else:
            print(f"Mensagem não reconhecida: {mensagem_recebida}")

    def aguardar_conexao_microcontrolador(self):
        while not self.microcontrolador_conectado:
            status_message = "Aguardando conexão do Microcontrolador..."
            print(status_message)
            self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": status_message}))
            time.sleep(5)


class ComunicacaoNuvem:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao

    def enviar_dados_nuvem(self, ciclo_total, tempo_acionamento, intervalo, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        try:
            dados = {
                'ciclo_total': ciclo_total,
                'tempo_acionamento': self.formatar_tempo(tempo_acionamento),
                'intervalo': self.formatar_intervalo(intervalo),
                'fase_desenvolvimento': fase_desenvolvimento,
                'textura_solo': textura_solo,
                'evapotranspiracao': round(float(evapotranspiracao), 2),
                'precipitacao': round(float(precipitacao), 2)
            }
            mensagem = json.dumps(dados, indent=4)
            self.comunicacao.enviar_mensagem("borda/to/node-red", mensagem)
        except Exception as e:
            print(f"Erro ao enviar dados para o Node-RED: {e}")

    def enviar_mensagem_status(self, status_message, volume_total=None):
        try:
            dados = {
                'statusMessage': status_message
            }
            if volume_total is not None:
                dados = {
                    'volume_total': round(float(volume_total), 2)
                }

            mensagem = json.dumps(dados, indent=4)
            self.comunicacao.enviar_mensagem("borda/to/node-red/status_message", mensagem)
        except Exception as e:
            print(f"Erro ao enviar status para o Node-RED: {e}")

    @staticmethod
    def formatar_tempo(tempo):
        minutos = int(tempo)
        segundos = int((tempo - minutos) * 60)
        horas = 0
        return f"{horas:02}:{minutos:02}:{segundos:02}hs"

    @staticmethod
    def formatar_intervalo(intervalo):
        horas = int(intervalo)
        minutos = int((intervalo - horas) * 60)
        segundos = 0
        return f"{horas:02}:{minutos:02}:{segundos:02}hs"


class ComunicacaoMicrocontrolador:
    def __init__(self, comunicacao):
        self.comunicacao = comunicacao
        self.volume_total = 0.0

    def ligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "ligar_valvula")
        except Exception as e:
            print(f"Erro ao enviar mensagem 'ligar_valvula': {e}")

    def desligar_valvula(self):
        try:
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", "desligar_valvula")
            self.comunicacao.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": "Válvula desligada", "volume_total": self.volume_total}))
        except Exception as e:
            print(f"Erro ao enviar mensagem 'desligar_valvula': {e}")

    def atualizar_dados_ambientais(self, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
        try:
            dados = {
                'fase_desenvolvimento': fase_desenvolvimento,
                'textura_solo': textura_solo,
                'evapotranspiracao': evapotranspiracao,
                'precipitacao': precipitacao
            }
            mensagem = json.dumps(dados)
            self.comunicacao.enviar_mensagem("borda/to/microcontrolador", mensagem)
        except Exception as e:
            print(f"Erro ao enviar dados ambientais atualizados: {e}")

    def processar_mensagem_volume(self, mensagem):
        try:
            dados = json.loads(mensagem)
            if 'volume_total' in dados:
                self.volume_total = float(dados['volume_total'])
                print(f"Volume total atualizado: {self.volume_total} litros")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar mensagem: {mensagem}")


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
        self.gerenciar_valvula(tempo_acionamento, intervalo)

        return fase_desenvolvimento

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


if __name__ == '__main__':
    sistema = Main('10.0.0.117', 'borda')
    sistema.iniciar()
