# app/facade/aireYClimaFacade.py
import requests

class AireYClimaFacade:
    def __init__(self):
        self.api_url = "https://api.open-meteo.com/v1/forecast?latitude=40.4&longitude=-3.7&current=temperature_2m"

    def recoger_ultimo_dato(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return response.json()
        return {"error": "No se pudo obtener el dato"}

