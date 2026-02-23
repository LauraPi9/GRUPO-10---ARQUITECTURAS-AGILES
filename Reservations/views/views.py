from datetime import date, datetime

import requests
from flask import request
from flask_restful import Resource
from requests.exceptions import RequestException

from models import Currency, Reservation, ReservationSchema, ReservationStatus, db

reservation_schema = ReservationSchema()

PERCENTAGE_COMMISSION = 0.03

country_taxes_dict = {
    Currency.USD: 0.13,
    Currency.COP: 0.19,
    Currency.PEN: 0.20,
    Currency.ECU: 0.16,
    Currency.MXN: 0.17,
    Currency.CLP: 0.10,
    Currency.ARS: 0.25,
}


def calculate_amounts(amount_subtotal, currency):
    amount_taxes = amount_subtotal * country_taxes_dict[Currency[currency]]
    amount_commission = amount_subtotal * PERCENTAGE_COMMISSION
    amount_total = amount_subtotal + amount_taxes + amount_commission

    return amount_subtotal, amount_taxes, amount_commission, amount_total


class ReservationView(Resource):
    
    def post(self):
        amount_subtotal, amount_taxes, amount_commission, amount_total = (
            calculate_amounts(request.json["amount_subtotal"], request.json["currency"])
        )

        new_reservation = Reservation(
            creation_date=datetime.fromisoformat(request.json["creation_date"]),
            check_in_date=date.fromisoformat(request.json["check_in_date"]),
            check_out_date=date.fromisoformat(request.json["check_out_date"]),
            number_of_guests=request.json["number_of_guests"],
            number_of_nights=request.json["number_of_nights"],
            amount_subtotal=amount_subtotal,
            amount_taxes=amount_taxes,
            amount_commission=amount_commission,
            amount_total=amount_total,
            currency=request.json["currency"],
            status=ReservationStatus.PENDING,
        )

        try:
            db.session.add(new_reservation)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"status_code": 500, "message": "Internal server error"}, 500

        json_reservation = reservation_schema.dump(new_reservation)

        json_reservation["confirmation_code"] = (
            json_reservation.get("confirmation_code") or f"RES-{new_reservation.id}"
        )
        json_reservation["status"] = "CREATED"
        for key in ("amount_subtotal", "amount_taxes", "amount_commission", "amount_total"):
            if key in json_reservation and json_reservation[key] is not None:
                json_reservation[key] = float(json_reservation[key])

        json_shopping_cart = {
            "payer_id": 1,
            "payer_name": "TEST",
            "reservation": json_reservation,
        }

        try:
            shopping_cart_response = requests.post(
                "http://localhost:5002/cart/add", json=json_shopping_cart, timeout=60
            )
            shopping_cart_response.raise_for_status()
        except RequestException:
            db.session.rollback()
            return {
                "status_code": 400,
                "message": "An error occurred while adding the reservation to the shopping cart.",
            }, 400

        return {
            "status_code": 201,
            "message": "Reservation successfully created",
            "reservation": json_reservation,
        }, 201
