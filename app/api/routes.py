# app/api/routes.py
from flask import Blueprint, jsonify
from app.facade.aireYClimaFacade import AireYClimaFacade

api = Blueprint('api', __name__)
fachada = AireYClimaFacade()

@api.route('/api/aire-clima/actual', methods=['GET'])
def obtener_dato_actual():
    datos = fachada.recoger_ultimo_dato()
    return jsonify(datos)

