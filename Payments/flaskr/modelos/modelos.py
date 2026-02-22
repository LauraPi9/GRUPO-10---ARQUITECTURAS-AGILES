import enum
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import validates

db = SQLAlchemy()

class EstadoPago(enum.Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO= "PAGADO"
    ACTIVA = "ACTIVA"
    TEMPORAL = "TEMPORAL"
    CANELADA = "CANCELADA"

class Pago(db.Model):
    __tablename__ = "Pago",
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    token_tarjeta = db.Column(db.String(256), nullable=True)
    estado_pago=db.Column(db.Enum(EstadoPago), nullable=False, default="PENDIENTE")
    provedor_de_pago = db.Column(db.Integer, db.ForeignKey('Provedor_de_Pago.id'))

class PagoYInformacionTarjeta:
    def __init__(self, payer_id, name, identification_number, payment_method, number, expiration_date,valor):
        self.payer_id = payer_id
        self.name = name
        self.identification_number = identification_number
        self.payment_method = payment_method
        self.number = number
        self.expiration_date = expiration_date
        self.valor = valor


class ProvedorPago(db.Model):
    __tablename__ = "Provedor_de_Pago"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128),nullable=False)
    pagos = db.relationship('Pago', cascade='all, delete, delete-orphan')

class EnumDiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {'llave': value.name}

class PagoScheme(SQLAlchemyAutoSchema):
    estado_pago = fields.Enum(EstadoPago,by_value=True)
    class Meta: 
        model = Pago
        include_relationships= True
        load_instance = True