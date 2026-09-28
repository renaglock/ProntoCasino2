# Feature: Anclaje Superior de Modales de Cobro, Centrado Visual M3 y Fluidez de Transición 60 FPS

- **ID Feature**: `PC-FEAT-TOP-ANCHOR`
- **Fecha**: 2026-09-28
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Platform Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) (Secciones 2, 3 y 5) & [docs/plan_expansion_universidades_chile/README.md](../plan_expansion_universidades_chile/README.md)

---

## 1. Resumen Ejecutivo y Valor de Negocio

### 1.1 Declaración del Problema
1. **Espacio Muerto Invertido**: Al presionar el botón **"Cobrar y Entregar"** (o activar el escáner QR) en la pantalla de Caja (`CashierScreen`), tanto con rol de **Cajero** como de **Administrador**, el modal de confirmación y el encabezado se renderizaban empujados hacia la parte inferior de la pantalla, dejando un área sustancial de espacio muerto en la parte superior.
2. **Asimetría de Texto en Diálogo de Cobro**: El título y el mensaje del modal de confirmación se encontraban alineados a la izquierda sin centrado horizontal (`halign="center"`), lo que provocaba un vacío asimétrico en el lado derecho de la tarjeta.
3. **Pérdida de Fluidez y Salto Visual al Entrar a Cobro**: Debido a que la reconstrucción de pedidos se ejecutaba en `on_enter()` (tras concluir la transición de pantalla), los labels se instanciaban con ancho base `width=100` y recalculaban su envoltorio y recorte en el frame subsiguiente, generando un molesto parpadeo o acomodo de texto visible y una caída de frames (*jank*).

### 1.2 Valor Aportado y Métrica de Éxito
- **Ergonomía Móvil M3**: El contenido del diálogo de cobro y el encabezado permanecen anclados de forma fija en la zona superior de la pantalla, directamente bajo la barra de la app.
- **Centrado y Simetría Axial**: El título, mensaje de confirmación y botones quedan perfectamente centrados en la tarjeta.
- **Transición Estable a 60 FPS**: Se eliminó el reacomodo tardío de texto al precalcular el árbol de widgets en `on_pre_enter()`.
- **Métricas Clave**:
  - Tiempo de renderizado de la transición: Fluida a 60 FPS sin caídas de frame.
  - Cero saltos visuales o parpadeos de texto tras ingresar a la pantalla.

---

## 2. Especificación Técnica y Arquitectura

### 2.1 Capas y Módulos Modificados
- **`punto_casino/views/screens/cashier_screen.py`**:
  - Se importó `from kivy.uix.widget import Widget`.
  - Se inicializó `self.bottom_spacer = None` en `__init__`.
  - **Ciclo de vida optimizado**: Se implementó `on_pre_enter()` para ejecutar `self._hide_modals()` y `self.refresh_orders()` **antes** de iniciar la animación de transición, dejando `on_enter()` ligero.
  - **Centrado Material 3**: En `_ask_charge_comanda`, se configuró `halign="center"` en `c_title` y `c_msg`, con botones simétricos al 50% de ancho cada uno (`size_hint=(0.5, None)`).
  - En `_show_qr_scanner_modal`, se configuró `halign="center"` en el título del escáner.
  - En `_ask_charge_comanda` y `_show_qr_scanner_modal`, se incorpora dinámicamente un espaciador flexible inferior `self.bottom_spacer = Widget(size_hint_y=1)` en `index=0` de `root_layout`.
  - En `_hide_modals`, se remueve `self.bottom_spacer` limpiamente y se restaura el contenedor de pedidos `self.scroll` con `size_hint_y=1` y `opacity=1`.

- **`main.py`**:
  - En `navigate_to()`, se despacha explícitamente `target.on_pre_enter()` antes del cambio de `self.sm.current` para que la pantalla entrante prepare y estilice su contenido con antelación a la animación `FadeTransition`.

- **`punto_casino/views/screens/admin_screen.py`**:
  - Se importó `from kivy.uix.widget import Widget`.
  - Se añadieron `self.bottom_spacer = None` y `self.list_container = None` en `__init__`.
  - En `_show_list_view`, se almacena la referencia del contenedor de listado `self.list_container = container`.
  - En `_show_comanda_audit_modal` y `_ask_delete_confirmation`, se oculta `self.list_container` (`size_hint_y=None, height=0, opacity=0, disabled=True`) y se añade `self.bottom_spacer = Widget(size_hint_y=1)` en `index=0`.
  - En `_hide_modals`, se remueve `bottom_spacer` y se restablece la visibilidad de `self.list_container` (`size_hint_y=1, opacity=1, disabled=False`).

---

## 3. Verificación y Casos de Prueba

1. **Navegación Fluida a Pantalla de Caja (Cobro)**:
   - Cambiar de pestaña (ej: desde Menús o Reservas hacia Caja).
   - **Resultado esperado**: La pantalla se desvanece con los elementos y tarjetas ya completamente formados; no se observa ningún reacomodo, salto o titubeo de texto al terminar la animación.

2. **Centrado en Modal "Cobrar y Entregar Comanda"**:
   - En una comanda activa, pulsar *"Cobrar y Entregar"*.
   - **Resultado esperado**:
     - Título *"Cobrar y Entregar Comanda"* centrado horizontalmente.
     - Texto de confirmación *"¿Cobrar $X a [Nombre] y registrar entrega?"* centrado horizontalmente.
     - Botones *"Cancelar"* y *"Confirmar Cobro"* distribuidos de forma simétrica (50% / 50%).
     - Modal anclado en la parte superior sin espacio muerto superior.
