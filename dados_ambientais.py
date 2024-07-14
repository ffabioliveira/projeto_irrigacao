from datetime import datetime, timedelta
from simulador_climatico import SimuladorClimatico

class DadosAmbientais:
    def __init__(self, ciclo_total, textura_solo):
        if not isinstance(ciclo_total, int) or ciclo_total <= 0:
            raise ValueError("ciclo_total deve ser um inteiro positivo.")

        self.ciclo_total = ciclo_total
        self.textura_solo = textura_solo
        self.data_inicio = datetime.now()
        self.simulador = SimuladorClimatico(data_inicio=self.data_inicio, dias=ciclo_total)
        self.dados_climaticos = self.simulador.gerar_dados_climaticos()

    def obter_dados_ambientais(self):
        """Obtém os dados ambientais atuais."""
        data_atual = datetime.now()
        hora_atual = (data_atual - self.data_inicio).total_seconds() // 3600
        dia_atual = (data_atual - self.data_inicio).days + 1
        fase_desenvolvimento = dia_atual  # dias corridos
        evapotranspiracao = self.obter_evapotranspiracao(hora_atual)
        precipitacao = self.obter_precipitacao(hora_atual)
        return fase_desenvolvimento, self.textura_solo, evapotranspiracao, precipitacao

    def obter_evapotranspiracao(self, hora_atual):
        """Obtém a evapotranspiração do simulador."""
        return self.dados_climaticos.loc[int(hora_atual), 'Evapotranspiracao_mm']

    def obter_precipitacao(self, hora_atual):
        """Obtém a precipitação do simulador."""
        return self.dados_climaticos.loc[int(hora_atual), 'Precipitacao_mm']

    @staticmethod
    def formatar_tempo(tempo_minutos):
        """Formata o tempo em minutos para o formato MM:SS."""
        minutos = int(tempo_minutos)
        segundos = int((tempo_minutos - minutos) * 60)
        return f"{minutos:02}:{segundos:02}"

    @staticmethod
    def formatar_intervalo(intervalo_horas):
        """Formata o intervalo de horas para o formato HH:MM:SS."""
        horas = int(intervalo_horas)
        minutos = int((intervalo_horas - horas) * 60)
        segundos = int((intervalo_horas * 3600 - horas * 3600 - minutos * 60))
        return f"{horas:02}:{minutos:02}:{segundos:02}"
