import unittest
from unittest.mock import patch, Mock
from flask import Flask, template_rendered
import json
from contextlib import contextmanager
from app.ui.interfaz import ui, calcular_calidad_aire, obtener_coordenadas

@contextmanager
def captured_templates(app):
    """Contexto para capturar las plantillas renderizadas por Flask"""
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class TestInterfaz(unittest.TestCase):
    
    def setUp(self):
        # Crear una aplicación Flask de prueba
        self.app = Flask(__name__)
        self.app.register_blueprint(ui)
        self.client = self.app.test_client()
        
        # Datos simulados para las respuestas
        self.mock_clima_response = {
            "weather": {
                "current_weather": {
                    "temperature": 23.5
                }
            },
            "air_quality": {
                "hourly": {
                    "pm10": [15.2],
                    "pm2_5": [8.4]
                }
            }
        }
        
        # Datos simulados para geocodificación
        self.mock_geocoding_data = [
            {
                "lat": "40.4",
                "lon": "-3.7",
                "display_name": "Madrid"
            }
        ]
    
    def test_calcular_calidad_aire(self):
        # Probar diferentes escenarios de calidad del aire
        self.assertEqual(calcular_calidad_aire("N/A", 10), "Datos no disponibles")
        self.assertEqual(calcular_calidad_aire(10, "N/A"), "Datos no disponibles")
        self.assertEqual(calcular_calidad_aire(160, 80), "Mala calidad")
        self.assertEqual(calcular_calidad_aire(120, 40), "Algo mala")
        self.assertEqual(calcular_calidad_aire(60, 20), "Media")
        self.assertEqual(calcular_calidad_aire(30, 10), "Buena")
        self.assertEqual(calcular_calidad_aire(20, 10), "Muy buena")
    
    @patch('app.ui.interfaz.obtener_datos_clima')
    def test_mostrar_interfaz(self, mock_obtener_datos_clima):
        # Configurar el mock
        mock_obtener_datos_clima.return_value = self.mock_clima_response
        
        # Capturar la plantilla renderizada
        with captured_templates(self.app) as templates:
            response = self.client.get('/?ciudad=Madrid')
            
            # Verificar la respuesta
            self.assertEqual(response.status_code, 200)
            
            # Verificar la plantilla y contexto
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'index.html')
            self.assertEqual(context['temperatura'], 23.5)
            self.assertEqual(context['pm10'], 15.2)
            self.assertEqual(context['pm2_5'], 8.4)
            
            # Verificar que se llamó al método con la ciudad correcta
            mock_obtener_datos_clima.assert_called_once_with('Madrid')
    
    @patch('app.ui.interfaz.requests.get')
    def test_obtener_coordenadas(self, mock_requests_get):
        # Configurar la respuesta simulada
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_geocoding_data)
        mock_response.json.return_value = self.mock_geocoding_data
        mock_requests_get.return_value = mock_response
        
        # Ejecutar la función
        lat, lon = obtener_coordenadas("Madrid")
        
        # Verificar resultados
        self.assertEqual(lat, 40.4)
        self.assertEqual(lon, -3.7)
        
        # Probar comportamiento con error
        mock_response.status_code = 404
        lat, lon = obtener_coordenadas("CiudadInexistente")
        self.assertIsNone(lat)
        self.assertIsNone(lon)
    
    @patch('app.ui.interfaz.obtener_coordenadas')
    @patch('app.ui.interfaz.requests.get')
    def test_mostrar_historico(self, mock_requests_get, mock_obtener_coordenadas):
        # Configurar los mocks
        mock_obtener_coordenadas.return_value = (40.4, -3.7)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "informe": {
                "temperatura": {"max_promedio": 25.4},
                "calidad_aire": {"pm10_promedio": 20.1},
                "tendencias": {},
                "recomendaciones": ["Recomendación de prueba"]
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Capturar la plantilla renderizada
        with captured_templates(self.app) as templates:
            response = self.client.get('/historico?ciudad=Madrid&dias=7')
            
            # Verificar la respuesta
            self.assertEqual(response.status_code, 200)
            
            # Verificar la plantilla y contexto
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'historico.html')
            self.assertEqual(context['ciudad'], 'Madrid')
            self.assertEqual(context['dias'], 7)
            self.assertIn('informe', context)

if __name__ == '__main__':
    unittest.main()