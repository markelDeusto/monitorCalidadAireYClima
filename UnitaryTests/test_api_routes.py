import unittest
from unittest.mock import patch, Mock
from flask import Flask
import json
from app.api.routes import api

class TestApiRoutes(unittest.TestCase):
    
    def setUp(self):
        # Crear una aplicación Flask de prueba
        self.app = Flask(__name__)
        self.app.register_blueprint(api)
        self.client = self.app.test_client()
        
        # Datos simulados para las respuestas
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
        self.mock_datos = {
            "weather": self.mock_weather_data,
            "air_quality": self.mock_air_quality_data
        }
        
        # Datos históricos simulados
        self.mock_datos_historicos = {
            "weather_historical": {
                "daily": {
                    "time": ["2023-05-15", "2023-05-16", "2023-05-17"],
                    "temperature_2m_max": [25.3, 24.8, 26.2],
                    "temperature_2m_min": [15.1, 14.9, 16.2]
                }
            },
            "air_quality_historical": {
                "hourly": {
                    "time": ["2023-05-15T12:00"] * 72,
                    "pm10": [20.1] * 72,
                    "pm2_5": [12.3] * 72
                }
            }
        }
        
        self.mock_informe = {
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
    
    @patch('app.api.routes.fachada.recoger_ultimo_dato')
    def test_obtener_dato_actual(self, mock_recoger_ultimo_dato):
        # Configurar el mock
        mock_recoger_ultimo_dato.return_value = self.mock_datos
        
        # Realizar solicitud a la API con parámetros válidos
        response = self.client.get('/api/aire-clima/actual?latitude=40.4&longitude=-3.7')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, self.mock_datos)
        
        # Verificar que se llamó al método de la fachada con los parámetros correctos
        mock_recoger_ultimo_dato.assert_called_once_with(40.4, -3.7)
        
        # Probar con parámetros faltantes
        response = self.client.get('/api/aire-clima/actual')
        self.assertEqual(response.status_code, 400)
        
    @patch('app.api.routes.fachada.obtener_datos_historicos')
    @patch('app.api.routes.fachada.analizar_tendencias')
    def test_obtener_datos_historicos(self, mock_analizar_tendencias, mock_obtener_datos_historicos):
        # Configurar los mocks
        mock_obtener_datos_historicos.return_value = self.mock_datos_historicos
        mock_analizar_tendencias.return_value = self.mock_informe
        
        # Realizar solicitud a la API con parámetros válidos
        response = self.client.get('/api/aire-clima/historico?latitude=40.4&longitude=-3.7&dias=7')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["datos_historicos"], self.mock_datos_historicos)
        self.assertEqual(data["informe"], self.mock_informe)
        
        # Verificar que se llamaron a los métodos de la fachada con los parámetros correctos
        mock_obtener_datos_historicos.assert_called_once_with(40.4, -3.7, 7)
        mock_analizar_tendencias.assert_called_once_with(self.mock_datos_historicos)
        
        # Probar con parámetros faltantes
        response = self.client.get('/api/aire-clima/historico')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()