"""Enumeraciones para el dominio del carrito de compras."""

import enum


class CartStatus(enum.Enum):
    """Estados del ciclo de vida del carrito durante el proceso de pago."""

    ACTIVE = 1  # Item agregado al carrito, pago no procesado
    CONFIRMED = 2  # Pago procesado exitosamente
    FAILED = 3  # Pago rechazado o fallido


class Currency(enum.Enum):
    """Monedas soportadas por el sistema."""

    USD = "USD"
    COP = "COP"
    PEN = "PEN"
    ECU = "ECU"
    MXN = "MXN"
    CLP = "CLP"
    ARS = "ARS"
