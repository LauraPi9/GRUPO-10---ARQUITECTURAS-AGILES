"""Mappers para transformar datos entre servicios."""


def reservation_to_payment_payload(payer_id, payer_name, reservation_data):
    """
    Transforma datos de reserva al formato esperado por el servicio de pagos.

    Args:
        payer_id (int): ID del pagador
        payer_name (str): Nombre del pagador
        reservation_data (dict): Datos de la reserva

    Returns:
        dict: Payload formateado para el servicio de pagos
    """
    return {
        "payer_id": payer_id,
        "name": payer_name,
        "identification_number": 1212121,  # Quemado
        "payment_method": "VISA",  # Quemado
        "id_reserva": reservation_data.get("id"),
        "number": "4037997623271984",  # Quemado
        "expiration_date": "2027/04",  # Quemado
        "valor": reservation_data.get("amount_total"),
    }
