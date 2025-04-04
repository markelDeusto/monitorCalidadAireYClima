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
    temperatura = datos.get("current", {}).get("temperature_2m", "N/A")
    return render_template('index.html', temperatura=temperatura)
