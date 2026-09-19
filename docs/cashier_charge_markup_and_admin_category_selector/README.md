# Feature: Corrección de Etiquetas Markup, Cobro Omnipresente de Comandas, Selector de Categorías y Generalización de Ofertas

- **Fecha**: 2026-09-19
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Platform Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) (Secciones 2, 3, 4 y 5)

---

## 1. Descripción y Objetivo
Esta actualización resuelve integralmente los requerimientos detectados en la operativa de caja, catálogo y administración del casino universitario:

1. **Corrección de Error Visual de Markup BBCode (`[color=...]`)**:
   - Se corrigió el error visual donde etiquetas de formato BBCode como `[color=#10B981]Plato agregado al carrito.[/color]` aparecían de forma literal en la tarjeta del carrito de `CatalogScreen`.
   - Se activó la propiedad `markup=True` en todos los labels dinámicos (`cart_label`, `status_label`) garantizando renderizado cromático nativo en la interfaz.

2. **Prevención de Superposición de Texto en Detalle de Reserva**:
   - En el modal de detalle de comanda (`ReservationsScreen`), los nombres largos de platos con leyendas (ej: `• 1x Lasaña Boloñesa (Últimas porciones)`) colisionaban con las filas inferiores.
   - Se incorporó truncamiento controlado en una línea (`shorten=True, shorten_from="right"`), proporciones de ancho fijas (`72%` nombre de plato, `28%` subtotal monetario) y dimensionamiento dinámico de la caja contenedora de ítems.

3. **Flujo de Cobro Omnipresente e Inmediato para el Cajero**:
   - **En `ReservationsScreen`**: Cuando un cajero o administrador visualiza cualquier reserva activa (`PENDING`, `CONFIRMED`, `READY`), ahora dispone del botón destacado **"Cobrar en Caja"** (`style="offer"` con ícono `cash-register`), permitiéndole registrar el pago y entrega directamente desde el modal de comanda con un solo toque.
   - **En `CashierScreen`**: El cajero ya no está forzado a utilizar un escaneo por cámara web para cobrar pedidos en cola. Cada tarjeta de comanda en cola activa (ya sea `PENDING`, `CONFIRMED` o `READY`) cuenta con el botón primario de 1 toque **"Cobrar y Entregar"**, el cual despliega una confirmación directa modal (`_ask_charge_comanda`), actualiza el estado a `DELIVERED`, devuelve stock a contabilidad y descuenta los estados correspondientes.
   - Se añadió la acción secundaria **"Listo Cocina"** (`_mark_order_ready`) para avanzar comandas confirmadas a estado de retiro.
   - Se optimizó el modal de escáner QR para autoverificar los pedidos precargados (`prefill_id`) sin requerir pulsaciones redundantes.

4. **Selector Interactivo de Categorías del Menú en Panel Administrador**:
   - En `AdminScreen`, se reemplazó el campo de texto libre para categoría por un selector guiado interactivo (`select` modal) que despliega las categorías oficiales del catálogo: `Menú Normal`, `Menú Ejecutivo`, `Menú Hipocalórico`, `Menú Vegetariano`, `Comidas Rápidas`, `Bebidas`, y `Postres y Snacks`.
   - El administrador selecciona la categoría mediante botones táctiles con íconos vectoriales asociados, evitando errores de tipeo y manteniendo consistencia con los filtros del catálogo.

5. **Generalización de Ofertas y Descuentos Especiales**:
   - Se eliminó la restricción conceptual que asociaba los descuentos únicamente a productos "por vencer".
   - Los botones, leyendas y textos de sugerencia se actualizaron a **"Activar Oferta / Descuento Especial"** (y **"Oferta / Descuento: ACTIVA"** al estar habilitado), con sugerencias ampliadas como *"Promo 2x1, Menú del día, 30% OFF, Por vencer"*.

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura y Módulos Modificados

- **`punto_casino/services/order_service.py`**:
  - Incorporación del método `mark_delivered(self, order_id: str) -> bool` para permitir a cajeros y administradores liquidar comandas y marcarlas como entregadas desde cualquier pantalla.
  - Validación de estados terminales para impedir cobrar comandas previamente canceladas o rechazadas.

- **`punto_casino/views/screens/catalog_screen.py`**:
  - Adición de `markup=True` a `self.cart_label` y `self.status_label` en el pie de página del catálogo.

- **`punto_casino/views/screens/reservations_screen.py`**:
  - Detección de rol de usuario autenticado (`UserRole.CASHIER`, `UserRole.ADMIN`).
  - Renderizado condicional del botón `"Cobrar en Caja"` (`style="offer"`, ícono `cash-register`) en el modal `_show_order_detail_modal` para pedidos en estados activos (`PENDING`, `CONFIRMED`, `READY`).
  - Implementación de `_charge_order_as_cashier(self, order: Order)` que delega en `order_service.mark_delivered()`.
  - Corrección de colisión de texto mediante `shorten=True, shorten_from="right"` en cada fila de plato (`dp(22)` de alto).

- **`punto_casino/views/screens/cashier_screen.py`**:
  - Reestructuración de botones en `_build_comanda_card`:
    - Para comandas `PENDING`: Nivel 1 = `"Cobrar y Entregar"`; Nivel 2 = `"Confirmar Cocina"` y `"Rechazar"`.
    - Para comandas `CONFIRMED`: Nivel 1 = `"Cobrar y Entregar"`; Nivel 2 = `"Listo Cocina"` y `"Escanear QR"`.
    - Para comandas `READY`: Nivel 1 = `"Cobrar y Entregar"`.
  - Métodos `_ask_charge_comanda(self, order: Order)` y `_execute_direct_charge(self, order: Order)` para liquidar comandas sin requerir cámara física.
  - Método `_mark_order_ready(self, order: Order)` para marcar comanda lista en mesón.
  - Autoverificación automática en `_show_qr_scanner_modal` ante parámetros `prefill_id`.

- **`punto_casino/views/screens/admin_screen.py`**:
  - Campo `self.input_cat` configurado como `readonly=True`, acompañado por el botón `"Elegir"` con ícono `menu-down`.
  - Modal `_show_category_picker(self)` con las 7 categorías oficiales del menú universitario.
  - Método `_select_category(self, cat_name: str)` para asignar el valor seleccionado y cerrar el modal.
  - Renombrado de etiquetas a `"Activar Oferta / Descuento Especial"` y `"Oferta / Descuento: ACTIVA"`.
  - Campo de motivo con hint generalizado (`"Motivo (ej: Promo 2x1, Menú del día, 30% OFF, Por vencer)"`).

---

## 3. Flujo de Datos y Ciclo de Vida

```
[Cliente o Cajero crea comanda]
               │
               ▼
     OrderStatus.PENDING
         │          │
         │          ├─────────────────────────┐
         │ (Confirmar Cocina)                 │ (Cobrar y Entregar)
         ▼                                    ▼
OrderStatus.CONFIRMED                OrderStatus.DELIVERED
         │                                    ▲
         ├────────────────────────────────────┤
         │ (Cobrar y Entregar directo         │
         │  o desde modal de Reserva)         │
         ▼                                    │
OrderStatus.READY                             │
         │                                    │
         └────────────────────────────────────┘
```

---

## 4. Checklist de Verificación Funcional

- [x] El texto del carrito en el catálogo muestra los colores correctos sin mostrar etiquetas `[color=...]` sin procesar.
- [x] Los nombres largos de platos en el modal de reserva no se montan ni superponen con los platos contiguos.
- [x] El cajero puede cobrar cualquier comanda activa (`PENDING`, `CONFIRMED`, `READY`) tanto desde la pestaña **Caja** como desde el modal de detalle en **Reservas**.
- [x] Al confirmar una comanda a cocina, el cajero conserva el botón **"Cobrar y Entregar"** para procesar el pago en cualquier momento.
- [x] En el formulario de administración de platos, la categoría se selecciona mediante un selector con las 7 categorías oficiales del menú.
- [x] La sección de descuentos y ofertas permite activar promociones con motivo libre sin restringirse a fechas de vencimiento.

