from datetime import datetime, timedelta

class DadosAmbientais:
    def __init__(self, ciclo_total, textura_solo):
        self.ciclo_total = ciclo_total
        self.textura_solo = textura_solo
        self.data_inicio = datetime.now()

    def obter_dados_ambientais(self):
        data_atual = datetime.now()
        dia_atual = (data_atual - self.data_inicio).days + 1
        fase_desenvolvimento = dia_atual  # dias corridos
        evapotranspiracao = 0 # mm/dia
        precipitacao = 0  # mm
        return fase_desenvolvimento, self.textura_solo, evapotranspiracao, precipitacao

    @staticmethod
    def formatar_tempo(tempo_minutos):
        minutos = int(tempo_minutos)
        segundos = int((tempo_minutos - minutos) * 60)
        return f"{minutos:02}:{segundos:02}"

    @staticmethod
    def formatar_intervalo(intervalo_horas):
        horas = int(intervalo_horas)
        minutos = int((intervalo_horas - horas) * 60)
        segundos = int((intervalo_horas * 3600 - horas * 3600 - minutos * 60))
        return f"{horas:02}:{minutos:02}:{segundos:02}"
