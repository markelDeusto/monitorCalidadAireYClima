import unittest
from unittest.mock import patch, Mock
import json
from app.facade.aireYClimaFacade import AireYClimaFacade
from datetime import datetime

class TestAireYClimaFacade(unittest.TestCase):
    
    def setUp(self):
        self.facade = AireYClimaFacade()
        # Datos simulados para pruebas
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
                "time": ["2023-05-20T12:00", "2023-05-20T13:00"],
                "pm10": [15.2, 16.7],
                "pm2_5": [8.4, 9.1]
            }
        }
        self.mock_historical_weather_data = {
            "daily": {
                "time": ["2023-05-15", "2023-05-16", "2023-05-17"],
                "temperature_2m_max": [25.3, 24.8, 26.2],
                "temperature_2m_min": [15.1, 14.9, 16.2]
            }
        }
        self.mock_historical_air_quality_data = {
            "hourly": {
                "time": [f"2023-05-15T{h:02d}:00" for h in range(24)] + 
                        [f"2023-05-16T{h:02d}:00" for h in range(24)] + 
                        [f"2023-05-17T{h:02d}:00" for h in range(24)],
                "pm10": [20.1] * 24 + [18.5] * 24 + [22.3] * 24,
                "pm2_5": [12.3] * 24 + [11.8] * 24 + [13.1] * 24
            }
        }

    @patch('app.facade.aireYClimaFacade.requests.get')
    def test_recoger_ultimo_dato(self, mock_requests_get):
        # Configurar las respuestas simuladas
        mock_weather_response = Mock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = self.mock_weather_data
        
        mock_air_quality_response = Mock()
        mock_air_quality_response.status_code = 200
        mock_air_quality_response.json.return_value = self.mock_air_quality_data
        
        # Configurar el comportamiento del mock para retornar las respuestas simuladas
        mock_requests_get.side_effect = [mock_weather_response, mock_air_quality_response]
        
        # Ejecutar la función a probar
        resultado = self.facade.recoger_ultimo_dato(40.4, -3.7)
        
        # Verificar los resultados
        self.assertEqual(resultado['weather'], self.mock_weather_data)
        self.assertEqual(resultado['air_quality'], self.mock_air_quality_data)
        
        # Verificar que se llamó a requests.get con los parámetros correctos
        calls = mock_requests_get.call_args_list
        self.assertEqual(len(calls), 2)
        
        # Verificar la llamada para obtener datos del clima
        weather_args = calls[0][1]
        self.assertEqual(weather_args['params']['latitude'], 40.4)
        self.assertEqual(weather_args['params']['longitude'], -3.7)
        self.assertTrue(weather_args['params']['current_weather'])
        
        # Verificar la llamada para obtener calidad del aire
        air_quality_args = calls[1][1]
        self.assertEqual(air_quality_args['params']['latitude'], 40.4)
        self.assertEqual(air_quality_args['params']['longitude'], -3.7)
        self.assertEqual(air_quality_args['params']['hourly'], "pm10,pm2_5")

    @patch('app.facade.aireYClimaFacade.requests.get')
    def test_obtener_datos_historicos(self, mock_requests_get):
        # Configurar las respuestas simuladas
        mock_weather_response = Mock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = self.mock_historical_weather_data
        
        mock_air_quality_response = Mock()
        mock_air_quality_response.status_code = 200
        mock_air_quality_response.json.return_value = self.mock_historical_air_quality_data
        
        # Configurar el comportamiento del mock
        mock_requests_get.side_effect = [mock_weather_response, mock_air_quality_response]
        
        # Ejecutar la función a probar
        resultado = self.facade.obtener_datos_historicos(40.4, -3.7, 7)
        
        # Verificar los resultados
        self.assertEqual(resultado['weather_historical'], self.mock_historical_weather_data)
        self.assertEqual(resultado['air_quality_historical'], self.mock_historical_air_quality_data)
        
        # Verificar que se llamó a requests.get con los parámetros correctos
        calls = mock_requests_get.call_args_list
        self.assertEqual(len(calls), 2)

    def test_analizar_tendencias(self):
        # Datos para la prueba
        datos_historicos = {
            "weather_historical": self.mock_historical_weather_data,
            "air_quality_historical": self.mock_historical_air_quality_data
        }
        
        # Ejecutar la función a probar
        informe = self.facade.analizar_tendencias(datos_historicos)
        
        # Verificar la estructura del informe
        self.assertIn('temperatura', informe)
        self.assertIn('calidad_aire', informe)
        self.assertIn('tendencias', informe)
        self.assertIn('recomendaciones', informe)
        
        # Verificar cálculos específicos
        temp_info = informe['temperatura']
        self.assertEqual(temp_info['max_promedio'], round(sum(self.mock_historical_weather_data['daily']['temperature_2m_max'])/3, 1))
        self.assertEqual(temp_info['min_promedio'], round(sum(self.mock_historical_weather_data['daily']['temperature_2m_min'])/3, 1))
        self.assertEqual(temp_info['max_registrada'], max(self.mock_historical_weather_data['daily']['temperature_2m_max']))
        self.assertEqual(temp_info['min_registrada'], min(self.mock_historical_weather_data['daily']['temperature_2m_min']))

    def test_generar_recomendaciones(self):
        # Crear un informe simulado para probar las recomendaciones
        informe = {
            "temperatura": {
                "max_registrada": 32,  # Temperatura alta para activar recomendación
                "min_registrada": 4,   # Temperatura baja para activar recomendación
                "variacion": 16        # Variación alta para activar recomendación
            },
            "calidad_aire": {
                "pm25_promedio": 26,   # PM2.5 alto para activar recomendación
                "dias_calidad_mala": 3  # Días malos para activar recomendación
            },
            "tendencias": {
                "temperatura": "al alza",
                "calidad_aire": "empeorando"
            }
        }
        
        # Ejecutar el método privado que se está probando
        self.facade._generar_recomendaciones(informe)
        
        # Verificar que se generaron recomendaciones
        self.assertTrue(len(informe['recomendaciones']) > 0)
        
        # Verificar recomendaciones específicas basadas en las condiciones simuladas
        recomendaciones = informe['recomendaciones']
        self.assertTrue(any('temperaturas altas' in r for r in recomendaciones))
        self.assertTrue(any('temperaturas bajas' in r for r in recomendaciones))
        self.assertTrue(any('variación de temperatura' in r for r in recomendaciones))
        self.assertTrue(any('calidad del aire ha sido deficiente' in r for r in recomendaciones))
        self.assertTrue(any('varios días con mala calidad del aire' in r for r in recomendaciones))
        self.assertTrue(any('tendencia al alza' in r for r in recomendaciones))
        self.assertTrue(any('está empeorando' in r for r in recomendaciones))

if __name__ == '__main__':
    unittest.main()