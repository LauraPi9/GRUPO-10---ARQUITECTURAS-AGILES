"""Lógica de negocio para el carrito de compras."""

from flaskr import db
from flaskr.modelos.modelos import Cart
from flaskr.modelos.enums import CartStatus
from flaskr.servicios.payment_client import PaymentClient
from flaskr.servicios.validator_client import ValidatorClient
from flaskr.servicios.mappers import reservation_to_payment_payload


class CartService:


    @staticmethod
    def add_to_cart(payer_id, payer_name, reservation_data):

        confirmation_code = reservation_data.get("confirmation_code") or f"RES-{reservation_data.get('id', 0)}"
        cart_item = Cart(
            payer_id=payer_id,
            payer_name=payer_name,
            reservation_id=reservation_data.get("id"),
            confirmation_code=confirmation_code,
            check_in_date=reservation_data.get("check_in_date"),
            check_out_date=reservation_data.get("check_out_date"),
            number_of_guests=reservation_data.get("number_of_guests"),
            number_of_nights=reservation_data.get("number_of_nights"),
            amount_subtotal=reservation_data.get("amount_subtotal"),
            amount_taxes=reservation_data.get("amount_taxes"),
            amount_commission=reservation_data.get("amount_commission"),
            amount_total=reservation_data.get("amount_total"),
            currency=reservation_data.get("currency"),
            status=CartStatus.ACTIVE,
        )

        
        db.session.add(cart_item)
        db.session.commit()

        
        payment_payload = reservation_to_payment_payload(
            payer_id=payer_id, payer_name=payer_name, reservation_data=reservation_data
        )

        
        validation_ok, validation_response, validation_status = ValidatorClient.validate_invoice(
            payment_payload
        )
        if not validation_ok:
            cart_item.status = CartStatus.FAILED
            db.session.commit()
            return cart_item, validation_response, validation_status

        
        success, payment_response, status_code = PaymentClient.create_payment(
            payment_payload
        )

        
        if success:
            cart_item.status = CartStatus.CONFIRMED
        else:
            cart_item.status = CartStatus.FAILED

        db.session.commit()

        return cart_item, payment_response, status_code

    @staticmethod
    def get_cart_by_id(cart_id):
        
        return Cart.query.get(cart_id)

    @staticmethod
    def get_all_carts():
        
        return Cart.query.all()
