# app/ui/interfaz.py
import requests

class Interfaz:
    def __init__(self):
        self.api_url = "http://127.0.0.1:5000/api/aire-clima/actual"

    def ejecutar_programa(self):
        print("Obteniendo datos del clima...")
        response = requests.get(self.api_url)
        if response.status_code == 200:
            print("Datos obtenidos:", response.json())
        else:
            print("Error al obtener datos")

if __name__ == "__main__":
    interfaz = Interfaz()
    interfaz.ejecutar_programa()

