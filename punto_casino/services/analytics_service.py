"""Analítica local (método MJV): guarda eventos de uso en data/analitica.json y los resume."""

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

ARCHIVO = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "data", "analitica.json"
)


def leer_eventos() -> List[Dict[str, Any]]:
    """Todos los eventos guardados; lista vacía si el archivo no existe o está corrupto."""
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def registrar_evento(nombre: str, datos: Optional[Dict[str, Any]] = None) -> None:
    """Agrega un evento {evento, fecha, datos} al JSON local. Nunca rompe el flujo de la app."""
    eventos = leer_eventos()
    eventos.append({"evento": nombre, "fecha": datetime.now().isoformat(timespec="seconds"), "datos": datos or {}})
    try:
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(eventos, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


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
