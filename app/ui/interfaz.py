# app/ui/interfaz.py
from flask import Blueprint, render_template, request
import requests

ui = Blueprint('ui', __name__, template_folder='templates')

def obtener_datos_clima(ciudad):
    # Obtener coordenadas de la ciudad usando una API de geocodificación
    geocoding_url = "https://nominatim.openstreetmap.org/search"
    geocoding_params = {
        "q": ciudad,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "mi-aplicacion-clima/1.0 (contacto@example.com)"  # Cambia el correo por uno válido
    }
    geocoding_response = requests.get(geocoding_url, params=geocoding_params, headers=headers)


    if geocoding_response.status_code == 200 and geocoding_response.text.strip():
        try:
            geocoding_data = geocoding_response.json()
            if geocoding_data:
                location = geocoding_data[0]
                latitude = location["lat"]
                longitude = location["lon"]

                # Llamar a la API interna para obtener datos del clima y calidad del aire
                url = f"http://127.0.0.1:5000/api/aire-clima/actual"
                response = requests.get(url, params={"latitude": latitude, "longitude": longitude})

                if response.status_code == 200:
                    return response.json()
        except ValueError as e:
            print("Error al decodificar JSON de geocodificación:", e)
    return {"error": "No se pudo obtener el dato"}


@ui.route('/')
def mostrar_interfaz():
    ciudad = request.args.get("ciudad", "Vitoria")  # Ciudad por defecto: Madrid
    datos = obtener_datos_clima(ciudad)
    temperatura = datos.get("weather", {}).get("current_weather", {}).get("temperature", "N/A")
    
    # Acceder al primer valor de las listas de PM10 y PM2.5
    air_quality = datos.get("air_quality", {}).get("hourly", {})
    pm10 = air_quality.get("pm10", ["N/A"])[0]  # Primer valor de la lista
    pm2_5 = air_quality.get("pm2_5", ["N/A"])[0]  # Primer valor de la lista
    
    calidad_aire = calcular_calidad_aire(pm10, pm2_5)
    return render_template(
        'index.html',
        temperatura=temperatura,
        pm10=pm10,
        pm2_5=pm2_5,
        calidad_aire=calidad_aire
    )
    
    
def calcular_calidad_aire(pm10, pm2_5):
    if pm10 == "N/A" or pm2_5 == "N/A":
        return "Datos no disponibles"
    if pm10 > 150 or pm2_5 > 75:
        return "Mala calidad"
    elif pm10 > 100 or pm2_5 > 50:
        return "Algo mala"
    elif pm10 > 50 or pm2_5 > 25:
        return "Media"
    elif pm10 > 25 or pm2_5 > 15:
        return "Buena"
    else:
        return "Muy buena"
    

