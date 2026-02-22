"""Vistas (controladores) para el carrito de compras."""

from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate, ValidationError
from flaskr.servicios.cart_service import CartService
from flaskr.modelos.enums import Currency, CartStatus


bp = Blueprint("cart", __name__, url_prefix="/cart")


class ReservationSchema(Schema):
    """Schema de validación para datos de reserva."""

    id = fields.Integer(required=True)
    confirmation_code = fields.String(required=True)
    creation_date = fields.String(required=False)
    check_in_date = fields.String(required=True)
    check_out_date = fields.String(required=True)
    number_of_guests = fields.Integer(required=True)
    number_of_nights = fields.Integer(required=True)
    amount_subtotal = fields.Float(required=True)
    amount_taxes = fields.Float(required=True)
    amount_commission = fields.Float(required=True)
    amount_total = fields.Float(required=True)
    currency = fields.String(
        required=True, validate=validate.OneOf([c.value for c in Currency])
    )
    status = fields.String(required=False)


class AddToCartSchema(Schema):
    """Schema de validación para agregar al carrito."""

    payer_id = fields.Integer(required=True)
    payer_name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    reservation = fields.Nested(ReservationSchema, required=True)


class CartItemSchema(Schema):
    """Schema para serializar items del carrito."""

    id = fields.Integer()
    payer_id = fields.Integer()
    payer_name = fields.String()
    reservation_id = fields.Integer()
    confirmation_code = fields.String()
    check_in_date = fields.String()
    check_out_date = fields.String()
    number_of_guests = fields.Integer()
    number_of_nights = fields.Integer()
    amount_subtotal = fields.Float()
    amount_taxes = fields.Float()
    amount_commission = fields.Float()
    amount_total = fields.Float()
    currency = fields.String()
    status = fields.Method("get_status")
    created_at = fields.DateTime()

    def get_status(self, obj):
        """Serializa el enum CartStatus a su nombre."""
        return obj.status.name if hasattr(obj.status, "name") else str(obj.status)


@bp.route("/add", methods=["POST"])
def add_to_cart():
    """
    Endpoint para agregar una reserva al carrito y procesar el pago.

    Valida los datos de entrada, llama al servicio de negocio,
    y retorna la respuesta en JSON.
    """
    try:
        # Validar datos de entrada
        schema = AddToCartSchema()
        data = schema.load(request.get_json())

        # Llamar al servicio de negocio
        cart_item, payment_response, status_code = CartService.add_to_cart(
            payer_id=data["payer_id"],
            payer_name=data["payer_name"],
            reservation_data=data["reservation"],
        )

        # Serializar respuesta
        cart_schema = CartItemSchema()
        cart_data = cart_schema.dump(cart_item)

        return jsonify({"cart": cart_data, "payment": payment_response}), status_code

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:cart_id>", methods=["GET"])
def get_cart_item(cart_id):
    """
    Obtiene un item del carrito por su ID.
    """
    cart_item = CartService.get_cart_by_id(cart_id)

    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    schema = CartItemSchema()
    return jsonify(schema.dump(cart_item)), 200


@bp.route("/", methods=["GET"])
def get_all_carts():
    """
    Obtiene todos los items del carrito.
    """
    carts = CartService.get_all_carts()
    schema = CartItemSchema(many=True)
    return jsonify(schema.dump(carts)), 200


@bp.route("/health", methods=["GET"])
def health():
    """Endpoint de salud del servicio."""
    return jsonify({"status": "healthy", "service": "ShoppingCart"}), 200
