"""Lógica de negocio para el carrito de compras."""

from flaskr import db
from flaskr.modelos.modelos import Cart
from flaskr.modelos.enums import CartStatus
from flaskr.servicios.payment_client import PaymentClient
from flaskr.servicios.mappers import reservation_to_payment_payload


class CartService:
    """Servicio que maneja la lógica de negocio del carrito."""

    @staticmethod
    def add_to_cart(payer_id, payer_name, reservation_data):
        """
        Agrega una reserva al carrito y procesa el pago.

        Args:
            payer_id (int): ID del pagador
            payer_name (str): Nombre del pagador
            reservation_data (dict): Datos de la reserva

        Returns:
            tuple: (cart_item: Cart, payment_response: dict, status_code: int)
        """
        # Crear item del carrito
        cart_item = Cart(
            payer_id=payer_id,
            payer_name=payer_name,
            reservation_id=reservation_data.get("id"),
            confirmation_code=reservation_data.get("confirmation_code"),
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

        # Guardar en base de datos
        db.session.add(cart_item)
        db.session.commit()

        # Preparar payload para el servicio de pagos
        payment_payload = reservation_to_payment_payload(
            payer_id=payer_id, payer_name=payer_name, reservation_data=reservation_data
        )

        # Llamar al servicio de pagos
        success, payment_response, status_code = PaymentClient.create_payment(
            payment_payload
        )

        # Actualizar estado del carrito según resultado del pago
        if success:
            cart_item.status = CartStatus.CONFIRMED
        else:
            cart_item.status = CartStatus.FAILED

        db.session.commit()

        return cart_item, payment_response, status_code

    @staticmethod
    def get_cart_by_id(cart_id):
        """
        Obtiene un item del carrito por su ID.

        Args:
            cart_id (int): ID del carrito

        Returns:
            Cart: Item del carrito o None si no existe
        """
        return Cart.query.get(cart_id)

    @staticmethod
    def get_all_carts():
        """
        Obtiene todos los items del carrito.

        Returns:
            list[Cart]: Lista de todos los items del carrito
        """
        return Cart.query.all()
