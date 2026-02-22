import enum

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Currency(enum.Enum):
    USD = "USD"
    COP = "COP"
    PEN = "PEN"
    ECU = "ECU"
    MXN = "MXN"
    CLP = "CLP"
    ARS = "ARS"


class ReservationStatus(enum.Enum):
    PENDING = 1
    CONFIRMED = 2
    ONGONING = 3
    COMPLETED = 4
    CANCELED = 5


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmation_code = db.Column(db.String(16), nullable=True)
    creation_date = db.Column(db.DateTime)
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    number_of_guests = db.Column(db.Integer)
    number_of_nights = db.Column(db.Integer)
    amount_subtotal = db.Column(db.Numeric(10, 2))
    amount_taxes = db.Column(db.Numeric(10, 2))
    amount_commission = db.Column(db.Numeric(10, 2))
    amount_total = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.Enum(Currency))
    status = db.Column(db.Enum(ReservationStatus))


class ReservationSchema(SQLAlchemyAutoSchema):
    amount_subtotal = fields.Float()
    amount_taxes = fields.Float()
    amount_commission = fields.Float()
    amount_total = fields.Float()
    currency = fields.Enum(Currency, by_value=True)
    status = fields.Enum(ReservationStatus, by_value=True)

    class Meta:
        model = Reservation
        load_instance = True
