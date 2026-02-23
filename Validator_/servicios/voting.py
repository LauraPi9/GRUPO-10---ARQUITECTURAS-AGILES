"""
Táctica de Votación - Detección de errores en cálculo de facturación.
Envía la misma solicitud a múltiples instancias de Payments y valida por consenso.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import requests
except ImportError:
    requests = None

from Validator_.config import (
    PAYMENTS_INSTANCES,
    DETECTION_THRESHOLD_MS,
    DECIMAL_TOLERANCE,
    PAYMENTS_REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


def _valores_equivalentes(a: float, b: float, tolerancia: float = DECIMAL_TOLERANCE) -> bool:
   
    return abs(float(a) - float(b)) <= tolerancia


def validar_factura_por_votacion(datos_factura: dict) -> dict:
    
    if not requests:
        return {
            "valido": False,
            "total_consensuado": None,
            "falla_detectada": True,
            "tiempo_deteccion_ms": 0,
            "respuestas": [],
            "mensaje": "Dependencia 'requests' no instalada.",
        }

    inicio = time.perf_counter()
    respuestas = []
    urls = [u.strip() for u in PAYMENTS_INSTANCES if u.strip()]

    if len(urls) < 1:
        return {
            "valido": False,
            "total_consensuado": None,
            "falla_detectada": True,
            "tiempo_deteccion_ms": (time.perf_counter() - inicio) * 1000,
            "respuestas": [],
            "mensaje": "No hay URLs de Payments configuradas (PAYMENTS_URLS).",
        }

    def _llamar_instancia(url: str) -> dict:
        t0 = time.perf_counter()
        try:
            
            r = requests.post(url, json=datos_factura, timeout=PAYMENTS_REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
           
            total = data.get("valor") if data.get("valor") is not None else data.get("total")
            tiempo_ms = (time.perf_counter() - t0) * 1000
            return {"url": url, "total": total, "ok": True, "error": None, "tiempo_ms": round(tiempo_ms, 2)}
        except Exception as e:
            tiempo_ms = (time.perf_counter() - t0) * 1000
            return {"url": url, "total": None, "ok": False, "error": str(e), "tiempo_ms": round(tiempo_ms, 2)}

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        futures = {executor.submit(_llamar_instancia, url): url for url in urls}
        for future in as_completed(futures):
            respuestas.append(future.result())

    tiempo_ms = (time.perf_counter() - inicio) * 1000

    
    logger.info(
        "Validator↔Payments | total_ms=%.2f | umbral_500ms=%s | instancias=%s",
        tiempo_ms,
        tiempo_ms < DETECTION_THRESHOLD_MS,
        [(r.get("url"), r.get("tiempo_ms"), "ok" if r.get("ok") else r.get("error")) for r in respuestas],
    )
    for r in respuestas:
        logger.info(
            "Validator↔Payments | url=%s | tiempo_ms=%s | ok=%s",
            r.get("url"), r.get("tiempo_ms"), r.get("ok"),
        )

    
    totales = [r["total"] for r in respuestas if r["ok"] and r["total"] is not None]

    if not totales:
        return {
            "valido": False,
            "total_consensuado": None,
            "falla_detectada": True,
            "tiempo_deteccion_ms": tiempo_ms,
            "respuestas": respuestas,
            "mensaje": "Todas las instancias fallaron o no devolvieron total.",
        }

   
    grupos = []
    usados = set()
    for i, t in enumerate(totales):
        if i in usados:
            continue
        grupo = [t]
        for j, t2 in enumerate(totales):
            if j != i and j not in usados and _valores_equivalentes(t, t2):
                grupo.append(t2)
                usados.add(j)
        usados.add(i)
        grupos.append(grupo)

    if len(totales) == 1:
        hay_consenso = True
        total_consensuado = totales[0]
        falla_detectada = False
        instancias_fallando = []
    else:
        
        grupo_ganador = max(grupos, key=len)
        votos_ganador = len(grupo_ganador)
        total_instancias = len(totales)
        hay_consenso = votos_ganador > total_instancias / 2
        total_consensuado = grupo_ganador[0] if hay_consenso else None
        falla_detectada = len(grupos) > 1 

        instancias_fallando = [
            {"url": r["url"], "valor_devuelto": r["total"]}
            for r in respuestas
            if r.get("ok") and r.get("total") is not None and total_consensuado is not None
            and not _valores_equivalentes(r["total"], total_consensuado)
        ]

    if hay_consenso and not falla_detectada:
        mensaje = "Cálculo validado por votación."
    elif hay_consenso and falla_detectada:
        mensaje = "Mayoría consensuada; se detectaron instancia(s) con valor distinto (ver log)."
    else:
        mensaje = "Falla detectada: divergencia en resultados de Payments (sin mayoría)."

    
    logger.info(
        "Validator↔Payments | falla_detectada=%s | valido=%s | mensaje=%s",
        falla_detectada, hay_consenso, mensaje,
    )
    if instancias_fallando:
        logger.warning(
            "Validator↔Payments | instancia(s) con valor distinto al consenso: %s",
            instancias_fallando,
        )

    return {
        "valido": hay_consenso,
        "total_consensuado": total_consensuado,
        "falla_detectada": falla_detectada,
        "instancias_fallando": instancias_fallando,
        "tiempo_deteccion_ms": round(tiempo_ms, 2),
        "respuestas": respuestas,
        "mensaje": mensaje,
        "cumple_umbral_500ms": tiempo_ms < DETECTION_THRESHOLD_MS,
        "tiempos_por_instancia_ms": [
            {"url": r.get("url"), "tiempo_ms": r.get("tiempo_ms"), "ok": r.get("ok")}
            for r in respuestas
        ],
    }
