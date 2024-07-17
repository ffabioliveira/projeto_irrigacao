import paho.mqtt.client as mqtt
import time
import json

class ComunicacaoMQTT:
    def __init__(self, broker, client_id):
        self.client = mqtt.Client(client_id)
        self.broker = broker
        self.microcontrolador_conectado = False
        self.mensagens_status = []
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
            self.callback_volume(mensagem_recebida)
        else:
            self.mensagens_status.append(mensagem_recebida)
            if mensagem_recebida.startswith("Status:"):
                print(f"Microcontrolador informou: {mensagem_recebida}")
                self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": mensagem_recebida.split(': ', 1)[1]}))
            elif mensagem_recebida == "Microcontrolador conectado!":
                self.microcontrolador_conectado = True
                print("Microcontrolador conectado!")
                self.enviar_mensagem("borda/to/node-red/status_message", '{"statusMessage": "Microcontrolador conectado!"}')
            self.enviar_mensagens_status()

    def aguardar_conexao_microcontrolador(self):
        while not self.microcontrolador_conectado:
            print("Aguardando conexão do Microcontrolador...")
            self.enviar_mensagem("borda/to/node-red/status_message", '{"statusMessage": "Aguardando conexão do Microcontrolador..."}')
            time.sleep(5)

    def enviar_mensagens_status(self):
        for mensagem in self.mensagens_status:
            if isinstance(mensagem, float):
                self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": mensagem}))
            else:
                self.enviar_mensagem("borda/to/node-red/status_message", json.dumps({"statusMessage": mensagem}))
        self.mensagens_status = []
