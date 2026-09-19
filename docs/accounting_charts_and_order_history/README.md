# Feature: Herramientas Gráficas de Contabilidad y Robustecimiento de Historial de Pedidos

- **Fecha**: 2026-09-19
- **Estado**: Completada
- **Autor / Agente**: Antigravity Punto Casino Engineer
- **Referencia Requerimientos**: docs/requerimientos.md (Sección 1.1, 1.2, 2.2 y Fase 2 - Métricas de Ventas)

---

## 1. Descripción y Objetivo

Esta feature aborda tres necesidades críticas para la administración del casino universitario:
1. **Eliminación de jerga técnica en la UI**: Se reemplazó el texto `Platos (CRUD)` de las pestañas por `Platos`, asegurando una interfaz profesional, limpia e institucional que no expone tecnicismos de desarrollo al usuario administrativo.
2. **Herramientas Gráficas de Contabilidad Financiera y Operacional**: Se dotó al panel de administración de métricas e instrumentos visuales de alto impacto:
   - **Tarjetas KPI Ejecutivas**: Recaudación Neta Total (CLP), Ticket Promedio por Pedido, Tasa de Despacho Efectivo (%) y Pedidos Totales.
   - **Gráfico Proporcional por Categoría de Menú**: Gráfico de barras horizontales con barras de progreso estilizadas, mostrando recaudación monetaria y porcentaje por categoría (Menú Normal, Ejecutivo, Hipocalórico, Comidas Rápidas, Bebidas, etc.).
   - **Balance Operacional Segmentado**: Barra multi-estado en un solo riel visual que divide entregas efectivas (verde), comandas en cocina (ámbar) y pedidos cancelados (rojo) con leyenda interactiva.
   - **Ranking de Platos Más Vendidos**: Clasificación ordenada de los platos con mayor demanda y volumen despachado.
3. **Robustecimiento del Historial de Pedidos y Auditoría**:
   - **Buscador Reactivo sin Pérdida de Foco**: Permite buscar pedidos instantáneamente por número de comanda, ID de transacción, nombre del cliente o platos incluidos.
   - **Chips de Filtro por Estado**: Botones segmentados (`Todos`, `Entregados`, `En Cocina`, `Cancelados`) para filtrar el historial de manera inmediata.
   - **Modal de Auditoría de Comanda**: Vista detallada con desglose ítem por ítem, subtotales, cliente, hora de registro, estado contable y la opción de cobrar/liquidar en caja directamente desde la auditoría.

---

## 2. Tecnicismos y Arquitectura

### 2.1 Módulos y Capas Involucradas

- **`punto_casino/repositories/order_repository.py`**:
  - Incorporación de semillas de datos de prueba representativas (`_seed_sample_orders`) con comandas reales en distintos estados (`DELIVERED`, `CONFIRMED`, `PENDING`, `CANCELLED`) y variedad de categorías de platos.
- **`punto_casino/services/order_service.py`**:
  - `get_accounting_report()`: Motor de agregación contable que calcula métricas financieras globales, desglose por categoría con porcentaje relativo, distribución de estados operativos y ranking de popularidad de platos.
  - Sincronización del secuenciador de comandas (`_next_comanda_number`) calculando dinámicamente el valor máximo existente + 1.
- **`punto_casino/views/screens/admin_screen.py`**:
  - Eliminación de la etiqueta `(CRUD)` en la barra de navegación del administrador.
  - Implementación de constructores de gráficos visuales en KivyMD (`_build_kpi_summary_card`, `_build_category_distribution_card`, `_build_operational_balance_card`, `_build_top_dishes_card`).
  - Separación del contenedor dinámico `self.orders_list_box` para actualizar la lista de pedidos reactivamente ante eventos `on_text` del buscador sin destruir el campo de texto ni causar parpadeo visual.
  - Modal de auditoría `_show_comanda_audit_modal` y acción `_charge_order_from_audit` para liquidación directa.
  - Limpieza segura de modales superpuestos en `_hide_modals()`.

### 2.2 Gráficos Nativos en KivyMD (Sin Dependencias Externas)

Para garantizar portabilidad en Android y escritorio sin dependencias pesadas que eleven el tamaño del APK o causen problemas de renderizado en OpenGL ES:
- Las barras de progreso de las categorías se construyen anidando un `MDCard` interior con `size_hint=(pct / 100.0, 1)` dentro de un `MDCard` exterior que actúa como carril guía (`size_hint=(1, None), height=dp(8)`).
- La barra de balance operacional distribuye proporcionalmente sub-tarjetas con los colores institucionales:
  - `#10B981` (Verde Esmeralda) para entregadas.
  - `#D97706` (Ámbar) para comandas activas en preparación.
  - `#DC2626` (Rojo) para canceladas.

---

## 3. Casos Borde y Manejo de Errores

1. **División por Cero en Métricas**: Si la base de datos no contiene pedidos o la recaudación es 0, los cálculos porcentuales y de ticket promedio retornan `0` de forma segura evitando excepciones `ZeroDivisionError`.
2. **Preservación del Foco en Búsqueda**: En Kivy, redibujar todo el `ScrollView` al tipear en un `MDTextField` remueve el widget del árbol gráfico, perdiendo el foco y cerrando el teclado en móviles. Se implementó una arquitectura de contenedor dedicado (`orders_list_box`), donde solo se refrescan las tarjetas de pedidos hijas mientras el `MDTextField` permanece intacto.
3. **Superposición de Modales**: Al abrir el modal de auditoría o confirmación, se invoca previamente `_hide_modals()`, asegurando que no queden widgets huérfanos en `self.root_layout`.

---

## 4. Pruebas y Verificación

### 4.1 Comandos de Ejecución
```bash
./kivy_env/bin/python main.py
```

### 4.2 Checklist de Verificación Funcional
- [x] Iniciar sesión con rol Administrador (`admin` / `admin123`).
- [x] Verificar que el botón de navegación superior indique exactamente **"Platos"** y no contenga la palabra "(CRUD)".
- [x] Cambiar a la pestaña **"Ventas & Métricas"**:
  - Verificar que las tarjetas de métricas muestren la Recaudación Neta, Ticket Promedio y Tasa de Despacho.
  - Verificar el gráfico de barras horizontales con el desglose de ingresos por categoría de menú.
  - Verificar la barra de balance operacional segmentada.
  - Verificar el ranking de platos más vendidos.
- [x] En la sección de **"Historial de Pedidos & Auditoría"**:
  - Probar la barra de búsqueda en tiempo real escribiendo el número de comanda (ej: `#101`), nombre de cliente (ej: `Carlos`) o plato (ej: `Empanada`).
  - Probar los chips de filtrado (`Todos`, `Entregados`, `En Cocina`, `Cancelados`).
  - Presionar el botón **"Auditar"** de cualquier comanda para desplegar el modal de auditoría contable.
  - En pedidos activos, presionar **"Cobrar en Caja"** para liquidar el pedido y verificar la actualización inmediata del estado.

