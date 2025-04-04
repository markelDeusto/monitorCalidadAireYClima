from flask import Blueprint, jsonify, request
from app.facade.aireYClimaFacade import AireYClimaFacade

api = Blueprint('api', __name__)
fachada = AireYClimaFacade()

@api.route('/api/aire-clima/actual', methods=['GET'])
def obtener_dato_actual():
    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    if latitude is None or longitude is None:
        return jsonify({"error": "Faltan parámetros de latitud o longitud"}), 400
    datos = fachada.recoger_ultimo_dato(latitude, longitude)
    return jsonify(datos)

@api.route('/api/aire-clima/historico', methods=['GET'])
def obtener_datos_historicos():
    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    dias = request.args.get("dias", default=7, type=int)
    
    if latitude is None or longitude is None:
        return jsonify({"error": "Faltan parámetros de latitud o longitud"}), 400
    
    # Obtener datos históricos
    datos_historicos = fachada.obtener_datos_historicos(latitude, longitude, dias)
    
    # Analizar tendencias
    informe = fachada.analizar_tendencias(datos_historicos)
    
    # Combinar los datos históricos con el informe
    resultado = {
        "datos_historicos": datos_historicos,
        "informe": informe
    }
    
    return jsonify(resultado)