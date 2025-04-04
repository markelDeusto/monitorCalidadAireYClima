# app/facade/aireYClimaFacade.py
import requests
from datetime import datetime, timedelta
import statistics

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

    def obtener_datos_historicos(self, latitude, longitude, dias=7):
        """
        Obtiene datos históricos de clima y calidad del aire.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            dias: Número de días hacia atrás para obtener datos (por defecto 7)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=dias)
        
        # Formato de fechas para la API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Parámetros para datos históricos de clima
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
        
        # Parámetros para datos históricos de calidad del aire
        air_quality_params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "hourly": "pm10,pm2_5",
            "timezone": "auto"
        }
        
        # Obtener datos históricos del clima
        weather_response = requests.get(self.weather_api_url, params=weather_params)
        weather_data = weather_response.json() if weather_response.status_code == 200 else {}
        
        # Obtener datos históricos de calidad del aire
        air_quality_response = requests.get(self.air_quality_api_url, params=air_quality_params)
        air_quality_data = air_quality_response.json() if air_quality_response.status_code == 200 else {}
        
        return {
            "weather_historical": weather_data,
            "air_quality_historical": air_quality_data
        }
    
    def analizar_tendencias(self, datos_historicos):
        """
        Analiza tendencias en los datos históricos para generar un informe.
        """
        informe = {
            "temperatura": {},
            "calidad_aire": {},
            "tendencias": {},
            "recomendaciones": []
        }
        
        # Analizar datos del clima
        try:
            if "weather_historical" in datos_historicos and "daily" in datos_historicos["weather_historical"]:
                temps_max = datos_historicos["weather_historical"]["daily"].get("temperature_2m_max", [])
                temps_min = datos_historicos["weather_historical"]["daily"].get("temperature_2m_min", [])
                fechas = datos_historicos["weather_historical"]["daily"].get("time", [])
                
                if temps_max and temps_min:
                    informe["temperatura"] = {
                        "max_promedio": round(statistics.mean(temps_max), 1),
                        "min_promedio": round(statistics.mean(temps_min), 1),
                        "max_registrada": round(max(temps_max), 1),
                        "min_registrada": round(min(temps_min), 1),
                        "variacion": round(max(temps_max) - min(temps_min), 1)
                    }
                    
                    # Detectar tendencia de temperatura
                    if len(temps_max) > 3:
                        tendencia_temp = "estable"
                        if temps_max[-1] > temps_max[0] + 2:
                            tendencia_temp = "al alza"
                        elif temps_max[-1] < temps_max[0] - 2:
                            tendencia_temp = "a la baja"
                        informe["tendencias"]["temperatura"] = tendencia_temp
        except Exception as e:
            informe["errores"] = informe.get("errores", []) + [f"Error analizando clima: {str(e)}"]
            
        # Analizar datos de calidad del aire
        try:
            if "air_quality_historical" in datos_historicos and "hourly" in datos_historicos["air_quality_historical"]:
                pm10_values = datos_historicos["air_quality_historical"]["hourly"].get("pm10", [])
                pm25_values = datos_historicos["air_quality_historical"]["hourly"].get("pm2_5", [])
                
                if pm10_values and pm25_values:
                    # Agrupar por día para tener valores diarios
                    pm10_diario = [pm10_values[i:i+24] for i in range(0, len(pm10_values), 24)]
                    pm25_diario = [pm25_values[i:i+24] for i in range(0, len(pm25_values), 24)]
                    
                    # Calcular promedios diarios
                    pm10_promedios = [statistics.mean(dia) for dia in pm10_diario if dia]
                    pm25_promedios = [statistics.mean(dia) for dia in pm25_diario if dia]
                    
                    informe["calidad_aire"] = {
                        "pm10_promedio": round(statistics.mean(pm10_values), 2),
                        "pm25_promedio": round(statistics.mean(pm25_values), 2),
                        "pm10_max": round(max(pm10_values), 2),
                        "pm25_max": round(max(pm25_values), 2),
                        "dias_calidad_mala": sum(1 for pm10, pm25 in zip(pm10_promedios, pm25_promedios) if pm10 > 50 or pm25 > 25)
                    }
                    
                    # Detectar tendencia de calidad del aire
                    if len(pm10_promedios) > 3:
                        tendencia_aire = "estable"
                        if pm10_promedios[-1] > pm10_promedios[0] * 1.2:
                            tendencia_aire = "empeorando"
                        elif pm10_promedios[-1] < pm10_promedios[0] * 0.8:
                            tendencia_aire = "mejorando"
                        informe["tendencias"]["calidad_aire"] = tendencia_aire
        except Exception as e:
            informe["errores"] = informe.get("errores", []) + [f"Error analizando calidad del aire: {str(e)}"]
        
        # Generar recomendaciones
        self._generar_recomendaciones(informe)
        
        return informe
    
    def _generar_recomendaciones(self, informe):
        """Genera recomendaciones basadas en el análisis de datos."""
        recomendaciones = []
        
        # Recomendaciones por temperatura
        if "temperatura" in informe:
            if informe["temperatura"].get("max_registrada", 0) > 30:
                recomendaciones.append("Se han registrado temperaturas altas. Recuerde mantenerse hidratado y evitar la exposición directa al sol durante horas pico.")
            if informe["temperatura"].get("min_registrada", 20) < 5:
                recomendaciones.append("Se han registrado temperaturas bajas. Abríguese adecuadamente para evitar resfriados.")
            if informe["temperatura"].get("variacion", 0) > 15:
                recomendaciones.append("Hay gran variación de temperatura durante el período. Vístase en capas para adaptarse a los cambios.")
        
        # Recomendaciones por calidad del aire
        if "calidad_aire" in informe:
            if informe["calidad_aire"].get("pm25_promedio", 0) > 25:
                recomendaciones.append("La calidad del aire ha sido deficiente. Considere reducir actividades al aire libre, especialmente si tiene problemas respiratorios.")
            if informe["calidad_aire"].get("dias_calidad_mala", 0) >= 3:
                recomendaciones.append("Ha habido varios días con mala calidad del aire. Use mascarilla si necesita salir en días de alta contaminación.")
            
        # Recomendaciones por tendencias
        if "tendencias" in informe:
            if informe["tendencias"].get("temperatura") == "al alza":
                recomendaciones.append("La temperatura muestra una tendencia al alza. Prevea medidas para el calor en los próximos días.")
            if informe["tendencias"].get("calidad_aire") == "empeorando":
                recomendaciones.append("La calidad del aire está empeorando. Manténgase informado sobre niveles de contaminación.")
        
        informe["recomendaciones"] = recomendaciones