"""Inicializador del paquete flaskr."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config=None):
    """Factory function para crear la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)

    
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + os.path.join(app.instance_path, "shopping_cart.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PAYMENT_SERVICE_URL=os.getenv("PAYMENT_SERVICE_URL", "http://localhost:5001"),
        VALIDATOR_SERVICE_URL=os.getenv("VALIDATOR_SERVICE_URL", "http://localhost:5000"),
    )

    if config:
        app.config.update(config)

   
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

   
    db.init_app(app)
    ma.init_app(app)

    
    from flaskr.vistas import vistas

    app.register_blueprint(vistas.bp)

    
    with app.app_context():
        db.create_all()

    return app
