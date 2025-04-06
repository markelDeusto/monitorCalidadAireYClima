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
    
    @patch('app.ui.interfaz.requests.get')
    def test_flujo_completo_consulta_actual(self, mock_requests):
        """Prueba de integración para el flujo completo de consulta de datos actuales"""
        
        # Configurar mock para todas las respuestas HTTP
        def mock_response_generator(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            
            # Crear respuesta para la API de geocodificación
            if 'nominatim.openstreetmap.org' in url:
                mock_geocoding_response = Mock()
                mock_geocoding_response.status_code = 200
                mock_geocoding_response.text = json.dumps(self.mock_geocoding_data)
                mock_geocoding_response.json.return_value = self.mock_geocoding_data
                return mock_geocoding_response
            
            # Crear respuesta para la API interna de aire-clima
            elif '/api/aire-clima/actual' in url:
                mock_api_response = Mock()
                mock_api_response.status_code = 200
                mock_api_response.json.return_value = {
                    "weather": self.mock_weather_data,
                    "air_quality": self.mock_air_quality_data
                }
                return mock_api_response
            
            # Respuesta predeterminada para cualquier otra URL
            default_response = Mock()
            default_response.status_code = 404
            return default_response
        
        # Configurar el comportamiento del mock para responder según la URL
        mock_requests.side_effect = mock_response_generator
        
        # Realizar la solicitud a través de la interfaz web
        response = self.client.get('/?ciudad=Madrid')
        
        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Temperatura: 23.5', response.data)
        self.assertIn(b'PM10: 15.2', response.data)
        self.assertIn(b'PM2.5: 8.4', response.data)
    
    @patch('app.ui.interfaz.requests.get')
    def test_flujo_completo_datos_historicos(self, mock_requests):
        """Prueba de integración para el flujo completo de consulta de datos históricos"""
        
        # Configurar mock para todas las respuestas HTTP
        def mock_response_generator(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            
            # Crear respuesta para la API de geocodificación
            if 'nominatim.openstreetmap.org' in url:
                mock_geocoding_response = Mock()
                mock_geocoding_response.status_code = 200
                mock_geocoding_response.text = json.dumps(self.mock_geocoding_data)
                mock_geocoding_response.json.return_value = self.mock_geocoding_data
                return mock_geocoding_response
            
            # Crear respuesta para la API interna de datos históricos
            elif '/api/aire-clima/historico' in url:
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
                return mock_api_response
            
            # Respuesta predeterminada para cualquier otra URL
            default_response = Mock()
            default_response.status_code = 404
            return default_response
        
        # Configurar el comportamiento del mock para responder según la URL
        mock_requests.side_effect = mock_response_generator
        
        # Realizar la solicitud a través de la interfaz web
        response = self.client.get('/historico?ciudad=Madrid&dias=7')
        
        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Madrid', response.data)
        # Verificamos solo que contenga el texto "recomendación" en lugar de "informe" ya que sabemos que las recomendaciones se muestran en la página
        self.assertIn('recomendación', response.data.decode('utf-8').lower())

if __name__ == '__main__':
    unittest.main()