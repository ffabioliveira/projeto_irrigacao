import requests
import configparser
import os

class APIClima:
    def __init__(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '../../config/configuracoes.ini')
        config.read(config_path)
        self.api_key = config['API_CLIMA']['API_KEY'].strip("'")
        self.base_url = config['API_CLIMA']['BASE_URL'].strip("'")

    def obter_dados_precipitacao(self, latitude, longitude):
        url = f"{self.base_url}?lat={latitude}&lon={longitude}&appid={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            precipitacao = dados.get('rain', {}).get('1h', 0)
            return precipitacao
        else:
            response.raise_for_status()

if __name__ == "__main__":
    latitude = -23.5505 # Latitude de São Paulo
    longitude = -46.6333 # Longitude de São Paulo
    try:
        precip = api_clima.obter_dados_precipitacao(latitude, longitude)
        print(f"Precipitação: {precip} mm")
    except Exception as e:
        print(f"Erro: {e}")
