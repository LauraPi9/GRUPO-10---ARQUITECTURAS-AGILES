from flask_restful import Resource
from ..modelos import db, Pago, PagoScheme, PagoScheme, PagoYInformacionTarjetaDTO, EstadoPago
from flask import request, current_app
import requests

pago_schema = PagoScheme()
pagos_schema = PagoScheme(many=True) 

class VistaPagos(Resource):
    def get(self):
        pagos = Pago.query.all()
        return pagos_schema.dump(pagos), 200
    

    def post(self):
        nueva_solicitud = PagoYInformacionTarjetaDTO(
            payer_id = request.json['payer_id'],
            name = request.json['name'],
            identification_number = request.json['identification_number'],
            payment_method = request.json['payment_method'], #VISA, MASTERCARD
            id_reserva = request.json['id_reserva'],
            number = request.json['number'],
            expiration_date = request.json['expiration_date'],
            valor = request.json['valor'],
        )

        if len(str(nueva_solicitud.number)) < 13 or len(str(nueva_solicitud.number)) > 20:
            return {
                "mensaje": "El tamaño debe estar entre 13 y 20.",
                "detalle": nueva_solicitud.number
            }, 400 

        credit_card_token_data = {
            "payerId": str(nueva_solicitud.payer_id),
            "name": nueva_solicitud.name,
            "identificationNumber":  str(nueva_solicitud.identification_number),
            "paymentMethod":  str(nueva_solicitud.payment_method),
            "number":  str(nueva_solicitud.number),
            "expirationDate":  str(nueva_solicitud.expiration_date),
        }
        
        token_result = PayUService.crear_token(credit_card_token_data)
        token_tarjeta = token_result["token_id"]
        #token_tarjeta = "Fk867I99i#!dFD"

        nuevo_pago = Pago(
            valor=nueva_solicitud.valor,
            token_tarjeta=token_tarjeta,
            id_reserva= nueva_solicitud.id_reserva,
            estado_pago=EstadoPago.PAGADO,
            provedor_de_pago=1
        )

        print(nuevo_pago)

        db.session.add(nuevo_pago)
        db.session.commit()
        return pago_schema.dump(nuevo_pago), 201
    
class VistaPago(Resource):
      def get(self, id_pago):
        pago_encontrado = Pago.query.get_or_404(id_pago)
        return pago_schema.dump(pago_encontrado)

class PayUService:
    @staticmethod
    def crear_token(credit_card_token_data: dict) -> dict:

        payload = {
            "language": "es",
            "command": "CREATE_TOKEN",
            "merchant": {
                "apiLogin": current_app.config["PAYU_API_LOGIN"],
                "apiKey": current_app.config["PAYU_API_KEY"],
            },
            "creditCardToken": credit_card_token_data
        }

        print(credit_card_token_data)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(
            current_app.config["PAYU_URL"],
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()
        print(data)

        token_info = data.get("creditCardToken", {})

        return {
            "code": data.get("code"),
            "token_id": token_info.get("creditCardTokenId"),
            "estado_token": token_info.get("name"),
            "payer_id": token_info.get("payerId"),
            "identification_number": token_info.get("identificationNumber"),
            "payment_method": token_info.get("paymentMethod"),
            "masked_number": token_info.get("maskedNumber"),
            "raw": data,
        }