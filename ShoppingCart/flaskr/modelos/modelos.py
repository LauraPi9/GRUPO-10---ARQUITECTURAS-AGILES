"""Modelos de base de datos para ShoppingCart."""

from flaskr import db
from datetime import datetime
from flaskr.modelos.enums import CartStatus


class Cart(db.Model):
    """
    Modelo para almacenar carritos de compra.
    Representa las reservas agregadas al carrito del usuario.
    """

    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    payer_id = db.Column(db.Integer, nullable=False)
    payer_name = db.Column(db.String(200), nullable=False)
    reservation_id = db.Column(db.Integer, nullable=False)
    confirmation_code = db.Column(db.String(50), nullable=False)
    check_in_date = db.Column(db.String(50), nullable=False)
    check_out_date = db.Column(db.String(50), nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    number_of_nights = db.Column(db.Integer, nullable=False)
    amount_subtotal = db.Column(db.Float, nullable=False)
    amount_taxes = db.Column(db.Float, nullable=False)
    amount_commission = db.Column(db.Float, nullable=False)
    amount_total = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Enum(CartStatus), nullable=False, default=CartStatus.ACTIVE)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Cart {self.id} - Reservation {self.reservation_id}>"
