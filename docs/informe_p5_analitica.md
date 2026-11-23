# Micro-Informe P5 — Analítica en Código, Funnel y A/B Testing

**Proyecto:** Pronto Casino UCT · **Equipo:** Renato Escárate, Jorge Mendoza, Yeremi Navarro · **Fecha:** 22 de noviembre de 2026

## 1. Implementación

- **Servicio defensivo:** `punto_casino/services/analytics_service.py`. `registrar_evento(nombre, datos)` agrega el evento a `data/analitica.json` dentro de un `try/except Exception`; si falla, lo anota con `logging.error` y la app sigue funcionando.
- **Vistas:** las pantallas nunca escriben el JSON; solo llaman a `registrar_evento`.

| Paso | Evento | Dónde se dispara |
| --- | --- | --- |
| 1 | `app_abierta` | `main.py`, al iniciar la app |
| 2 | `login_exitoso` (y `login_fallido`) | `login_screen.py`, login con correo o como invitado |
| 3 | `pedido_creado` | Catálogo, al pagar o reservar (`OrderService.checkout`) |

## 2. Matriz MJV

| Métrica | Justificación | Valor (acción) |
| --- | --- | --- |
| Conversión del funnel (`app_abierta → login_exitoso → pedido_creado`) | Saber en qué paso abandona el estudiante | Mejorar la pantalla donde más se pierde |
| Medios de pago y reservas (`pedido_creado`) | Ver si se paga en la app o se reserva para pagar en caja | Ordenar la pasarela según el uso real |
| Comida perdida en CLP (`pedido_perdido`) | Medir reservas vencidas y cancelaciones | Si es alta, exigir pago anticipado en hora punta |
| Logins fallidos (`login_fallido`) | Detectar si el acceso es una barrera | Si son muchos, agregar "recordar sesión" o recuperar clave |

## 3. Cálculo del Funnel (sesión de prueba real)

Calculado con `analytics_service.funnel()` sobre `data/analitica.json` (13 eventos, 22-11-2026). Cada `app_abierta` inicia una sesión; una sesión cuenta en un paso si llegó a él y a los anteriores, así un re-login no infla el resultado.

| Paso | Sesiones | % respecto del paso 1 |
| --- | --- | --- |
| 1. `app_abierta` | 3 | 100 % |
| 2. `login_exitoso` | 2 | 66,7 % |
| 3. `pedido_creado` | 1 | 33,3 % |

**Lectura:**

- **Login (pierde 33,3 %):** la sesión que no entró registró 6 `login_fallido` en 8 segundos, un *rage tap* que indica frustración. Acción: mensaje de error más claro y opción "recuperar clave".
- **Pedido (pierde 33,3 %):** una sesión entró y no compró. Acción: medir si se queda en el catálogo o abandona en la pasarela, con un evento `pasarela_abierta`.
- El único pedido fue una **reserva sin pago**, lo que motiva la propuesta A/B de la sección 4.
- La muestra es de 3 sesiones: demuestra que la medición funciona, no es una conclusión estadística.

## 4. Propuesta de A/B Testing

- **Hipótesis:** si en la pasarela se destaca el pago en línea, baja la cantidad de reservas sin pago que vencen y con ello la comida perdida.
- **Variante A (actual):** "Reservar sin pagar" aparece como una opción más, con el mismo peso que Beca BAES, Webpay, TEF y DAE.
- **Variante B:** los medios de pago en línea van primero y "Reservar sin pagar" queda como enlace secundario al final.
- **Asignación:** 50 % de usuarios en cada variante, guardando `{"variante": "A" | "B"}` en `pedido_creado`.
- **Métricas:** % de pedidos pagados en la app sobre el total de `pedido_creado`, y CLP perdido por `reserva_vencida`.
- **Decisión:** si B sube el pago anticipado sin bajar la conversión del paso 3, se adopta B.
