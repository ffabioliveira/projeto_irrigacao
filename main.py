import paho.mqtt.client as mqtt
import time
from logica_fuzzy import criar_sistema_fuzzy, calcular_fuzzy

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Máquina 1 conectada ao broker!")
        client.subscribe("maquina2/to/maquina1")
    else:
        print(f"Falha na conexão da Máquina 1. Código de retorno: {rc}")

def on_message(client, userdata, message):
    global maquina2_conectada  # Adiciona a variável global para modificá-la
    mensagem_recebida = message.payload.decode()
    print(f"Máquina 1 recebeu do tópico maquina2/to/maquina1: {mensagem_recebida}")

    if "Volume" in mensagem_recebida:
        dados = mensagem_recebida.split(';')
        for dado in dados:
            if dado.startswith("Volume"):
                volume_atual = float(dado.split(':')[1])
                print(f"Volume atual: {volume_atual:.2f} litros")
            elif dado.startswith("Tempo"):
                tempo_parcial = float(dado.split(':')[1])
                print(f"Tempo parcial: {tempo_parcial:.2f} minutos")
    elif "Confirmação:" in mensagem_recebida or "Próximo acionamento" in mensagem_recebida:
        print(f"\nMáquina 1 recebeu confirmação: {mensagem_recebida}\n")
    elif "Válvula" in mensagem_recebida:
        print(f"\nMáquina 2 informou: {mensagem_recebida}\n")
    elif "Máquina 2 conectada" in mensagem_recebida:  # Verifica a mensagem de conexão
        maquina2_conectada = True  # Sai do loop de espera

def obter_dados_ambientais():
    # Substitua esta função pela coleta real de dados da API do clima
    fase_desenvolvimento = 14  # dias
    textura_solo = 18  # porcentagem de argila
    evapotranspiracao = 5  # mm/dia
    precipitacao = 0  # mm
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
    broker = '10.0.0.117'  # Endereço IP do broker MQTT
    client = mqtt.Client("maquina1")
    client.on_connect = on_connect
    client.on_message = on_message

    print("Conectando Máquina 1 ao broker...")
    client.connect(broker)
    client.loop_start()

    maquina2_conectada = False
    while not maquina2_conectada:  # Aguarda a conexão da Máquina 2
        print("Aguardando conexão da Máquina 2...")
        time.sleep(5)

    ciclo_total = int(input("Informe o ciclo total da cultura em dias: "))  # Solicita o ciclo total
    simulador_fuzzy = criar_sistema_fuzzy(ciclo_total)

    try:
        while True:
            fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao = obter_dados_ambientais()
            tempo_acionamento, intervalo = calcular_fuzzy(simulador_fuzzy, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao)

            tempo_formatado = formatar_tempo(tempo_acionamento)
            intervalo_formatado = formatar_intervalo(intervalo)

            print(f"Tempo de acionamento recomendado: {tempo_formatado} minutos")
            print(f"Intervalo entre as irrigações recomendado: {intervalo_formatado} horas")

            client.publish("maquina1/to/maquina2", f"Ciclo:{ciclo_total};Tempo:{tempo_acionamento:.2f};Intervalo:{intervalo:.2f}")

            time.sleep(intervalo * 3600)  # Converter horas para segundos
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erro durante a execução: {e}")

    client.loop_stop()
    client.disconnect()
    print("Máquina 1 desconectada.")

