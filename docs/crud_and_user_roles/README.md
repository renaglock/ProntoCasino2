# Feature: CRUD Profesional de Menús, Separación de Roles y Comandas Enumeradas (PRONTO CASINO UCT)

- **Fecha**: 2026-09-15
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) y [docs/PRONTO CASINO.pdf](../PRONTO%20CASINO.pdf) (Diseño de interfaz UCT, categorías de menú y entrevista con el personal de casino Cristian)

---

## 1. Descripción y Objetivo
Esta feature materializa el diseño de interfaz y requerimientos descubiertos en el recurso gráfico de **PRONTO CASINO UCT** ([docs/PRONTO CASINO.pdf](../PRONTO%20CASINO.pdf)):
1. **Separación de Usuarios (Roles)**:
   - **Estudiante (Renato / Cliente)**: Dispone de un monedero universitario con saldo disponible, navega categorías de menú (*Normal*, *Ejecutivo*, *Hipocalórico*, *Vegetariano*), visualiza ingredientes y reserva con comanda numerada.
   - **Cajero (Cristian / Sabor Único)**: Resuelve el problema identificado en la entrevista (*"las boletas se pierden o la gente toma pedidos ajenos"*), proveyendo una pantalla de comandas enumeradas secuencialmente (`#101`, `#102`...) con confirmación de entrega.
   - **Administrador**: Acceso exclusivo al panel de control con CRUD profesional (crear, editar y eliminar platos).
   - **Invitado**: Pedidos rápidos para usuarios no registrados.
2. **CRUD Profesional con Confirmación de Acciones**:
   - Creación, lectura, actualización y eliminación de platos del casino.
   - Diálogos modales interactivos para confirmar acciones críticas (eliminación de productos, confirmación de reservas de pedidos y confirmación/rechazo de comandas en caja).

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura y Módulos
- **`punto_casino/core/config.py`**: Branding institucional `PRONTO CASINO UCT`, ubicación `CASINO CENTRAL UCT` y categorías del PDF.
- **`punto_casino/models/product.py`**: Entidad `Product` con detalle de plato (`name`), ingredientes/acompañamiento (`ingredients`), precio (`price`), categoría (`category`) y stock.
- **`punto_casino/models/order.py`**: Entidad `Order` con número de comanda secuencial (`comanda_number`: int, e.g. `101`, `102`...).
- **`punto_casino/models/user.py`**: Entidad `User` con saldo universitario (`balance`: int) y rol (`UserRole`).
- **`punto_casino/services/auth_service.py`**: Manejo de sesión activa y cambio dinámico entre usuarios:
  - Estudiante Renato (Saldo: $15.000 CLP).
  - Cajero Cristian (Operador de cocina y caja).
  - Administrador (Gestor de inventario y menús).
  - Invitado (Público general).
- **`punto_casino/views/screens/admin_screen.py` (`AdminScreen`)**:
  - Panel administrativo con listado completo de productos.
  - Formulario modal para agregar y editar productos con validación.
  - Diálogo de confirmación antes de eliminar productos para evitar pérdida accidental de datos.
- **`punto_casino/views/screens/catalog_screen.py` (`CatalogScreen`)**:
  - Filtro por pestañas de categoría (*Todos*, *Normal*, *Ejecutivo*, *Hipocalórico*, *Vegetariano*, *Rápidas*, *Bebidas*).
  - Muestra el saldo disponible del estudiante en tiempo real.
  - Diálogo modal de confirmación antes de comprometer la reserva y descontar saldo.
- **`punto_casino/views/screens/cashier_screen.py` (`CashierScreen`)**:
  - Visualización prominente del número de comanda (`Comanda #101`) para entrega inequívoca en mesón.
  - Diálogos de confirmación para aprobar o rechazar pedidos.
- **`main.py`**: Barra superior unificada con selector de usuario/rol activo y barra de navegación responsive.

### 2.2 Ciclo de Vida de la Comanda Enumerada
```text
[Estudiante reserva pedido]
         │
         ▼
[OrderService genera Comanda #101]
         │
         ▼
[Cajero Cristian visualiza Comanda #101] ──► [Confirma en caja] ──► [Entrega al estudiante con Comanda #101]
```

---

## 3. Casos Borde y Manejo de Errores
- **Saldo Insuficiente**: Si el estudiante tiene saldo menor al total del carrito, el sistema le notifica y previene la transacción.
- **Confirmación Obligatoria**: Ninguna acción destructiva (eliminación de productos) o financiera (reserva) se ejecuta sin confirmación explícita del operador en el modal.
- **Validaciones en Formulario**: El CRUD valida que el precio y stock sean valores numéricos mayores a cero y que los campos requeridos no queden vacíos.

---

## 4. Pruebas y Verificación

### Comando de ejecución local
```bash
./kivy_env/bin/python main.py
```

### Checklist de Verificación Funcional
- [x] Selector de usuario en la barra superior alterna entre Estudiante, Cajero, Administrador e Invitado.
- [x] Filtro de categorías del PDF funciona en el catálogo de platos.
- [x] Diálogos de confirmación aparecen antes de reservar y antes de eliminar un producto.
- [x] Panel administrativo permite agregar, editar y eliminar platos.
- [x] Las comandas en caja se muestran con su número secuencial (`#101`, `#102`...).

