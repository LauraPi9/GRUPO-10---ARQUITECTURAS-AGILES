from flaskr import create_app
from flaskr.modelos.modelos import db, Pago, EstadoPago, ProvedorPago
from flaskr.modelos.modelos import PagoScheme
from flask_restful import Api
from flaskr.vistas import VistaPagos, VistaPago

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaPagos,'/pagos')
api.add_resource(VistaPago,'/pago/<int:id_pago>')

with app.app_context():
    pago_esquema = PagoScheme()
    pago1 = Pago(
        valor = 54523.25,
        id_reserva= 1,
        token_tarjeta= "errIuyhk7394hhKKK00jKUU",
        estado_pago = EstadoPago.PENDIENTE,
    )

    pago2 = Pago(
        valor =10000,
         id_reserva= 2,
        token_tarjeta="J098h@$Fjqjsd423f",
        estado_pago= EstadoPago.PAGADO,
    )

    mercado_pago = ProvedorPago(
        nombre = "Mercado Pago",
        pagos = [pago1]
    )

    payU = ProvedorPago(
        nombre = "PayU",
        pagos = [pago2]
    )

    db.session.add(pago1)
    db.session.add(pago2)
    db.session.add(mercado_pago)
    db.session.add(payU)
    db.session.commit()
    print([pago_esquema.dumps(pago) for pago in Pago.query.all()])
    print(ProvedorPago.query.all())

if __name__ == "__main__":
    import os
    port = int(os.getenv("PAYMENTS_PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
