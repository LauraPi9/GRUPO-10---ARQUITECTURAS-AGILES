"""Cliente HTTP para comunicación con el servicio de pagos."""

import requests
from flask import current_app


class PaymentClient:
    """Cliente para realizar llamadas al servicio de pagos."""

    @staticmethod
    def create_payment(payment_data):
        
        try:
            payment_service_url = current_app.config.get("PAYMENT_SERVICE_URL")
            url = f"{payment_service_url}/pagos"

            response = requests.post(
                url,
                json=payment_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code in [200, 201]:
                return True, response.json(), response.status_code
            else:
                return (
                    False,
                    response.json() if response.text else {},
                    response.status_code,
                )

        except requests.exceptions.Timeout:
            return False, {"error": "Payment service timeout"}, 504
        except requests.exceptions.ConnectionError:
            return False, {"error": "Cannot connect to payment service"}, 503
        except Exception as e:
            return False, {"error": str(e)}, 500
