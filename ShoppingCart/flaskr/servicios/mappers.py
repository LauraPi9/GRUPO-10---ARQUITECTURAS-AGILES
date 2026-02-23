"""Mappers para transformar datos entre servicios."""


def reservation_to_payment_payload(payer_id, payer_name, reservation_data):
   
    return {
        "payer_id": payer_id,
        "name": payer_name,
        "identification_number": 1212121,  # Quemado
        "payment_method": "VISA",  # Quemado
        "id_reserva": reservation_data.get("id"),
        "number": "4037997623271984",  # Quemado
        "expiration_date": "2027/04",  # Quemado
        "valor": float(reservation_data.get("amount_total") or 0),
    }
