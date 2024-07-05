import paho.mqtt.client as mqtt
import time

class ComunicacaoMQTT:
    def __init__(self, broker, client_id):
        self.client = mqtt.Client(client_id)
        self.broker = broker
        self.microcontrolador_conectado = False

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
        if mensagem_recebida.startswith("Status:"):
            print(f"Microcontrolador informou: {mensagem_recebida}")
        elif mensagem_recebida == "Microcontrolador conectado!":
            self.microcontrolador_conectado = True
            print("Microcontrolador conectado!")

    def aguardar_conexao_microcontrolador(self):
        while not self.microcontrolador_conectado:
            print("Aguardando conexão do Microcontrolador...")
            time.sleep(5)
