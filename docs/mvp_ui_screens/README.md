# Feature: Pantallas de Interfaz de Usuario del MVP (KivyMD 2.0.0)

- **Fecha**: 2026-09-15
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) (Sección 1: Contexto, Sección 2: Lista de usuarios, Sección 6: Definición del MVP, Sección 9: Flujo principal)

---

## 1. Descripción y Objetivo
Esta feature implementa la interfaz visual gráfica del MVP de Punto Casino Universidad en KivyMD 2.0.0 (Material Design 3). El objetivo es proveer a los estudiantes e invitados una pantalla intuitiva de catálogo y carrito para ordenar productos y reservar su pedido sin hacer filas, y al personal de caja un terminal interactivo para visualizar los pedidos entrantes y aprobarlos o rechazarlos en tiempo real.

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura y Módulos
- **`punto_casino/views/screens/catalog_screen.py` (`CatalogScreen`)**:
  - Pantalla principal de catálogo de productos para clientes e invitados.
  - Integra input para el nombre del cliente (`MDTextField`).
  - Lista desplazable (`ScrollView`) con tarjetas de producto (`MDCard`) generadas dinámicamente según el repositorio.
  - Carrito reactivo con cálculo automático de totales en CLP y botón para reservar (`OrderService.checkout`).
  - Botón de navegación directa hacia el terminal de caja.
- **`punto_casino/views/screens/cashier_screen.py` (`CashierScreen`)**:
  - Pantalla de recepción para el cajero.
  - Lista de pedidos pendientes en cola (`OrderStatus.PENDING`).
  - Cada tarjeta presenta el identificador (`PED-XXXXXX`), cliente, desglose de ítems y monto total.
  - Botón "Confirmar Pedido" (`CashierService.confirm_order`) y botón "Rechazar" (`CashierService.reject_order`, que automáticamente repone el stock).
  - Botón de navegación para regresar al catálogo.
- **`main.py` (`PuntoCasinoApp`)**:
  - Configura el tema Material Design 3 (Paleta `"Orange"` y Acento `"Amber"`).
  - Inicializa repositorios y servicios compartidos en memoria.
  - Administra la navegación entre pantallas mediante `MDScreenManager`.

### 2.2 Flujo de Datos
```text
[Cliente / Invitado]                [Cajero]
   │                                   │
   ├─► Selecciona productos            │
   ├─► Click "Reservar Pedido"         │
   │        │                          │
   │        ▼                          │
   │   OrderService.checkout()         │
   │   (Descuenta stock temporal)      │
   │   (Crea Pedido en PENDING)        │
   │        │                          │
   │        └─────────────────────────►│ Ve pedido en cola
   │                                   ├─► Click "Confirmar Pedido"
   │                                   │        │
   │                                   │        ▼
   │                                   │   CashierService.confirm_order()
   │                                   │   (Estado -> CONFIRMED)
   │                                   │   (Listo para retiro con QR)
```

### 2.3 Componentes KivyMD 2.0.0
- `MDScreenManager`: Controlador de vistas `'catalog'` y `'cashier'`.
- `MDCard`: Tarjetas estilizadas (`elevated`, `outlined`) para cada producto y pedido.
- `MDButton`, `MDButtonText`: Botones declarativos MD3 con estilos `filled`, `tonal` y `outlined`.
- `MDTextField`, `MDTextFieldHintText`: Campo de entrada de texto moderno para el nombre del usuario.
- `ScrollView`: Contenedor desplazable que soporta cualquier cantidad de productos o pedidos concurrentes.

---

## 3. Casos Borde y Manejo de Errores
- **Validación de Carrito Vacío**: Si el cliente presiona "Reservar" sin artículos, se captura la excepción y se informa mediante el banner de estado.
- **Stock Agotado en Tiempo Real**: Si el stock de un producto se agota, el servicio bloquea la reserva y la UI muestra el error sin caer en excepción no controlada.
- **Restitución Automática por Rechazo**: Si el cajero rechaza el pedido, el servicio restituye el inventario y refresca la lista automáticamente.

---

## 4. Pruebas y Verificación

### Comando de ejecución
```bash
./kivy_env/bin/python main.py
```

### Verificación Funcional Realizada
- [x] Ejecución del entrypoint con carga visual fluida en X11 (`DISPLAY=:0.0`).
- [x] Navegación bidireccional entre la pantalla de catálogo y la pantalla de caja.
- [x] Flujo completo: selección de producto -> reserva -> visto bueno en caja.

