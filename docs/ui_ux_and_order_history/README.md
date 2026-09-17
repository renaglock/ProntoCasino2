# Feature: Rediseño UI/UX Móvil y Módulo de Historial de Pedidos para Caja y Admin

- **Fecha**: 2026-09-17
- **Estado**: En Revisión HITL
- **Autor / Agente**: Antigravity Punto Casino Engineer
- **Referencia Requerimientos**: docs/requerimientos.md (Secciones 1.1, 2, 3, 5 y 6 MVP y Post-MVP)

---

## 1. Descripción y Objetivo

Resolver de raíz los defectos visuales de colisión y solapamiento de textos en tarjetas (`AdminScreen`, `CashierScreen`), desbordamiento horizontal de botones en pantallas móviles (380x720 px), y dotar a los roles de **Cajero** y **Administrador** de un **Historial Completo de Pedidos y Métricas Operativas**.

---

## 2. Tecnicismos y Arquitectura

### 2.1 Módulos y Capas Afectadas

1. **Capa de Dominio y Servicios (`punto_casino/services/`)**:
   - `cashier_service.py`: Adición de `get_history_orders()` y métricas de caja.
   - `order_service.py`: Soporte para métricas agregadas de ventas (`total_delivered_amount`, `orders_by_status`).
   - `auth_service.py`: Soporte para `refund_user_balance` transaccional.

2. **Capa de Presentación (`punto_casino/views/screens/`)**:
   - `admin_screen.py`:
     - Reemplazo de tarjetas de altura estática por tarjetas adaptativas (`adaptive_height=True`).
     - Reorganización visual: ID en pill badge, título en negrita con contraste, badge de stock dinámico.
     - Switcher/Pestañas: `[🍽️ Catálogo CRUD]` y `[📊 Historial de Pedidos y Ventas]`.
     - Métricas en tiempo real: Total recaudado en CLP, total comandas atendidas, tasa de éxito.
   - `cashier_screen.py`:
     - Solución de desbordamiento de botones: reorganización ergonómica en 2 filas:
       - Fila 1: `[⚡ Cobrar y Entregar (QR)]` (botón principal lleno a ancho completo).
       - Fila 2: `[✓ Confirmar]` y `[✗ Rechazar]` (50% de ancho cada uno).
     - Corrección de modal de escáner QR: botones organizados vertical/horizontalmente sin salir del viewport de 380px.
     - Switcher: `[📥 Cola Activa]` vs `[📋 Historial de Comandas]`.
   - `catalog_screen.py` y `reservations_screen.py`:
     - Uso de `adaptive_height=True` para prevenir solapamientos.

---

## 3. Casos Borde y Manejo de Errores

1. **Pantallas Angostas (360px a 380px)**: Los botones ya no utilizan anchos fijos combinados mayores a 320dp; se distribuyen proporcionalmente en la cuadrícula vertical.
2. **Nombres de Platos Extensos**: Títulos de hasta 3 líneas se muestran con espacio suficiente sin encimar descripciones o botones gracias al layout adaptativo.
3. **Historial Vacío**: Vistas de estado vacío (*Empty state*) con instrucciones claras y tarjetas estilizadas.

---

## 4. Pruebas y Verificación

```powershell
.\kivy_env\Scripts\python.exe main.py
```

