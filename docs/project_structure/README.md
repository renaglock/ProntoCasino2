# Feature: Arquitectura de Carpetas y Módulos Base (Clean Layered Architecture)

- **Fecha**: 2026-09-15
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) (Sección 3: Tipos de usuario, Sección 4: Datos básicos, Sección 5: Requisitos funcionales/no funcionales de modularidad, Sección 9: Flujo principal)

---

## 1. Descripción y Objetivo
Esta feature establece la arquitectura base del proyecto en Python estructurada en capas independientes. El objetivo principal es desacoplar completamente la lógica de negocio y las entidades de datos de la interfaz visual KivyMD, permitiendo que la plataforma Punto Casino Universidad soporte una evolución limpia hacia el MVP (reserva de pedidos por clientes/invitados y confirmación en caja por cajeros) y soporte escalabilidad futura sin acoplamiento.

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura y Módulos
La arquitectura se organiza bajo el paquete raíz `punto_casino/` con las siguientes responsabilidades:

1. **`punto_casino/core/`**:
   - `config.py`: Definición de paletas de colores Material Design 3 (`theme_cls.primary_palette = "Orange"`), configuración global de la app y títulos.
2. **`punto_casino/models/`**:
   - `product.py`: Dataclass pura de `Product` (`id_producto`, `name`, `price`, `stock`, `is_active`, `category`).
   - `order.py`: Dataclass de `Order`, `OrderItem` y enumeración `OrderStatus` (`PENDING`, `CONFIRMED`, `REJECTED`, `READY`, `DELIVERED`).
   - `user.py`: Dataclass de `User` y enumeración `UserRole` (`CLIENT`, `CASHIER`, `ADMIN`, `GUEST`).
3. **`punto_casino/repositories/`**:
   - `base.py`: Protocolos e interfaces abstractas para persistencia de datos.
   - `product_repository.py`: Repositorio con datos iniciales de cafetería universitaria chilena (Empanadas, Sandwiches, Bebidas, Café) y operaciones de consulta y descuento de stock.
   - `order_repository.py`: Repositorio de pedidos en memoria con filtrado por estado y cliente.
4. **`punto_casino/services/`**:
   - `order_service.py`: Lógica de creación de pedidos, cálculo de subtotales y totales, validación de disponibilidad de stock e inicio de reserva.
   - `cashier_service.py`: Gestión de la cola de pedidos pendientes para el cajero, confirmación o rechazo de pedidos y modificación de stock/disponibilidad de productos.
5. **`punto_casino/utils/`**:
   - `formatters.py`: Formateo de moneda local chilena (ej. `$2.000`) y fechas amigables.
   - `qr_generator.py`: Generación y parseo de payloads para validación de retiro mediante QR.
6. **`punto_casino/views/`**:
   - `screens/`: Pantallas principales (`CatalogScreen`, `CartScreen`, `CashierScreen`, `AdminScreen`).
   - `components/`: Tarjetas y widgets reutilizables de KivyMD.

### 2.2 Flujo de Datos y Ciclo de Vida
```text
[KivyMD View / Screen]
       │
       ▼
[Service Layer (order_service / cashier_service)]
       │
       ▼
[Repository Layer (InMemory / SQLite)] ──► [Models (Product, Order, User)]
```
- La capa de presentación KivyMD invoca métodos del servicio sin conocer detalles del almacenamiento.
- El servicio orquesta la validación de inventario y mutación de estado.
- Las actualizaciones a la interfaz gráfica se despachan en el hilo principal mediante `kivy.clock.Clock.schedule_once`.

### 2.3 Transiciones de Estado del Pedido
- **PENDING**: Pedido creado por cliente o invitado. Stock reservado preliminarmente.
- **CONFIRMED**: El cajero aprueba la orden en su terminal. Se genera el identificador de retiro QR.
- **REJECTED**: El cajero declina el pedido (ej. producto agotado). Se repone el stock.
- **READY**: Pedido preparado y listo en mesón.
- **DELIVERED**: Pedido entregado al usuario final.

---

## 3. Casos Borde y Manejo de Errores
- **Stock Insuficiente**: `OrderService` lanza excepción controlada `ValueError` si la cantidad solicitada excede el inventario disponible.
- **Productos Inactivos**: Los productos dados de baja por el cajero (`is_active=False`) se filtran automáticamente en el catálogo del cliente.
- **Seguridad en Moneda**: Todos los cálculos monetarios se realizan en enteros/números positivos y se formatean estrictamente según moneda chilena (`CLP`).

---

## 4. Pruebas y Verificación

### Comando de ejecución local
```bash
./kivy_env/bin/python -c "import punto_casino; print('Punto Casino package importado con exito')"
```

### Checklist de Verificación Funcional
- [x] Paquete `punto_casino` estructurado con todos los submódulos requeridos.
- [x] Entidades `Product`, `Order`, `User` tipadas y desacopladas de librerías externas.
- [x] Servicios con separación estricta de responsabilidades (Cajero vs Cliente).
- [x] Compatible con Python 3.13 en `kivy_env`.

