from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import os

def create_app(config_name):
    app=Flask(__name__)

    port = os.getenv("PAYMENTS_PORT", "5001")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///admon_payments_{port}.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "frase-secreta"
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_IDENTITY_CLAIM"] = "sub"
    app.config["PAYU_URL"] = os.getenv(
        "PAYU_URL",
        "https://sandbox.api.payulatam.com/payments-api/4.0/service.cgi"
    )
    app.config["PAYU_API_LOGIN"] = os.getenv("PAYU_API_LOGIN", "pRRXKOl8ikMmt9u")
    app.config["PAYU_API_KEY"] = os.getenv("PAYU_API_KEY", "4Vj8eK4rloUd272L48hsrarnUA")
    # Para experimento de votación: si está activo, esta instancia puede devolver un valor distinto
    app.config["PAYMENTS_INJECT_FAULT"] = os.getenv("PAYMENTS_INJECT_FAULT", "").lower() in ("1", "true", "yes")
    app.config["PAYMENTS_FAULT_PROBABILITY"] = float(os.getenv("PAYMENTS_FAULT_PROBABILITY", "0.5"))

    return app