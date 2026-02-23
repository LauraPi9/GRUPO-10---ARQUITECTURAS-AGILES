from flask import Flask

from Validator_.vistas.validacion import validacion_bp


def create_app(config_name="default"):
    app = Flask(__name__)
    app.register_blueprint(validacion_bp)

    import logging
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "validator_payments.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    app.logger.info("Validator logging to %s", log_file)

    return app