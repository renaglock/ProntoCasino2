# PC-FEAT-007 — Analítica local con método MJV y vencimiento de reservas

## 1. Resumen Ejecutivo y Valor de Negocio

### 1.1 Declaración del Problema
La app no medía su uso. No se sabía qué platos rotan, con qué medio pagan los estudiantes, cuánto tardan en pedir ni cuánta comida se pierde. Además, las reservas sin pago no vencían: la app decía "tienes 1 hora", pero el stock quedaba retenido sin límite.

### 1.2 Valor Aportado y Métrica de Éxito (Matriz MJV)

| Métrica (M) | Justificación (J) | Valor / acción (V) |
|---|---|---|
| `pedido_creado` → más vendidos | Saber qué platos sostienen la venta | Producir más para no agotarlos en hora punta |
| `pedido_creado` → menos vendidos | Detectar platos que no rotan y terminan en merma | Ponerlos en oferta o sacarlos del menú |
| `pedido_creado` → medios de pago (la reserva cuenta como medio `RESERVA_CAJA`) | Validar que BAES domina la venta estudiantil | Ordenar la pasarela por uso real |
| `pedido_creado.segundos_flujo` | Validar que pedir por la app es más rápido que la fila | Si supera ~90 s, agregar "repetir último pedido" |
| `pedido_perdido` (monto CLP y motivo) | Medir comida y dinero perdidos | Si es alta, exigir pago anticipado en hora punta |
| `reserva_retirada` → tasa de retiro y minutos hasta retiro | Saber si la reserva sin pago se cumple | Tasa baja: limitar reservas. Retiro rápido: acortar la ventana de 1 h |

### 1.3 Actores
Cliente e invitado generan `pedido_creado` y `cancelado_cliente`. Cajero y admin generan `reserva_retirada` y `rechazado_caja`. El vencimiento lo ejecuta la app sola.

## 2. Especificación Técnica

### 2.1 Capas y módulos
- `services/analytics_service.py`: `registrar_evento(nombre, datos)`, `leer_eventos()` y `resumen()`.
- `services/order_service.py`: `checkout` (pedido_creado y duración), `cancel_order` (pedido_perdido), `expire_reservations` (vencimiento), `mark_delivered` (reserva_retirada).
- `services/cashier_service.py`: `reject_order` (pedido_perdido) y `process_qr_payment` (reserva_retirada).
- `main.py`: corre `expire_reservations()` al iniciar y cada 60 s con `Clock.schedule_interval`.

### 2.2 Dónde se dispara cada evento (vista → servicio)

| Evento | Vista | Servicio |
|---|---|---|
| `pedido_creado` | `CatalogScreen._execute_payment` | `OrderService.checkout` |
| `pedido_perdido` (cancelado_cliente) | `ReservationsScreen` (cancelar) | `OrderService.cancel_order` |
| `pedido_perdido` (reserva_vencida) | — (automático) | `OrderService.expire_reservations` |
| `pedido_perdido` (rechazado_caja) | `CashierScreen` (rechazar) | `CashierService.reject_order` |
| `reserva_retirada` | `CashierScreen` (cobrar/entregar) | `CashierService.process_qr_payment` |
| `reserva_retirada` | `AdminScreen` / `ReservationsScreen` (cobrar) | `OrderService.mark_delivered` |

El tiempo del flujo corre desde el primer producto agregado al carrito hasta el pago. Vaciar el carrito reinicia el contador.

### 2.3 Estados
`PENDING` (reserva sin pago) pasa a `CANCELLED` si pasa más de 1 hora sin retirarse. El stock vuelve al inventario.

### 2.5 Persistencia
`data/analitica.json` es una lista de eventos `{"evento", "fecha", "datos"}`. Si el archivo falta o está corrupto, se parte de cero. Un error de escritura nunca interrumpe la venta.

## 3. Privacidad
Los eventos guardan el ID del pedido, los productos y los montos. No guardan nombre, RUT ni correo.

## 4. Casos borde
- Reserva vencida escaneada en caja: muestra "fue cancelada o su reserva venció".
- Pedidos de la semilla con más de 1 hora pendientes: vencen en el primer arranque.

## 5. Verificación
`test_analytics_mjv_events_and_reservation_expiry` cubre los cuatro eventos, el vencimiento, la devolución del stock y el resumen. Las pruebas escriben en `test_temp_analitica.json`, nunca en `data/`.

## 6. Rollback
Quitar las dos líneas de `expire_reservations` en `main.py` desactiva el vencimiento. Borrar `data/analitica.json` reinicia la analítica.
