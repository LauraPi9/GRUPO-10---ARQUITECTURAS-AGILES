"""Cliente HTTP para comunicación con el servicio Validator (táctica de votación)."""

import requests
from flask import current_app


class ValidatorClient:

    @staticmethod
    def validate_invoice(payment_payload):
        
        try:
            validator_url = current_app.config.get("VALIDATOR_SERVICE_URL")
            url = f"{validator_url.rstrip('/')}/api/validate-invoice"

            response = requests.post(
                url,
                json=payment_payload,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            if response.status_code == 200:
                return True, response.json(), response.status_code
            else:
                return (
                    False,
                    response.json() if response.text else {"error": "Validator rejected"},
                    response.status_code,
                )

        except requests.exceptions.Timeout:
            return False, {"error": "Validator service timeout"}, 504
        except requests.exceptions.ConnectionError:
            return False, {"error": "Cannot connect to Validator service"}, 503
        except Exception as e:
            return False, {"error": str(e)}, 500
