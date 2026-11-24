# Micro-Informe P5 — Analítica en Código, Funnel y A/B Testing

**Proyecto:** Pronto Casino UCT · **Equipo:** Renato Escárate, Jorge Mendoza, Yeremi Navarro · **Fecha:** 24 de noviembre de 2026

## Implementación (resumen)

- **Servicio:** `punto_casino/services/analytics_service.py`. Las vistas nunca tocan el JSON; solo llaman a `registrar_evento(nombre, datos)`.
- **Programación defensiva:** la escritura va en `try/except` y registra el fallo con `logging.error`. La lectura captura `OSError` y `json.JSONDecodeError` y los anota con `logging.warning`. Si algo falla, la app sigue funcionando.
- **Evidencia:** `data/analytics_events.json`, con 13 eventos reales.

| Paso | Evento | Dónde se dispara |
| --- | --- | --- |
| 1 | `app_abierta` | `main.py`, al iniciar la app |
| 2 | `login_exitoso` (y `login_fallido`) | `views/screens/login_screen.py`, login con correo o como invitado |
| 3 | `pedido_creado` | Catálogo → pasarela, al pagar o reservar (`OrderService.checkout`) |

## Sección A — Matriz MJV

| Evento | Métrica (M) | Justificación (J) | Valor / acción (V) |
| --- | --- | --- | --- |
| `app_abierta` | Sesiones iniciadas (base del funnel = 100 %) | Saber cuántos estudiantes abren la app y en qué horario | Dimensionar la demanda en hora de almuerzo y medir el resto del funnel contra esta base |
| `login_exitoso` (+ `login_fallido`) | % de sesiones que logran entrar | El login es la barrera antes de ver el catálogo | Si cae o hay muchos fallidos: mensaje de error más claro y "recuperar clave" |
| `pedido_creado` — metadatos: `medio_pago`, `es_reserva`, `total`, `items`, `segundos_flujo`, `variante` | % de sesiones con login que terminan en pedido, y medio de pago usado | Es la conversión real del negocio: un pedido es una venta | Ordenar la pasarela según el uso real; es el paso que ataca el A/B de la Sección C |

*Además se registran `pedido_perdido` y `reserva_retirada`, que miden la comida perdida en CLP. No forman parte del funnel.*

## Sección B — Cálculo y diagnóstico del funnel

Se calcula con `analytics_service.funnel()` sobre `data/analytics_events.json` (13 eventos de la sesión de prueba del 22-11-2026). Cada `app_abierta` inicia una sesión, y una sesión cuenta en un paso si llegó a él y a todos los anteriores. Así, un re-login no infla el resultado.

**Conteo de ocurrencias:** `app_abierta` 3 · `login_exitoso` 3 · `login_fallido` 6 · `pedido_creado` 1.

| Paso | Sesiones | % vs paso 1 | Conversión desde el paso anterior | Abandono en la etapa |
| --- | --- | --- | --- | --- |
| 1. `app_abierta` | 3 | 100 % | — | — |
| 2. `login_exitoso` | 2 | 66,7 % | 2/3 = 66,7 % | 33,3 % |
| 3. `pedido_creado` | 1 | 33,3 % | 1/2 = **50 %** | **50 %** |

**Diagnóstico:**

- **Mayor abandono: login → pedido (50 %).** Una de cada dos sesiones que entra no termina en pedido. Este es el paso más débil y el objetivo del A/B.
- **Login (33,3 %):** la sesión que no entró registró 6 `login_fallido` en 8 segundos. Es un *rage tap* que indica frustración. Acción: mensaje de error más claro y "recuperar clave".
- El único pedido fue una **reserva sin pago**. La pasarela actual abre en "Reservar sin pagar", lo que empuja a no pagar en la app.
- La muestra es de 3 sesiones: demuestra que la medición funciona, pero no es una conclusión estadística.

## Sección C — Propuesta de A/B Testing

- **Paso a optimizar:** `login_exitoso → pedido_creado` (50 %).
- **Hipótesis:** si la pasarela abre directo en los medios de pago en línea, más estudiantes con login terminan un pedido pagado, y bajan las reservas que vencen.
- **Variante A (actual):** al pulsar "Continuar", la pasarela abre en "Reservar sin pagar" y los medios en línea quedan detrás del botón "Ver medios de pago".
- **Variante B:** la pasarela abre directo en Webpay / Beca BAES / TEF / Beca DAE, y reservar queda como opción secundaria con el botón "Atrás".
- **Configuración en `data/remote_config.json`:**

```json
{ "ab_pasarela": { "activo": true, "porcentaje_b": 50 } }
```

- **Asignación:** `analytics_service.variante_ab(id_usuario)` aplica un hash al id del usuario y lo asigna a B si queda bajo `porcentaje_b`, así cada usuario ve siempre la misma variante. Con `"activo": false` todos ven A, y si el archivo falta o está corrupto también se usa A y queda en el log. La variante se guarda en `pedido_creado` (`"variante": "A" | "B"`).
- **Métrica principal:** conversión `login_exitoso → pedido_creado` por variante.
- **Métricas secundarias:** % de pedidos pagados en la app y CLP perdido por `reserva_vencida`.
- **Decisión:** si B sube la conversión del paso 3, o sube el pago en la app sin bajar esa conversión, se adopta B.
