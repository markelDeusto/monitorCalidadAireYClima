import unittest
from unittest.mock import patch, Mock
import json
from flask import Flask
from app.api.routes import api
from app.ui.interfaz import ui
from app.facade.aireYClimaFacade import AireYClimaFacade

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        # Crear una aplicación Flask de prueba con todos los componentes
        self.app = Flask(__name__)
        self.app.register_blueprint(api)
        self.app.register_blueprint(ui)
        self.client = self.app.test_client()
        
        # Crear instancia real de la fachada
        self.fachada = AireYClimaFacade()
        
        # Datos simulados para respuestas de API externas
        self.mock_weather_data = {
            "current_weather": {
                "temperature": 23.5,
                "windspeed": 12.3,
                "weathercode": 0,
                "time": "2023-05-20T12:00"
            }
        }
        self.mock_air_quality_data = {
            "hourly": {
                "time": ["2023-05-20T12:00"],
                "pm10": [15.2],
                "pm2_5": [8.4]
            }
        }
        self.mock_geocoding_data = [
            {
                "lat": "40.4",
                "lon": "-3.7",
                "display_name": "Madrid"
            }
        ]
    
    @patch('app.facade.aireYClimaFacade.requests.get')
    @patch('app.ui.interfaz.requests.get')
    def test_flujo_completo_consulta_actual(self, mock_ui_requests, mock_facade_requests):
        """Prueba de integración para el flujo completo de consulta de datos actuales"""
        
        # Configurar respuesta para geocodificación (UI)
        mock_geocoding_response = Mock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.text = json.dumps(self.mock_geocoding_data)
        mock_geocoding_response.json.return_value = self.mock_geocoding_data
        
        # Configurar respuestas para los datos de clima y aire (Facade)
        mock_weather_response = Mock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = self.mock_weather_data
        
        mock_air_quality_response = Mock()
        mock_air_quality_response.status_code = 200
        mock_air_quality_response.json.return_value = self.mock_air_quality_data
        
        # Configurar el comportamiento de los mocks
        mock_ui_requests.side_effect = [
            mock_geocoding_response,  # Para geocodificación
            Mock(status_code=200, json=lambda: {"weather": self.mock_weather_data, "air_quality": self.mock_air_quality_data})  # Para la llamada interna a la API
        ]
        mock_facade_requests.side_effect = [mock_weather_response, mock_air_quality_response]
        
        # Realizar la solicitud a través de la interfaz web
        response = self.client.get('/?ciudad=Madrid')
        
        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Temperatura: 23.5', response.data)
        self.assertIn(b'PM10: 15.2', response.data)
        self.assertIn(b'PM2.5: 8.4', response.data)
    
    @patch('app.facade.aireYClimaFacade.requests.get')
    @patch('app.ui.interfaz.requests.get')
    def test_flujo_completo_datos_historicos(self, mock_ui_requests, mock_facade_requests):
        """Prueba de integración para el flujo completo de consulta de datos históricos"""
        
        # Configurar respuesta para geocodificación (UI)
        mock_geocoding_response = Mock()
        mock_geocoding_response.status_code = 200
        mock_geocoding_response.json.return_value = self.mock_geocoding_data
        
        # Datos históricos simulados
        mock_historical_weather_data = {
            "daily": {
                "time": ["2023-05-15", "2023-05-16", "2023-05-17"],
                "temperature_2m_max": [25.3, 24.8, 26.2],
                "temperature_2m_min": [15.1, 14.9, 16.2]
            }
        }
        
        mock_historical_air_quality_data = {
            "hourly": {
                "time": ["2023-05-15T12:00"] * 72,
                "pm10": [20.1] * 72,
                "pm2_5": [12.3] * 72
            }
        }
        
        # Configurar respuestas para los datos históricos (Facade)
        mock_historical_weather_response = Mock()
        mock_historical_weather_response.status_code = 200
        mock_historical_weather_response.json.return_value = mock_historical_weather_data
        
        mock_historical_air_quality_response = Mock()
        mock_historical_air_quality_response.status_code = 200
        mock_historical_air_quality_response.json.return_value = mock_historical_air_quality_data
        
        # Configurar respuesta para la API interna
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {
            "informe": {
                "temperatura": {
                    "max_promedio": 25.4,
                    "min_promedio": 15.4
                },
                "calidad_aire": {
                    "pm10_promedio": 20.1,
                    "pm25_promedio": 12.3
                },
                "tendencias": {},
                "recomendaciones": ["Recomendación de prueba"]
            }
        }
        
        # Configurar el comportamiento de los mocks
        mock_ui_requests.side_effect = [mock_geocoding_response, mock_api_response]
        mock_facade_requests.side_effect = [mock_historical_weather_response, mock_historical_air_quality_response]
        
        # Realizar la solicitud a través de la interfaz web
        response = self.client.get('/historico?ciudad=Madrid&dias=7')
        
        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Madrid', response.data)
        self.assertIn(b'informe', str(response.data).lower())

if __name__ == '__main__':
    unittest.main()