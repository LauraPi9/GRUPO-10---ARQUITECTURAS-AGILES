
import os

#3 instancias en 5001, 5003 y 5004.
PAYMENTS_INSTANCES = os.getenv(
    "PAYMENTS_URLS",
    "http://localhost:5001/pagos,http://localhost:5003/pagos,http://localhost:5004/pagos",
).split(",")

# Umbral de detección en milisegundos (HU06)
DETECTION_THRESHOLD_MS = 500

# Timeout en segundos para cada llamada a Payments (PayU puede tardar varios segundos)
PAYMENTS_REQUEST_TIMEOUT = int(os.getenv("PAYMENTS_REQUEST_TIMEOUT", "20"))

DECIMAL_TOLERANCE = 0.01
