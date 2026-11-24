# Informe Analítica MJV — Pronto Casino

17 de noviembre de 2026 · Equipo: Renato Escárate (líder), Jorge Mendoza, Yeremi Navarro

Este informe responde los dos pasos del taller autónomo de la clase 26: la matriz MJV del proyecto y su implementación en código, con los eventos guardados en un JSON local.

## Paso 1: Matriz MJV

La matriz tiene 6 filas; el mínimo pedido era 3. Cada métrica lleva una acción definida para cuando el resultado sea alto o bajo.

| Métrica (M) | Justificación (J) | Valor / acción derivada (V) |
| --- | --- | --- |
| Productos más vendidos (`pedido_creado`) | Saber qué platos sostienen la venta del casino | Aumentar la producción de esos platos para que no se agoten en hora punta (12:00 a 14:30) |
| Productos menos vendidos (`pedido_creado`) | Detectar platos que no rotan y terminan como merma | Ponerlos en oferta o sacarlos del menú |
| Medios de pago más usados (`pedido_creado`); la reserva sin pago cuenta como medio propio, "Reserva (paga en caja)" | Comprobar si la Beca BAES domina la venta estudiantil, como supone el proyecto | Ordenar la pasarela según el uso real. Si la reserva es el medio más usado, revisar por qué no se paga en la app |
| Tiempo del flujo de pedido (`pedido_creado.segundos_flujo`) | Validar que pedir por la app es más rápido que hacer la fila | Si el promedio supera unos 90 s, agregar "repetir último pedido" o dejar marcado el último medio de pago |
| Pérdida de comida en CLP (`pedido_perdido`) | Medir la comida y el dinero perdidos por reservas vencidas, cancelaciones y rechazos | Si la pérdida por reservas vencidas es alta, exigir pago anticipado en hora punta |
| Cumplimiento de reservas (`reserva_retirada`): tasa de retiro y minutos hasta el retiro | Saber si los estudiantes cumplen con la reserva sin pago | Tasa de retiro baja: limitar o quitar la reserva en hora punta. Retiro rápido (por ejemplo, 20 min): acortar la ventana de 1 hora para liberar stock antes |

## Paso 2: Implementación en código

Cada evento se graba con `registrar_evento(nombre, datos)`, definida en `punto_casino/services/analytics_service.py`, que lo agrega a `data/analytics_events.json`. La tabla indica la pantalla y la función exacta donde se dispara cada evento.

| Evento | Pantalla que lo origina | Función que lo registra | Datos guardados |
| --- | --- | --- | --- |
| `pedido_creado` | Catálogo, al pulsar Pagar (`_execute_payment`) | `OrderService.checkout` | Pedido, medio de pago, si es reserva, total, productos, segundos del flujo |
| `pedido_perdido` | Mis Reservas (cancelar), Caja (rechazar) o automático | `OrderService.cancel_order`, `CashierService.reject_order`, `OrderService.expire_reservations` | Pedido, motivo (`cancelado_cliente`, `rechazado_caja`, `reserva_vencida`), monto en CLP, productos |
| `reserva_retirada` | Caja (escanear QR o cobrar), Admin o Mis Reservas (cobrar) | `CashierService.process_qr_payment`, `OrderService.mark_delivered` | Pedido, medio con que se pagó en caja, minutos desde la reserva |

Ejemplo de un evento grabado en `data/analytics_events.json` (verificado con una prueba automática):

```json
{
    "evento": "pedido_creado",
    "fecha": "2026-11-17T12:41:05",
    "datos": {
        "pedido": "PED-3FA21C",
        "medio_pago": "BAES_JUNAEB",
        "es_reserva": false,
        "total": 4800,
        "items": [{"product_id": "MENU-01", "nombre": "Pastel de Choclo", "cantidad": 1}],
        "segundos_flujo": 38
    }
}
```
