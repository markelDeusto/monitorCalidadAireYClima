# app/facade/aireYClimaFacade.py
import requests

class AireYClimaFacade:
    def __init__(self):
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        self.air_quality_api_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        self.weather_params = {
            "latitude": 40.4,
            "longitude": -3.7,
            "current_weather": True
        }
        self.air_quality_params = {
            "latitude": 40.4,
            "longitude": -3.7,
            "hourly": "pm10,pm2_5"
        }

    def recoger_ultimo_dato(self, latitude, longitude):
        # Parámetros dinámicos basados en las coordenadas
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }
        air_quality_params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm10,pm2_5"
        }

        # Obtener datos del clima actual
        weather_response = requests.get(self.weather_api_url, params=weather_params)
        weather_data = weather_response.json() if weather_response.status_code == 200 else {}

        # Obtener datos de calidad del aire
        air_quality_response = requests.get(self.air_quality_api_url, params=air_quality_params)
        air_quality_data = air_quality_response.json() if air_quality_response.status_code == 200 else {}

        # Combinar los datos
        return {
            "weather": weather_data,
            "air_quality": air_quality_data
        }