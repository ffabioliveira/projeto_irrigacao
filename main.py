import paho.mqtt.client as mqtt
import time
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Computador de Borda conectado ao broker!")
        client.subscribe("microcontrolador/to/borda")
    else:
        print(f"Falha na conexão do Computador de Borda. Código de retorno: {rc}")

def on_message(client, userdata, message):
    global microcontrolador_conectado
    mensagem_recebida = message.payload.decode()

    if mensagem_recebida.startswith("Status:"):
        print(f"Microcontrolador informou: {mensagem_recebida}")
    elif mensagem_recebida == "Microcontrolador conectado!":
        microcontrolador_conectado = True
        print("Microcontrolador conectado!")

def obter_dados_ambientais():
    fase_desenvolvimento = 67  # dias
    textura_solo = 47  # porcentagem de argila
    evapotranspiracao = 10  # mm/dia
    precipitacao = 20  # mm
    return fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao

def formatar_tempo(tempo_minutos):
    minutos = int(tempo_minutos)
    segundos = int((tempo_minutos - minutos) * 60)
    return f"{minutos:02}:{segundos:02}"

def formatar_intervalo(intervalo_horas):
    horas = int(intervalo_horas)
    minutos = int((intervalo_horas - horas) * 60)
    segundos = int((intervalo_horas * 3600 - horas * 3600 - minutos * 60))
    return f"{horas:02}:{minutos:02}:{segundos:02}"

if __name__ == '__main__':
    broker = '10.0.0.117'
    client = mqtt.Client("borda")
    client.on_connect = on_connect
    client.on_message = on_message
    print("Conectando Computador de Borda ao broker...")
    client.connect(broker)
    client.loop_start()

    microcontrolador_conectado = False

    while not client.is_connected():
        time.sleep(1)

    while not microcontrolador_conectado:
        print("Aguardando conexão do Microcontrolador...")
        time.sleep(5)

    ciclo_total = int(input("Informe o ciclo total da cultura em dias: "))
    simulador_fuzzy = criar_sistema_fuzzy(ciclo_total)

    fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = obter_dados_ambientais()
    tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

    tempo_formatado = formatar_tempo(tempo_acionamento)
    intervalo_formatado = formatar_intervalo(intervalo)

    print(f"Tempo de acionamento recomendado: {tempo_formatado} minutos")
    print(f"Intervalo entre as irrigações recomendado: {intervalo_formatado} horas")

    client.publish("borda/to/microcontrolador", f"Ciclo:{ciclo_total};Tempo:{tempo_acionamento:.2f};Intervalo:{intervalo:.2f}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erro durante a execução: {e}")

    client.loop_stop()
    client.disconnect()
    print("Computador de Borda desconectado.")
