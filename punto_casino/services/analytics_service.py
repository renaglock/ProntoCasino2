"""Analítica local (método MJV): guarda eventos de uso en data/analytics_events.json y los resume."""

import json
import logging
import os
import zlib
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

_DATA = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "data")
ARCHIVO = os.path.join(_DATA, "analytics_events.json")
REMOTE_CONFIG = os.path.join(_DATA, "remote_config.json")


def leer_eventos() -> List[Dict[str, Any]]:
    """Todos los eventos guardados; lista vacía si el archivo no existe o está corrupto."""
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # primera ejecución: aún no hay eventos
    except (OSError, json.JSONDecodeError) as e:
        logging.warning(f"No se pudo leer {ARCHIVO}: {e}")
        return []


def variante_ab(id_usuario: str) -> str:
    """Variante del A/B de la pasarela según data/remote_config.json; 'A' si está apagado o falla.
    El hash del usuario lo deja siempre en la misma variante."""
    try:
        with open(REMOTE_CONFIG, "r", encoding="utf-8") as f:
            exp = json.load(f)["ab_pasarela"]
        if not exp.get("activo"):
            return "A"
        return "B" if zlib.crc32(id_usuario.encode()) % 100 < exp.get("porcentaje_b", 50) else "A"
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        logging.warning(f"remote_config inválido, se usa la variante A: {e}")
        return "A"


def registrar_evento(nombre: str, datos: Optional[Dict[str, Any]] = None) -> None:
    """Agrega un evento {evento, fecha, datos} al JSON local. Nunca rompe el flujo de la app."""
    try:
        eventos = leer_eventos()
        eventos.append({"evento": nombre, "fecha": datetime.now().isoformat(timespec="seconds"), "datos": datos or {}})
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(eventos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Fallo analítica [{nombre}]: {e}")


PASOS_FUNNEL = ["app_abierta", "login_exitoso", "pedido_creado"]


def funnel() -> List[tuple]:
    """(paso, sesiones, % respecto del primer paso). Cada app_abierta inicia una sesión;
    una sesión cuenta en un paso si llegó a ese paso y a todos los anteriores."""
    sesiones: List[set] = []
    for e in leer_eventos():
        if e["evento"] == PASOS_FUNNEL[0]:
            sesiones.append(set())
        elif sesiones:
            sesiones[-1].add(e["evento"])
    base = len(sesiones)
    resultado = []
    for i, paso in enumerate(PASOS_FUNNEL):
        n = sum(1 for s in sesiones if all(p in s for p in PASOS_FUNNEL[1:i + 1]))
        resultado.append((paso, n, round(n / base * 100, 1) if base else 0.0))
    return resultado


def items_de(order) -> List[Dict[str, Any]]:
    """Productos de una comanda en formato compacto para los eventos."""
    return [{"product_id": i.product_id, "nombre": i.name, "cantidad": i.quantity} for i in order.items]


def resumen() -> Dict[str, Any]:
    """Calcula las métricas de la matriz MJV a partir de los eventos guardados."""
    eventos = leer_eventos()
    creados = [e["datos"] for e in eventos if e["evento"] == "pedido_creado"]
    perdidos = [e["datos"] for e in eventos if e["evento"] == "pedido_perdido"]
    retiros = [e["datos"] for e in eventos if e["evento"] == "reserva_retirada"]

    ventas: Counter = Counter()
    for d in creados:
        for it in d["items"]:
            ventas[it["nombre"]] += it["cantidad"]
    # La reserva sin pago cuenta como un medio de pago más ("Reserva (paga en caja)")
    medios = Counter("RESERVA_CAJA" if d["es_reserva"] else d["medio_pago"] for d in creados)
    tiempos = [d["segundos_flujo"] for d in creados if d.get("segundos_flujo") is not None]

    reservas = sum(1 for d in creados if d["es_reserva"])
    vencidas = sum(1 for d in perdidos if d["motivo"] == "reserva_vencida")
    return {
        "mas_vendidos": ventas.most_common(5),
        "menos_vendidos": sorted(ventas.items(), key=lambda x: x[1])[:5],
        "medios_pago": medios.most_common(),
        "segundos_flujo_promedio": round(sum(tiempos) / len(tiempos)) if tiempos else None,
        "perdida_clp": sum(d["monto"] for d in perdidos),
        "perdida_por_motivo": dict(Counter(d["motivo"] for d in perdidos)),
        "reservas_creadas": reservas,
        "reservas_retiradas": len(retiros),
        "reservas_vencidas": vencidas,
        "tasa_retiro_pct": round(len(retiros) / reservas * 100, 1) if reservas else None,
        "minutos_retiro_promedio": round(sum(r["minutos_hasta_retiro"] for r in retiros) / len(retiros)) if retiros else None,
        "medio_pago_al_retirar": dict(Counter(r["medio_pago"] for r in retiros)),
    }
