import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SimuladorClimatico:
    def __init__(self, data_inicio, dias=7):
        self.data_inicio = data_inicio
        self.horas = dias * 24
        self.datas = pd.date_range(start=data_inicio, periods=self.horas, freq='h')  # Alterado de 'H' para 'h'

    def simular_precipitacao_horaria(self, umidade):
        precip = np.zeros(self.horas)
        for i in range(self.horas):
            mes = (self.data_inicio + timedelta(hours=i)).month
            if mes in [3, 4, 5, 6, 7]:  # Meses chuvosos
                probabilidade_chuva = umidade[i] / 100  # Aumenta a chance de chuva com a umidade
                if np.random.rand() < probabilidade_chuva:
                    precip[i] = np.random.poisson(0.5)  # Média de 0.5 mm por hora
            else:
                probabilidade_chuva = umidade[i] / 200  # Menor chance de chuva nos meses secos
                if np.random.rand() < probabilidade_chuva:
                    precip[i] = np.random.poisson(0.05)  # Média de 0.05 mm por hora
        return precip

    def calcular_evapotranspiracao(self, temp, umidade, vento, radiacao):
        # Constantes
        delta = 4098 * (0.6108 * np.exp((17.27 * temp) / (temp + 237.3))) / ((temp + 237.3) ** 2)
        gamma = 0.665 * 10 ** -3 * 101.3  # kPa/°C
        es = 0.6108 * np.exp((17.27 * temp) / (temp + 237.3))
        ea = umidade / 100 * es
        Rn = 0.408 * radiacao  # MJ/m^2/dia
        G = 0  # Fluxo de calor no solo assumido como 0

        # Fórmula de Penman-Monteith
        ET0 = (0.408 * delta * (Rn - G) + gamma * (900 / (temp + 273)) * vento * (es - ea)) / (delta + gamma * (1 + 0.34 * vento))

        # Garantir que o valor não seja negativo
        return max(ET0, 0)

    def gerar_dados_climaticos(self):
        temperatura = np.random.normal(28, 3, self.horas)  # Temperatura média em graus Celsius
        umidade = np.random.uniform(30, 60, self.horas)  # Umidade relativa em %
        vento = np.random.uniform(2, 5, self.horas)  # Velocidade do vento em m/s
        radiacao = np.random.uniform(20, 30, self.horas)  # Radiação solar em MJ/m^2/dia

        precipitacao = self.simular_precipitacao_horaria(umidade)
        evapotranspiracao = [self.calcular_evapotranspiracao(temp, umidade[i], vento[i], radiacao[i]) for i, temp in enumerate(temperatura)]

        dados_climaticos = pd.DataFrame({
            'DataHora': self.datas,
            'Precipitacao_mm': precipitacao,
            'Temperatura_C': temperatura,
            'Umidade_%': umidade,
            'Vento_m_s': vento,
            'Radiacao_MJ_m2_dia': radiacao,
            'Evapotranspiracao_mm': evapotranspiracao
        })

        return dados_climaticos

# Exemplo de uso
if __name__ == "__main__":
    simulador = SimuladorClimatico(data_inicio=datetime(2024, 7, 1), dias=7)
    dados = simulador.gerar_dados_climaticos()
    print(dados.head())
