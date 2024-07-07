# logica_fuzzy.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def criar_sistema_fuzzy(ciclo_total):
    # Definir as variáveis de entrada e saída
    fase_desenvolvimento = ctrl.Antecedent(np.linspace(0, ciclo_total, ciclo_total+1), 'Fase de desenvolvimento da cultura') # fase de desenvolvimento da cultura em dias
    textura_solo = ctrl.Antecedent(np.linspace(0, 100, 101), 'Textura do solo') # textura do solo em porcentagem de argila
    evapotranspiracao = ctrl.Antecedent(np.linspace(0, 14, 15), 'Evapotranspiração') # evapotranspiração em mm/dia
    precipitacao = ctrl.Antecedent(np.linspace(0, 25, 26), 'Precipitação pluviométrica') # precipitação pluviométrica em mm
    tempo_acionamento = ctrl.Consequent(np.linspace(0, 60, 61), 'Tempo de acionamento') # tempo de acionamento do sistema de irrigação em minutos
    intervalo = ctrl.Consequent(np.linspace(0, 24, 25), 'Intervalo entre as irrigações') # intervalo entre as irrigações em horas

    # Definir os termos fuzzy para cada variável usando porcentagens do ciclo total
    fase_desenvolvimento['inicial'] = fuzz.trapmf(fase_desenvolvimento.universe, [0, 0, ciclo_total*0.125, ciclo_total*0.25])
    fase_desenvolvimento['desenvolvimento'] = fuzz.trimf(fase_desenvolvimento.universe, [ciclo_total*0.125, ciclo_total*0.375, ciclo_total*0.625])
    fase_desenvolvimento['produção'] = fuzz.trimf(fase_desenvolvimento.universe, [ciclo_total*0.5, ciclo_total*0.75, ciclo_total])
    fase_desenvolvimento['senescência'] = fuzz.trapmf(fase_desenvolvimento.universe, [ciclo_total*0.75, ciclo_total, ciclo_total, ciclo_total])

    textura_solo['arenosa'] = fuzz.trapmf(textura_solo.universe, [0, 0, 10, 20])
    textura_solo['média'] = fuzz.trimf(textura_solo.universe, [10, 30, 50])
    textura_solo['argilosa'] = fuzz.trapmf(textura_solo.universe, [40, 60, 100, 100])

    evapotranspiracao['muito baixa'] = fuzz.trapmf(evapotranspiracao.universe, [0, 0, 1, 3])
    evapotranspiracao['baixa'] = fuzz.trimf(evapotranspiracao.universe, [1, 3, 5])
    evapotranspiracao['média'] = fuzz.trimf(evapotranspiracao.universe, [4, 7, 10])
    evapotranspiracao['alta'] = fuzz.trimf(evapotranspiracao.universe, [9, 11, 13])
    evapotranspiracao['muito alta'] = fuzz.trapmf(evapotranspiracao.universe, [11, 13, 14, 14])

    precipitacao['muito baixa'] = fuzz.trapmf(precipitacao.universe, [0, 0, 1, 3]) # Muito baixa até 3 mm
    precipitacao['baixa'] = fuzz.trapmf(precipitacao.universe, [1, 3, 4, 6]) # Baixa entre 1 e 6 mm
    precipitacao['média'] = fuzz.trapmf(precipitacao.universe, [4, 6, 7, 9]) # Média entre 4 e 9 mm
    precipitacao['alta'] = fuzz.trapmf(precipitacao.universe, [7, 9, 10, 12]) # Alta entre 7 e 12 mm
    precipitacao['muito alta'] = fuzz.trapmf(precipitacao.universe, [10, 12, 25, 25]) # Muito alta acima de 10 mm

    tempo_acionamento['curto'] = fuzz.trapmf(tempo_acionamento.universe, [0, 0, 1, 3]) # mudança na função trapezoidal
    tempo_acionamento['moderado'] = fuzz.trimf(tempo_acionamento.universe, [2, 4, 6]) # mudança na função triangular
    tempo_acionamento['longo'] = fuzz.trapmf(tempo_acionamento.universe, [5, 7, 10, 10]) # mudança na função trapezoidal

    intervalo['curto'] = fuzz.trapmf(intervalo.universe, [0, 0, 1, 2]) # mudança na função trapezoidal
    intervalo['moderado'] = fuzz.trimf(intervalo.universe, [1.5, 3, 4.5]) # mudança na função triangular
    intervalo['longo'] = fuzz.trapmf(intervalo.universe, [4, 5, 6, 6]) # mudança na função trapezoidal

    # Definir as regras fuzzy para determinar o tempo e o intervalo de irrigação
    regras = [
        ctrl.Rule(fase_desenvolvimento['inicial'] & textura_solo['arenosa'], (tempo_acionamento['curto'], intervalo['curto'])),
        ctrl.Rule(fase_desenvolvimento['desenvolvimento'] & textura_solo['média'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(fase_desenvolvimento['produção'] & textura_solo['argilosa'], (tempo_acionamento['longo'], intervalo['longo'])),
        ctrl.Rule(fase_desenvolvimento['senescência'] & textura_solo['arenosa'], (tempo_acionamento['curto'], intervalo['longo'])),
        ctrl.Rule(evapotranspiracao['muito baixa'] & precipitacao['muito alta'], (tempo_acionamento['curto'], intervalo['longo'])),
        ctrl.Rule(evapotranspiracao['muito alta'] & precipitacao['muito baixa'], (tempo_acionamento['longo'], intervalo['curto'])),
        ctrl.Rule(evapotranspiracao['média'] & precipitacao['média'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['alta'] | precipitacao['muito alta'], tempo_acionamento['curto']),
        ctrl.Rule(precipitacao['alta'] | precipitacao['muito alta'], intervalo['longo']),
        ctrl.Rule(fase_desenvolvimento['inicial'] & textura_solo['média'], (tempo_acionamento['curto'], intervalo['curto'])),
        ctrl.Rule(fase_desenvolvimento['inicial'] & textura_solo['argilosa'], (tempo_acionamento['curto'], intervalo['curto'])),
        ctrl.Rule(fase_desenvolvimento['desenvolvimento'] & textura_solo['arenosa'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(fase_desenvolvimento['desenvolvimento'] & textura_solo['argilosa'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(fase_desenvolvimento['produção'] & textura_solo['arenosa'], (tempo_acionamento['longo'], intervalo['longo'])),
        ctrl.Rule(fase_desenvolvimento['senescência'] & textura_solo['média'], (tempo_acionamento['curto'], intervalo['longo'])),
        ctrl.Rule(fase_desenvolvimento['senescência'] & textura_solo['argilosa'], (tempo_acionamento['curto'], intervalo['longo'])),
        ctrl.Rule(evapotranspiracao['muito baixa'], (tempo_acionamento['curto'], intervalo['curto'])),
        ctrl.Rule(evapotranspiracao['baixa'], (tempo_acionamento['curto'], intervalo['curto'])),
        ctrl.Rule(evapotranspiracao['alta'] & precipitacao['muito baixa'], (tempo_acionamento['longo'], intervalo['curto'])),
        ctrl.Rule(evapotranspiracao['alta'] & precipitacao['baixa'], (tempo_acionamento['longo'], intervalo['curto'])),
        ctrl.Rule(evapotranspiracao['alta'] & precipitacao['média'], (tempo_acionamento['longo'], intervalo['moderado'])),
        ctrl.Rule(evapotranspiracao['muito alta'], (tempo_acionamento['longo'], intervalo['curto'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & fase_desenvolvimento['inicial'], (tempo_acionamento['curto'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & fase_desenvolvimento['desenvolvimento'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & fase_desenvolvimento['produção'], (tempo_acionamento['longo'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & fase_desenvolvimento['senescência'], (tempo_acionamento['curto'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & textura_solo['arenosa'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & textura_solo['média'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & textura_solo['argilosa'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & evapotranspiracao['muito baixa'], (tempo_acionamento['curto'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & evapotranspiracao['baixa'], (tempo_acionamento['curto'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & evapotranspiracao['média'], (tempo_acionamento['moderado'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & evapotranspiracao['alta'], (tempo_acionamento['longo'], intervalo['moderado'])),
        ctrl.Rule(precipitacao['baixa'] | precipitacao['média'] & evapotranspiracao['muito alta'], (tempo_acionamento['longo'], intervalo['curto']))
    ]

    # Criar o sistema de controle fuzzy
    sistema = ctrl.ControlSystem(regras)
    return ctrl.ControlSystemSimulation(sistema)

def calcular_fuzzy(simulador, fase_desenvolvimento, textura_solo, evapotranspiracao, precipitacao):
    # Informar os valores das variáveis de entrada
    simulador.input['Fase de desenvolvimento da cultura'] = fase_desenvolvimento
    simulador.input['Textura do solo'] = textura_solo
    simulador.input['Evapotranspiração'] = evapotranspiracao
    simulador.input['Precipitação pluviométrica'] = precipitacao

    # Realizar o cálculo fuzzy
    simulador.compute()

    # Retornar os resultados
    return simulador.output['Tempo de acionamento'], simulador.output['Intervalo entre as irrigações']
