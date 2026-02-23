
from flask import Blueprint, request, jsonify

from Validator_.servicios.voting import validar_factura_por_votacion

validacion_bp = Blueprint("validacion", __name__, url_prefix="/api")


@validacion_bp.route("/validate-invoice", methods=["POST"])
def validar_factura():
   
    datos = request.get_json(silent=True) or {}
    
    if not datos:
        return jsonify({
            "valido": False,
            "falla_detectada": True,
            "mensaje": "Se requiere body JSON con datos de la factura.",
        }), 400

    resultado = validar_factura_por_votacion(datos)

    
    if resultado["valido"]:
        return jsonify(resultado), 200

   
    return jsonify(resultado), 422


