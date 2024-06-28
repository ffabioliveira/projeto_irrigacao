# main_maquina1.py
import paho.mqtt.client as mqtt
import time

mensagem_recebida = ""
volume_atual = 0.0

def on_message(client, userdata, message):
    global mensagem_recebida, volume_atual
    mensagem_recebida = message.payload.decode()

    if mensagem_recebida.startswith("Volume atual:"):
        volume_atual = float(mensagem_recebida.split(":")[1].strip())
    else:
        print(f"\nMáquina 1 recebeu: {mensagem_recebida}\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Máquina 1 conectada ao broker!")
        client.subscribe("maquina2/to/maquina1")
    else:
        print(f"Falha na conexão da Máquina 1. Código de retorno: {rc}")

def on_publish(client, userdata, mid):
    pass  # Removendo a impressão do ID da publicação

if __name__ == '__main__':
    broker = '10.0.0.117'
    client = mqtt.Client("maquina1")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    print("Conectando Máquina 1 ao broker...")
    client.connect(broker)

    client.loop_start()

    ligado = False

    try:
        while True:
            print("Menu:")
            print("1 - ligar válvula")
            print("2 - desligar válvula")
            print("3 - sair")
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                if not ligado:
                    client.publish("maquina1/to/maquina2", "Ligar válvula")
                    ligado = True
                else:
                    print("A válvula já está ligada!")
            elif opcao == "2":
                if ligado:
                    client.publish("maquina1/to/maquina2", "Desligar válvula")
                    ligado = False
                else:
                    print("A válvula já está desligada!")
            elif opcao == "3":
                break
            else:
                print("Opção inválida!")

            # Introduz um pequeno atraso para garantir que as mensagens sejam processadas
            time.sleep(0.5)

            # Espera ativa até receber a mensagem de confirmação ou atualização do volume
            while not mensagem_recebida:
                print(f"Volume atual: {volume_atual:.2f} litros")
                time.sleep(1)
                client.loop()

            mensagem_recebida = ""

    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()
    print("Máquina 1 desconectada.")
