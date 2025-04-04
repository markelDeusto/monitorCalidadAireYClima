# app/ui/interfaz.py
from flask import Blueprint, render_template
import requests

ui = Blueprint('ui', __name__, template_folder='templates')

# app/ui/interfaz.py
from flask import Blueprint, render_template
import requests

ui = Blueprint('ui', __name__, template_folder='templates')

def obtener_datos_clima():
    url = "http://127.0.0.1:5000/api/aire-clima/actual"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": "No se pudo obtener el dato"}

@ui.route('/')
def mostrar_interfaz():
    datos = obtener_datos_clima()
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
    

