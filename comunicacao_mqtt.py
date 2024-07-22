import json
import time
import paho.mqtt.client as mqtt

class ComunicacaoMQTT:
    def __init__(self, broker, client_id, main_instance):
        self.client = mqtt.Client(client_id)
        self.broker = broker
        self.main_instance = main_instance
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
            client.subscribe("node-red/to/borda/configuracao")
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
            try:
                dados = json.loads(mensagem_recebida)
                if 'ciclo_total' in dados and 'textura_solo' in dados:
                    self.main_instance.ciclo_total = int(dados['ciclo_total'])
                    self.main_instance.textura_solo = float(dados['textura_solo'])
                    print(f"Ciclo total e textura do solo atualizados: {self.main_instance.ciclo_total} dias, {self.main_instance.textura_solo}% argila")
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar mensagem: {mensagem_recebida} - Erro: {e}")

    def aguardar_conexao_microcontrolador(self):
        while not self.microcontrolador_conectado:
            status_message = "Aguardando conexão do Microcontrolador..."
            print(status_message)
            self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": status_message}))
            time.sleep(5)
